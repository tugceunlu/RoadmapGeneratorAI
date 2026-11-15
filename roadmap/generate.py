"""Turning retrieved course material into a week-by-week roadmap.

Small open models such as flan-t5 are poor at writing a long, structured plan in one
go, but good at short, focused tasks. So the roadmap is built in two steps:

1. Retrieval picks the most relevant, non-duplicate chunks of the learner's own
   course materials, one per week (retrieval-augmented generation).
2. For each week the model writes a short study task grounded in that chunk only.

Every week keeps a reference to the file it came from, so learners (and teachers)
can check where each recommendation comes from.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .ingest import Chunk, MaterialStore

MODEL = "google/flan-t5-base"


@dataclass
class WeekPlan:
    week: int
    focus: str
    task: str
    hours: int
    source: str


@dataclass
class Roadmap:
    goal: str
    interests: list[str]
    hours_per_week: int
    weeks: list[WeekPlan] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"## Your {len(self.weeks)}-week roadmap",
            f"**Goal:** {self.goal}  ",
            f"**Interests:** {', '.join(self.interests)}  ",
            f"**Time:** {self.hours_per_week} hours per week",
            "",
        ]
        for w in self.weeks:
            lines += [
                f"### Week {w.week}: {w.focus}",
                f"{w.task}",
                "",
                f"*About {w.hours} h · based on `{w.source}`*",
                "",
            ]
        return "\n".join(lines)


def first_sentence(text: str, limit: int = 90) -> str:
    """A short label for a chunk: its first heading-like line.

    The very first line of a file is often the document title ("Course Notes"),
    so if a chunk has a shorter heading on the next line, that one is used.
    """
    lines = [l.strip(" #*-") for l in text.strip().split("\n") if l.strip()]
    line = lines[0] if lines else ""
    if len(lines) > 1 and ":" in line and len(lines[1]) < 60:
        line = lines[1]
    sentence = line.split(". ")[0]
    return sentence if len(sentence) <= limit else sentence[: limit - 1].rstrip() + "…"


class RoadmapGenerator:
    def __init__(self, store: MaterialStore, model: str = MODEL):
        self.store = store
        self.model_name = model
        self._pipe = None

    @property
    def pipe(self):
        if self._pipe is None:  # load lazily: the model is ~1 GB
            from transformers import pipeline

            self._pipe = pipeline("text2text-generation", model=self.model_name)
        return self._pipe

    def pick_chunks(self, interests: list[str], goal: str, weeks: int, max_gap: float = 0.13) -> list[Chunk]:
        """The most relevant chunks, one per week.

        A chunk is skipped when it is much less relevant than the best match
        (``max_gap``), so unrelated material does not end up in the plan.
        """
        query = f"{goal}. Topics: {', '.join(interests)}"
        candidates = self.store.search(query, k=weeks * 4)
        if not candidates:
            return []
        best = candidates[0].distance
        picked: list[Chunk] = []
        for c in candidates:
            if c.distance > best + max_gap:
                break  # results are sorted, so everything after this is less relevant
            if any(p.source == c.source and p.index == c.index for p in picked):
                continue
            picked.append(c)
            if len(picked) == weeks:
                break
        # keep the course's own order within each file so the plan builds up logically
        return sorted(picked, key=lambda c: (c.source, c.index))

    def write_task(self, chunk: Chunk) -> str:
        """Ask the model what the learner should do to learn this chunk.

        flan-t5 follows short, summary-style instructions best; longer prompts
        made it repeat itself (see the prompt comparison in the README).
        """
        prompt = f"Summarize what a student should do to learn this: {chunk.text[:1200]}"
        out = self.pipe(
            prompt, max_new_tokens=70, do_sample=False, num_beams=4, no_repeat_ngram_size=3
        )[0]["generated_text"].strip()
        practice = out[0].upper() + out[1:] if out else "Work through the examples in this section."
        return f"Read this section of your materials, then: {practice}"

    def generate(self, interests: list[str], goal: str, hours_per_week: int, weeks: int = 5) -> Roadmap:
        roadmap = Roadmap(goal=goal, interests=interests, hours_per_week=hours_per_week)
        for i, chunk in enumerate(self.pick_chunks(interests, goal, weeks), start=1):
            roadmap.weeks.append(
                WeekPlan(
                    week=i,
                    focus=first_sentence(chunk.text),
                    task=self.write_task(chunk),
                    hours=hours_per_week,
                    source=chunk.source,
                )
            )
        return roadmap
