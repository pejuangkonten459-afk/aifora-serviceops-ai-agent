
import pytest

from app.rag.document_loader import load_documents
from app.rag.text_chunker import chunk_text


def test_load_documents_finds_sop():
    documents = load_documents()

    assert len(documents) >= 1
    assert any(
        document["source"] == "SOP-001-gangguan-jaringan.md"
        for document in documents
    )
    assert any(
        "Penanganan Gangguan Jaringan" in document["content"]
        for document in documents
    )


def test_chunk_text_splits_long_text():
    text = "A" * 1100

    chunks = chunk_text(text, chunk_size=500, overlap=100)

    assert len(chunks) == 3
    assert [len(chunk) for chunk in chunks] == [500, 500, 300]


def test_chunk_text_preserves_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunks = chunk_text(text, chunk_size=10, overlap=3)

    assert chunks == [
        "ABCDEFGHIJ",
        "HIJKLMNOPQ",
        "OPQRSTUVWX",
        "VWXYZ",
    ]


def test_chunk_text_returns_empty_list_for_blank_text():
    assert chunk_text("   ") == []


def test_chunk_text_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        chunk_text("teks", chunk_size=0)

    with pytest.raises(ValueError):
        chunk_text("teks", chunk_size=10, overlap=10)
