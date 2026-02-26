from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api", tags=["enrollment"])

@router.get("/worker_templates")
async def get_worker_templates(
    client_company_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get worker enrollment templates"""
    try:
        if client_company_id:
            query = text("""
                SELECT * FROM worker_templates
                WHERE client_company_id = :company_id
                ORDER BY created_at DESC
                LIMIT 1
            """)
            result = db.execute(query, {"company_id": client_company_id})
        else:
            query = text("SELECT * FROM worker_templates ORDER BY created_at DESC LIMIT 1")
            result = db.execute(query)
        
        row = result.fetchone()
        if row:
            columns = result.keys()
            data = dict(zip(columns, row))
            return {"data": data, "error": None}
        else:
            return {"data": None, "error": None}
    except Exception as e:
        return {"data": None, "error": None}  # Table might not exist

@router.get("/enrollment_invites")
async def get_enrollment_invite(
    worker_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get enrollment invitation for a worker"""
    try:
        if worker_id:
            query = text("""
                SELECT * FROM enrollment_invites
                WHERE worker_id = :worker_id
                ORDER BY created_at DESC
                LIMIT 1
            """)
            result = db.execute(query, {"worker_id": worker_id})
        else:
            query = text("SELECT * FROM enrollment_invites ORDER BY created_at DESC LIMIT 1")
            result = db.execute(query)
        
        row = result.fetchone()
        if row:
            columns = result.keys()
            data = dict(zip(columns, row))
            return {"data": data, "error": None}
        else:
            return {"data": None, "error": None}
    except Exception as e:
        return {"data": None, "error": None}

@router.get("/worker_sites")
async def get_worker_site_assignments(
    worker_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get site assignments for workers"""
    try:
        if worker_id:
            query = text("""
                SELECT * FROM worker_sites
                WHERE worker_id = :worker_id
                ORDER BY created_at DESC
            """)
            result = db.execute(query, {"worker_id": worker_id})
        else:
            query = text("SELECT * FROM worker_sites ORDER BY created_at DESC LIMIT 100")
            result = db.execute(query)
        
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": [], "error": None}

@router.post("/worker_sites")
async def create_site_assignments(
    assignments: list,
    db: Session = Depends(get_db)
):
    """Create multiple site assignments for a worker"""
    try:
        created = []
        
        for assignment in assignments:
            assignment_id = str(uuid.uuid4())
            query = text("""
                INSERT INTO worker_sites (
                    id, worker_id, site_id, created_at
                ) VALUES (
                    :id, :worker_id, :site_id, :created_at
                )
                RETURNING *
            """)
            
            result = db.execute(query, {
                "id": assignment_id,
                "worker_id": assignment.get("worker_id"),
                "site_id": assignment.get("site_id"),
                "created_at": datetime.utcnow()
            })
            
            row = result.fetchone()
            if row:
                columns = result.keys()
                created.append(dict(zip(columns, row)))
        
        db.commit()
        return {"data": created, "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}

@router.delete("/worker_sites")
async def delete_site_assignments(
    worker_id: str,
    site_ids: list,
    db: Session = Depends(get_db)
):
    """Delete site assignments for a worker"""
    try:
        placeholders = ','.join([f':site{i}' for i in range(len(site_ids))])
        params = {"worker_id": worker_id}
        params.update({f'site{i}': site_id for i, site_id in enumerate(site_ids)})
        
        query = text(f"""
            DELETE FROM worker_sites
            WHERE worker_id = :worker_id AND site_id IN ({placeholders})
            RETURNING id
        """)
        
        result = db.execute(query, params)
        db.commit()
        
        deleted_count = len(result.fetchall())
        
        return {"data": deleted_count, "error": None}
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
