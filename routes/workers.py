from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import Optional
import uuid
from datetime import datetime

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
            query = text("SELECT * FROM workers ORDER BY created_at DESC LIMIT 100")
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
        worker_id = worker_data.get('id') or str(uuid.uuid4())
        
        query = text("""
            INSERT INTO workers (
                id, first_name, last_name, email, phone, employee_id,
                client_company_id, status, created_at, updated_at
            ) VALUES (
                :id, :first_name, :last_name, :email, :phone, :employee_id,
                :client_company_id, :status, :created_at, :updated_at
            )
            RETURNING *
        """)
        
        params = {
            'id': worker_id,
            'first_name': worker_data.get('first_name', ''),
            'last_name': worker_data.get('last_name', ''),
            'email': worker_data.get('email'),
            'phone': worker_data.get('phone'),
            'employee_id': worker_data.get('employee_id'),
            'client_company_id': worker_data.get('client_company_id'),
            'status': worker_data.get('status', 'active'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.execute(query, params)
        db.commit()
        
        row = result.fetchone()
        columns = result.keys()
        data = dict(zip(columns, row))
        
        return {"data": data, "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}

@router.put("/{worker_id}")
async def update_worker(worker_id: str, updates: dict, db: Session = Depends(get_db)):
    """Update a worker"""
    try:
        update_fields = []
        params = {'id': worker_id, 'updated_at': datetime.utcnow()}
        
        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'employee_id', 'status']
        
        for field in allowed_fields:
            if field in updates:
                update_fields.append(f"{field} = :{field}")
                params[field] = updates[field]
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        update_fields.append("updated_at = :updated_at")
        
        query = text(f"""
            UPDATE workers SET {', '.join(update_fields)}
            WHERE id = :id RETURNING *
        """)
        
        result = db.execute(query, params)
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        columns = result.keys()
        data = dict(zip(columns, row))
        
        return {"data": data, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}

@router.delete("/{worker_id}")
async def delete_worker(worker_id: str, db: Session = Depends(get_db)):
    """Delete a worker"""
    try:
        query = text("DELETE FROM workers WHERE id = :id RETURNING id")
        result = db.execute(query, {"id": worker_id})
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        return {"data": True, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
