
import chromadb
import pytest

from app.rag.vector_store import index_documents, search_documents


@pytest.fixture
def test_collection():
    client = chromadb.Client()
    collection = client.create_collection(
        name="test_serviceops_sop",
        metadata={"hnsw:space": "cosine"},
    )

    yield collection

    client.delete_collection("test_serviceops_sop")


def test_index_documents_stores_chunks(test_collection):
    count = index_documents(collection=test_collection)

    assert count == test_collection.count()
    assert count >= 1


def test_search_documents_finds_network_sop(test_collection):
    index_documents(collection=test_collection)

    results = search_documents(
        "Apa yang harus dilakukan ketika koneksi internet terputus?",
        collection=test_collection,
    )

    assert len(results) >= 1
    assert results[0]["source"] == "SOP-001-gangguan-jaringan.md"
    assert any(
        "Langkah pemeriksaan" in result["content"]
        or "Koneksi internet terputus" in result["content"]
        for result in results
    )


def test_search_documents_rejects_empty_query(test_collection):
    with pytest.raises(ValueError, match="query must not be empty"):
        search_documents("   ", collection=test_collection)


def test_search_documents_rejects_invalid_result_count(test_collection):
    with pytest.raises(ValueError, match="n_results must be greater than 0"):
        search_documents("gangguan jaringan", n_results=0, collection=test_collection)


def test_search_documents_returns_empty_for_empty_collection(test_collection):
    results = search_documents("gangguan jaringan", collection=test_collection)

    assert results == []
