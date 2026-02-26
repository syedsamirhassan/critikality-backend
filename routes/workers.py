from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional

router = APIRouter(prefix="/api/workers", tags=["workers"])

@router.get("/")
async def get_workers(
    client_company_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all workers, optionally filtered by company"""
    query = "SELECT * FROM workers"
    params = []
    
    if client_company_id:
        query += " WHERE client_company_id = %s"
        params.append(client_company_id)
    
    query += " ORDER BY created_at DESC"
    
    result = db.execute(query, params)
    return {"data": result.fetchall(), "error": None}

@router.get("/{worker_id}")
async def get_worker_by_id(worker_id: str, db: Session = Depends(get_db)):
    """Get a single worker by ID"""
    query = "SELECT * FROM workers WHERE id = %s"
    result = db.execute(query, [worker_id])
    data = result.fetchone()
    
    if not data:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return {"data": data, "error": None}

@router.post("/")
async def create_worker(worker_data: dict, db: Session = Depends(get_db)):
    """Create a new worker"""
    # Implementation will insert into workers table
    return {"data": worker_data, "error": None}

@router.put("/{worker_id}")
async def update_worker(
    worker_id: str,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update a worker"""
    return {"data": updates, "error": None}

@router.delete("/{worker_id}")
async def delete_worker(worker_id: str, db: Session = Depends(get_db)):
    """Delete a worker"""
    return {"data": True, "error": None}
