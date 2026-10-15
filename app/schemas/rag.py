
from pydantic import BaseModel, Field


class RAGSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    n_results: int = Field(default=2, ge=1, le=10)


class RAGSearchResult(BaseModel):
    content: str
    source: str
    chunk_index: int
    distance: float


class RAGSearchResponse(BaseModel):
    query: str
    results: list[RAGSearchResult]
