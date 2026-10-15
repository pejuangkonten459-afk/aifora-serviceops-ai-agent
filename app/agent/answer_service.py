
import re

from app.rag.vector_store import search_documents


MAX_DISTANCE = 0.55


STOPWORDS = {
    "apa", "yang", "harus", "dilakukan", "ketika",
    "bagaimana", "cara", "untuk", "dan", "atau",
    "pada", "dengan", "saya", "mengajukan",
    "prosedur", "panduan", "informasi", "dokumen",
    "tersedia", "tercantum", "ditemukan", "standar",
    "berdasarkan", "gunakan", "dalam", "tidak",
    "ada", "belum", "cukup", "relevan",
}



def extract_keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {
        word
        for word in words
        if len(word) > 2 and word not in STOPWORDS
    }


def build_answer(query: str, n_results: int = 2) -> dict:
    query = query.strip()

    if len(query) < 3:
        raise ValueError(
            "Query must contain at least 3 non-whitespace characters."
        )

    results = search_documents(query=query, n_results=n_results)

    relevant_results = [
        result
        for result in results
        if result.get("distance", 1.0) <= MAX_DISTANCE
    ]

    query_keywords = extract_keywords(query)
    document_text = " ".join(
        result["content"] for result in relevant_results
    )
    matched_keywords = query_keywords & extract_keywords(document_text)

    if not relevant_results or not matched_keywords:
        return {
            "query": query,
            "answer": (
                "Belum ditemukan informasi SOP yang cukup relevan. "
                "Periksa dokumen yang tersedia atau eskalasikan kepada "
                "tim yang berwenang."
            ),
            "sources": [],
            "method": "extractive_rag",
        }

    content = "\n\n".join(
        result["content"].strip()
        for result in relevant_results
        if result["content"].strip()
    )

    answer = (
        "Panduan berdasarkan SOP:\n\n"
        f"{content}\n\n"
        "Gunakan prosedur dan batas kewenangan yang tercantum dalam SOP."
    )

    return {
        "query": query,
        "answer": answer,
        "sources": sorted(
            {result["source"] for result in relevant_results}
        ),
        "method": "extractive_rag",
    }
