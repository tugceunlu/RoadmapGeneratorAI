"""Reading course materials and storing them in a vector database."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION = "course_materials"


@dataclass
class Chunk:
    text: str
    source: str
    index: int
    distance: float = 0.0  # cosine distance to the query (lower = more relevant)


def read_text(name: str, data: bytes) -> str:
    """Return the plain text of a .txt or .pdf file given as bytes."""
    suffix = Path(name).suffix.lower()
    if suffix == ".txt":
        for encoding in ("utf-8", "cp1254", "latin-1"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not decode {name}")
    if suffix == ".pdf":
        from io import BytesIO

        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"Unsupported file type: {name} (use .txt or .pdf)")


def split(text: str, source: str, chunk_size: int = 450, overlap: int = 50) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return [Chunk(t.strip(), source, i) for i, t in enumerate(splitter.split_text(text)) if t.strip()]


class MaterialStore:
    """A persistent ChromaDB collection of course-material chunks."""

    def __init__(self, path: str | None = "data/chroma"):
        self.client = chromadb.PersistentClient(path=path) if path else chromadb.EphemeralClient()
        self.embed = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        self.collection = self.client.get_or_create_collection(
            COLLECTION, embedding_function=self.embed, metadata={"hnsw:space": "cosine"}
        )

    # ---- adding material -------------------------------------------------
    def add_file(self, name: str, data: bytes) -> int:
        """Add one file. Re-adding the same file replaces it. Returns the number of chunks."""
        chunks = split(read_text(name, data), source=name)
        self.collection.delete(where={"source": name})
        if not chunks:
            return 0
        self.collection.add(
            ids=[self._id(c) for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[{"source": c.source, "index": c.index} for c in chunks],
        )
        return len(chunks)

    def add_folder(self, folder: str | Path) -> int:
        total = 0
        for path in sorted(Path(folder).glob("*")):
            if path.suffix.lower() in {".txt", ".pdf"}:
                total += self.add_file(path.name, path.read_bytes())
        return total

    def add_uploads(self, files: Iterable[BinaryIO]) -> int:
        return sum(self.add_file(f.name, f.read()) for f in files)

    # ---- inspecting / searching ------------------------------------------
    def sources(self) -> list[str]:
        metas = self.collection.get(include=["metadatas"])["metadatas"] or []
        return sorted({m["source"] for m in metas})

    def count(self) -> int:
        return self.collection.count()

    def search(self, query: str, k: int = 5) -> list[Chunk]:
        if self.count() == 0:
            return []
        res = self.collection.query(query_texts=[query], n_results=min(k, self.count()))
        return [
            Chunk(doc, meta["source"], meta["index"], dist)
            for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
        ]

    def clear(self) -> None:
        self.client.delete_collection(COLLECTION)
        self.collection = self.client.get_or_create_collection(
            COLLECTION, embedding_function=self.embed, metadata={"hnsw:space": "cosine"}
        )

    @staticmethod
    def _id(chunk: Chunk) -> str:
        return hashlib.sha1(f"{chunk.source}:{chunk.index}".encode()).hexdigest()
