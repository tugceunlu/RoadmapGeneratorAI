"""Fast tests: ingestion, retrieval and roadmap assembly (the language model is stubbed)."""

from pathlib import Path

from roadmap import MaterialStore, RoadmapGenerator
from roadmap.ingest import read_text, split

SAMPLES = Path(__file__).parent.parent / "sample_materials"


def make_store() -> MaterialStore:
    store = MaterialStore(path=None)  # in-memory
    store.clear()
    store.add_folder(SAMPLES)
    return store


def test_read_and_split():
    text = read_text("notes.txt", ("Hello world. " * 200).encode())
    chunks = split(text, "notes.txt")
    assert len(chunks) > 1 and all(c.source == "notes.txt" for c in chunks)


def test_readding_a_file_replaces_it():
    store = make_store()
    before = store.count()
    store.add_folder(SAMPLES)
    assert store.count() == before
    assert len(store.sources()) == 3


def test_search_finds_relevant_material():
    store = make_store()
    hits = store.search("cleaning missing values in a dataset", k=2)
    assert hits[0].source == "data_analysis_basics.txt"


def test_generate_builds_one_week_per_chunk_with_sources():
    store = make_store()
    gen = RoadmapGenerator(store)
    gen._pipe = lambda prompt, **kw: [{"generated_text": "practise the examples from the notes"}]
    roadmap = gen.generate(["Data analysis"], "analyse a small dataset", hours_per_week=4, weeks=3)
    assert [w.week for w in roadmap.weeks] == [1, 2, 3]
    assert all(w.source.endswith(".txt") and "practise the examples" in w.task.lower() for w in roadmap.weeks)
    assert "Week 1" in roadmap.to_markdown()
