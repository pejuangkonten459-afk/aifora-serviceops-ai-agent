
from app.agent.answer_service import build_answer


def test_build_answer_rejects_unrelated_question(monkeypatch):
    def fake_search_documents(query: str, n_results: int = 2):
        return [
            {
                "content": (
                    "# SOP-001: Penanganan Gangguan Jaringan\n\n"
                    "## Langkah pemeriksaan\n"
                    "Periksa kabel jaringan dan koneksi Wi-Fi."
                ),
                "source": "SOP-001-gangguan-jaringan.md",
                "chunk_index": 0,
                "distance": 0.4841,
            }
        ]

    monkeypatch.setattr(
        "app.agent.answer_service.search_documents",
        fake_search_documents,
    )

    result = build_answer("Bagaimana cara mengajukan cuti tahunan?")

    assert result["sources"] == []
    assert "Belum ditemukan" in result["answer"]


def test_build_answer_accepts_relevant_question(monkeypatch):
    def fake_search_documents(query: str, n_results: int = 2):
        return [
            {
                "content": (
                    "## Langkah pemeriksaan\n"
                    "Pastikan kabel jaringan atau koneksi Wi-Fi tersambung."
                ),
                "source": "SOP-001-gangguan-jaringan.md",
                "chunk_index": 1,
                "distance": 0.3644,
            }
        ]

    monkeypatch.setattr(
        "app.agent.answer_service.search_documents",
        fake_search_documents,
    )

    result = build_answer(
        "Apa yang harus dilakukan ketika koneksi internet terputus?"
    )

    assert result["sources"] == ["SOP-001-gangguan-jaringan.md"]
    assert "koneksi Wi-Fi" in result["answer"]
