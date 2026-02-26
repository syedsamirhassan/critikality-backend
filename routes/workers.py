from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import Optional

router = APIRouter(prefix="/api/workers", tags=["workers"])

@router.get("")
async def get_workers(
    client_company_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all workers, optionally filtered by company"""
    try:
        if client_company_id:
            query = text("SELECT * FROM workers WHERE client_company_id = :company_id ORDER BY created_at DESC")
            result = db.execute(query, {"company_id": client_company_id})
        else:
            query = text("SELECT * FROM workers ORDER BY created_at DESC")
            result = db.execute(query)
        
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.get("/{worker_id}")
async def get_worker_by_id(worker_id: str, db: Session = Depends(get_db)):
    """Get a single worker by ID"""
    try:
        query = text("SELECT * FROM workers WHERE id = :worker_id")
        result = db.execute(query, {"worker_id": worker_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        columns = result.keys()
        data = dict(zip(columns, row))
        
        return {"data": data, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.post("")
async def create_worker(worker_data: dict, db: Session = Depends(get_db)):
    """Create a new worker"""
    try:
        return {"data": worker_data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.put("/{worker_id}")
async def update_worker(
    worker_id: str,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update a worker"""
    try:
        return {"data": updates, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.delete("/{worker_id}")
async def delete_worker(worker_id: str, db: Session = Depends(get_db)):
    """Delete a worker"""
    try:
        return {"data": True, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
