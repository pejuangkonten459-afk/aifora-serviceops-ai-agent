
from pathlib import Path

DOCUMENTS_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "documents"
)


def load_documents() -> list[dict[str, str]]:
    """Load Markdown documents from the documents directory."""
    documents = []

    for file_path in sorted(DOCUMENTS_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8-sig").strip()
        if not content:
            continue

        documents.append(
            {
                "source": file_path.name,
                "content": content,
            }
        )

    return documents
