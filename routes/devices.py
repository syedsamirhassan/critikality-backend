from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/devices", tags=["devices"])

@router.get("")
async def get_devices(db: Session = Depends(get_db)):
    """Get all devices"""
    try:
        query = text("SELECT * FROM devices ORDER BY created_at DESC LIMIT 100")
        result = db.execute(query)
        
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.get("/{device_id}")
async def get_device_by_id(device_id: str, db: Session = Depends(get_db)):
    """Get a single device by ID"""
    try:
        query = text("SELECT * FROM devices WHERE id = :device_id")
        result = db.execute(query, {"device_id": device_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")
        
        columns = result.keys()
        data = dict(zip(columns, row))
        
        return {"data": data, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.post("")
async def create_device(device_data: dict, db: Session = Depends(get_db)):
    """Create a new device"""
    try:
        device_id = device_data.get('id') or str(uuid.uuid4())
        
        query = text("""
            INSERT INTO devices (
                id, name, device_type, ip_address, port, location,
                status, created_at, updated_at
            ) VALUES (
                :id, :name, :device_type, :ip_address, :port, :location,
                :status, :created_at, :updated_at
            )
            RETURNING *
        """)
        
        params = {
            'id': device_id,
            'name': device_data.get('name', ''),
            'device_type': device_data.get('device_type', 'camera'),
            'ip_address': device_data.get('ip_address'),
            'port': device_data.get('port', 80),
            'location': device_data.get('location'),
            'status': device_data.get('status', 'active'),
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

@router.put("/{device_id}")
async def update_device(device_id: str, updates: dict, db: Session = Depends(get_db)):
    """Update a device"""
    try:
        update_fields = []
        params = {'id': device_id, 'updated_at': datetime.utcnow()}
        
        allowed_fields = ['name', 'device_type', 'ip_address', 'port', 'location', 'status']
        
        for field in allowed_fields:
            if field in updates:
                update_fields.append(f"{field} = :{field}")
                params[field] = updates[field]
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        update_fields.append("updated_at = :updated_at")
        
        query = text(f"""
            UPDATE devices SET {', '.join(update_fields)}
            WHERE id = :id RETURNING *
        """)
        
        result = db.execute(query, params)
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")
        
        columns = result.keys()
        data = dict(zip(columns, row))
        
        return {"data": data, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}

@router.delete("/{device_id}")
async def delete_device(device_id: str, db: Session = Depends(get_db)):
    """Delete a device"""
    try:
        query = text("DELETE FROM devices WHERE id = :id RETURNING id")
        result = db.execute(query, {"id": device_id})
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return {"data": True, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
