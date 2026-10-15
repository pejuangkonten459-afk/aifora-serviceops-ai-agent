
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from app.rag.document_loader import load_documents
from app.rag.text_chunker import chunk_text


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

COLLECTION_NAME = "serviceops_sop"


def get_collection():
    """Return a persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def index_documents(collection=None) -> int:
    """Index SOP chunks and return the collection item count."""
    if collection is None:
        collection = get_collection()

    documents = load_documents()

    for document in documents:
        chunks = chunk_text(document["content"])

        if not chunks:
            continue

        ids = [
            f"{document['source']}:{index}"
            for index in range(len(chunks))
        ]

        collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=[
                {
                    "source": document["source"],
                    "chunk_index": index,
                }
                for index in range(len(chunks))
            ],
        )

    return collection.count()


def search_documents(
    query: str,
    n_results: int = 2,
    collection=None,
) -> list[dict]:
    """Search SOP chunks relevant to a query."""
    query = query.strip()

    if not query:
        raise ValueError("query must not be empty")

    if n_results <= 0:
        raise ValueError("n_results must be greater than 0")

    if collection is None:
        collection = get_collection()

    total = collection.count()

    if total == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, total),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for index, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][index]

        matches.append(
            {
                "content": document,
                "source": metadata["source"],
                "chunk_index": metadata["chunk_index"],
                "distance": results["distances"][0][index],
            }
        )

    return matches
