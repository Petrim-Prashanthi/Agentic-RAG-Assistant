import sys
from pathlib import Path
import chromadb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(ROOT / "chroma_db")
DOCS_DIR = ROOT / "data" / "docs"


def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(
        "knowledge_base", metadata={"hnsw:space": "cosine"}
    )


def chunk_text(text: str, size: int = 200, overlap: int = 40):
    words = text.split()
    step = size - overlap
    chunks = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + size])
        if chunk:
            chunks.append(chunk)
    return chunks


def ingest(reset: bool = False):
    if reset:
        chromadb.PersistentClient(path=DB_PATH).delete_collection("knowledge_base")
    col = get_collection()
    ids, docs, metas = [], [], []
    for path in DOCS_DIR.glob("**/*"):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        for i, chunk in enumerate(chunk_text(text)):
            ids.append(f"{path.stem}-{i}")
            docs.append(chunk)
            metas.append({"source": path.name, "chunk": i})
    if ids:
        col.upsert(ids=ids, documents=docs, metadatas=metas)
    print(f"Ingested {len(ids)} chunks from {DOCS_DIR}")


if __name__ == "__main__":
    ingest(reset="--reset" in sys.argv)
