from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/zones", tags=["zones"])

@router.get("")
async def get_zones(
    zone_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all zones, optionally filtered by type"""
    try:
        if zone_type:
            query = text("SELECT * FROM location_zones WHERE zone_type = :zone_type ORDER BY created_at DESC")
            result = db.execute(query, {"zone_type": zone_type})
        else:
            query = text("SELECT * FROM location_zones ORDER BY created_at DESC LIMIT 100")
            result = db.execute(query)
        
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.get("/{zone_id}")
async def get_zone_by_id(zone_id: str, db: Session = Depends(get_db)):
    """Get a single zone by ID"""
    try:
        query = text("SELECT * FROM location_zones WHERE id = :zone_id")
        result = db.execute(query, {"zone_id": zone_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Zone not found")
        
        columns = result.keys()
        data = dict(zip(columns, row))
        
        return {"data": data, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.post("")
async def create_zone(zone_data: dict, db: Session = Depends(get_db)):
    """Create a new zone"""
    try:
        zone_id = zone_data.get('id') or str(uuid.uuid4())
        
        query = text("""
            INSERT INTO location_zones (
                id, name, zone_type, description, capacity,
                status, created_at, updated_at
            ) VALUES (
                :id, :name, :zone_type, :description, :capacity,
                :status, :created_at, :updated_at
            )
            RETURNING *
        """)
        
        params = {
            'id': zone_id,
            'name': zone_data.get('name', ''),
            'zone_type': zone_data.get('zone_type', 'general'),
            'description': zone_data.get('description'),
            'capacity': zone_data.get('capacity'),
            'status': zone_data.get('status', 'active'),
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

@router.put("/{zone_id}")
async def update_zone(zone_id: str, updates: dict, db: Session = Depends(get_db)):
    """Update a zone"""
    try:
        update_fields = []
        params = {'id': zone_id, 'updated_at': datetime.utcnow()}
        
        allowed_fields = ['name', 'zone_type', 'description', 'capacity', 'status']
        
        for field in allowed_fields:
            if field in updates:
                update_fields.append(f"{field} = :{field}")
                params[field] = updates[field]
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        update_fields.append("updated_at = :updated_at")
        
        query = text(f"""
            UPDATE location_zones SET {', '.join(update_fields)}
            WHERE id = :id RETURNING *
        """)
        
        result = db.execute(query, params)
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Zone not found")
        
        columns = result.keys()
        data = dict(zip(columns, row))
        
        return {"data": data, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}

@router.delete("/{zone_id}")
async def delete_zone(zone_id: str, db: Session = Depends(get_db)):
    """Delete a zone"""
    try:
        query = text("DELETE FROM location_zones WHERE id = :id RETURNING id")
        result = db.execute(query, {"id": zone_id})
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Zone not found")
        
        return {"data": True, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
