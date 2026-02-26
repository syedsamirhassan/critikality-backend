from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/api", tags=["enrollment"])

@router.get("/worker_templates")
async def get_worker_templates(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """Get worker templates"""
    return {"data": None, "error": None}

@router.get("/enrollment_invites")
async def get_enrollment_invite(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """Get enrollment invite"""
    return {"data": None, "error": None}

@router.get("/worker_sites")
async def get_worker_site_assignments(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """Get worker site assignments"""
    return {"data": [], "error": None}

@router.post("/worker_sites")
async def create_site_assignments(
    assignments: list,
    db: Session = Depends(get_db)
):
    """Create site assignments"""
    return {"data": True, "error": None}

@router.delete("/worker_sites")
async def delete_site_assignments(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """Delete site assignments"""
    return {"data": True, "error": None}
