from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.post("/rpc/get_worker_last_seen")
async def get_worker_last_seen(request_body: dict, db: Session = Depends(get_db)):
    """Get last seen timestamp for workers"""
    try:
        worker_ids = request_body.get('worker_ids', [])
        
        if not worker_ids:
            return {"data": [], "error": None}
        
        # Create placeholders for the IN clause
        placeholders = ','.join([f':id{i}' for i in range(len(worker_ids))])
        params = {f'id{i}': worker_id for i, worker_id in enumerate(worker_ids)}
        
        query = text(f"""
            SELECT 
                w.id as worker_id,
                w.first_name,
                w.last_name,
                MAX(se.created_at) as last_seen
            FROM workers w
            LEFT JOIN scan_events se ON w.id = se.worker_id
            WHERE w.id IN ({placeholders})
            GROUP BY w.id, w.first_name, w.last_name
        """)
        
        result = db.execute(query, params)
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        # Get worker counts
        worker_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_workers,
                COUNT(*) FILTER (WHERE status = 'active') as active_workers,
                COUNT(*) FILTER (WHERE status = 'inactive') as inactive_workers
            FROM workers
        """)).fetchone()
        
        # Get device counts
        device_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_devices,
                COUNT(*) FILTER (WHERE status = 'active') as active_devices
            FROM devices
        """)).fetchone()
        
        # Get zone counts
        zone_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_zones,
                COUNT(*) FILTER (WHERE zone_type = 'confined_space') as confined_spaces,
                COUNT(*) FILTER (WHERE zone_type = 'hazard_zone') as hazard_zones
            FROM location_zones
        """)).fetchone()
        
        # Get emergency events
        emergency_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_emergencies,
                COUNT(*) FILTER (WHERE status = 'active') as active_emergencies
            FROM emergency_events
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)).fetchone()
        
        stats = {
            "workers": dict(zip(worker_stats.keys(), worker_stats)) if worker_stats else {},
            "devices": dict(zip(device_stats.keys(), device_stats)) if device_stats else {},
            "zones": dict(zip(zone_stats.keys(), zone_stats)) if zone_stats else {},
            "emergencies": dict(zip(emergency_stats.keys(), emergency_stats)) if emergency_stats else {}
        }
        
        return {"data": stats, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
