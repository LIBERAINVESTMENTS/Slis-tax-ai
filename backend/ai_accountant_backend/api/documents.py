"""Document endpoints (stub)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["documents"])


@router.get("/documents")
def list_documents():
    return {"documents": [], "note": "Document management implemented in next increment"}
