from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.post("/rpc/get_worker_last_seen")
async def get_worker_last_seen(db: Session = Depends(get_db)):
    """Get worker last seen data (RPC endpoint)"""
    return {"data": [], "error": None}

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    companyId: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    return {"data": {
        "workerLastSeen": [],
        "workers": [],
        "zones": [],
        "devices": [],
        "movement": [],
        "scanEvents": [],
        "emergencies": []
    }, "error": None}
