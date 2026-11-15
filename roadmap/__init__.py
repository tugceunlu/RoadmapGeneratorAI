"""RoadmapGeneratorAI: turn course materials into a personalised, week-by-week study plan.

* ``ingest``   reads PDF/TXT files, splits them into chunks and stores them in ChromaDB,
               then finds the chunks that match a learner's interests and goal
* ``generate`` writes one grounded study task per week with a local language model
"""

from .ingest import MaterialStore
from .generate import RoadmapGenerator, Roadmap, WeekPlan

__all__ = ["MaterialStore", "RoadmapGenerator", "Roadmap", "WeekPlan"]
