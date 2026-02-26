from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import Optional

router = APIRouter(prefix="/api", tags=["team"])

@router.get("/user_roles")
async def get_team_members(
    client_company_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get team members with their roles"""
    try:
        if client_company_id:
            query = text("""
                SELECT ur.*, up.email, up.full_name
                FROM user_roles ur
                LEFT JOIN user_profiles up ON ur.user_id = up.id
                WHERE ur.client_company_id = :company_id
                ORDER BY ur.created_at DESC
            """)
            result = db.execute(query, {"company_id": client_company_id})
        else:
            query = text("""
                SELECT ur.*, up.email, up.full_name
                FROM user_roles ur
                LEFT JOIN user_profiles up ON ur.user_id = up.id
                ORDER BY ur.created_at DESC
                LIMIT 100
            """)
            result = db.execute(query)
        
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.get("/team_invites")
async def get_pending_invites(db: Session = Depends(get_db)):
    """Get pending team invitations"""
    try:
        query = text("""
            SELECT * FROM team_invites
            WHERE status = 'pending'
            ORDER BY created_at DESC
        """)
        result = db.execute(query)
        
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": [], "error": None}  # Table might not exist

@router.delete("/user_roles")
async def remove_team_member(
    user_id: str,
    client_company_id: str,
    db: Session = Depends(get_db)
):
    """Remove a team member"""
    try:
        query = text("""
            DELETE FROM user_roles 
            WHERE user_id = :user_id AND client_company_id = :company_id
            RETURNING user_id
        """)
        result = db.execute(query, {"user_id": user_id, "company_id": client_company_id})
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Team member not found")
        
        return {"data": True, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}

@router.delete("/team_invites")
async def delete_invite(
    invite_id: str,
    db: Session = Depends(get_db)
):
    """Delete a team invitation"""
    try:
        query = text("DELETE FROM team_invites WHERE id = :id RETURNING id")
        result = db.execute(query, {"id": invite_id})
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Invite not found")
        
        return {"data": True, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}

@router.patch("/user_roles")
async def update_member_role(
    user_id: str,
    client_company_id: str,
    role: str,
    db: Session = Depends(get_db)
):
    """Update a team member's role"""
    try:
        query = text("""
            UPDATE user_roles 
            SET role = :role, updated_at = NOW()
            WHERE user_id = :user_id AND client_company_id = :company_id
            RETURNING *
        """)
        result = db.execute(query, {
            "role": role,
            "user_id": user_id,
            "company_id": client_company_id
        })
        db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Team member not found")
        
        columns = result.keys()
        data = dict(zip(columns, row))
        
        return {"data": data, "error": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {"data": None, "error": str(e)}
