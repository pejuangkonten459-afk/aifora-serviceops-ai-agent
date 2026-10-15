
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import DateTime, Integer, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column
from pathlib import Path
from fastapi.responses import FileResponse

from app.services.classifier import classify_request
from app.database.base import Base
from app.database.models import OperationalRequest
from app.database.session import engine, get_db
from app.schemas.requests import RequestCreate, RequestResponse
from app.rag.vector_store import search_documents
from app.agent.answer_service import build_answer
from app.schemas.rag import (
    RAGSearchRequest,
    RAGSearchResponse,
)


PROJECT_CODE = "01.AIFORA.10.26"

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AIFORA ServiceOps AI Agent",
    description="Operational request API - AIFORA AI ENGINEERING",
    version="1.0.0",
    lifespan=lifespan,
)




@app.get("/")
def root():
    return {
        "project_code": PROJECT_CODE,
        "product": "ServiceOps AI Agent",
        "organization": "AIFORA AI ENGINEERING",
        "status": "running",
    }

@app.get("/dashboard")
def dashboard():
    dashboard_file = (
        Path(__file__).resolve().parent.parent
        / "dashboard"
        / "index.html"
    )
    return FileResponse(dashboard_file, media_type="text/html")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project_code": PROJECT_CODE,
    }


@app.post(
    "/requests",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request(
    payload: RequestCreate,
    db: Session = Depends(get_db),
):
    title = payload.title.strip()
    description = payload.description.strip()

    if len(title) < 3 or len(description) < 5:
        raise HTTPException(
            status_code=422,
            detail="Title or description is too short.",
        )

    classification = classify_request(title, description)

    request_record = OperationalRequest(
        title=title,
        description=description,
        category=classification["category"],
        priority=classification["priority"],
    )

    try:
        db.add(request_record)
        db.flush()

        from app.database.audit import AuditLog

        audit_record = AuditLog(
            request_id=request_record.id,
            action="request.created",
            details=(
                f"category={classification['category']}; "
                f"priority={classification['priority']}; "
                f"method={classification['method']}"
            ),
        )
        db.add(audit_record)
        db.commit()
        db.refresh(request_record)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save request and audit log.",
        )

    return request_record


@app.get("/requests", response_model=list[RequestResponse])
def list_requests(db: Session = Depends(get_db)):
    statement = select(OperationalRequest).order_by(
        OperationalRequest.id.desc()
    )
    return db.scalars(statement).all()


@app.get(
    "/requests/{request_id}",
    response_model=RequestResponse,
)
def get_request(request_id: int, db: Session = Depends(get_db)):
    request_record = db.get(OperationalRequest, request_id)

    if request_record is None:
        raise HTTPException(
            status_code=404,
            detail="Request not found.",
        )

    return request_record


@app.get("/audit-logs")
def list_audit_logs(db: Session = Depends(get_db)):
    from app.database.audit import AuditLog

    statement = select(AuditLog).order_by(AuditLog.id.desc())
    audit_records = db.scalars(statement).all()

    return [
        {
            "id": record.id,
            "request_id": record.request_id,
            "action": record.action,
            "details": record.details,
            "created_at": record.created_at,
        }
        for record in audit_records
    ]

@app.post("/rag/search", response_model=RAGSearchResponse)
def rag_search(payload: RAGSearchRequest):
    query = payload.query.strip()

    if len(query) < 3:
        raise HTTPException(
            status_code=422,
            detail="Query must contain at least 3 non-whitespace characters.",
        )

    try:
        results = search_documents(
            query=query,
            n_results=payload.n_results,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="RAG search failed.",
        ) from exc

    return {
        "query": query,
        "results": results,
    }

@app.post("/rag/answer")
def rag_answer(payload: RAGSearchRequest):
    query = payload.query.strip()

    if len(query) < 3:
        raise HTTPException(
            status_code=422,
            detail="Query must contain at least 3 non-whitespace characters.",
        )

    try:
        return build_answer(
            query=query,
            n_results=payload.n_results,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="RAG answer generation failed.",
        ) from exc

