from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
import json
import os
import sys

# Import license generator
sys.path.append(os.path.dirname(__file__) + '/..')
from generate_license import LicenseGenerator

router = APIRouter(prefix="/api/licenses", tags=["licenses"])

class LicenseRequest(BaseModel):
    customer_name: str
    site_id: str
    jetson_serial: str
    max_cameras: int = 4
    duration_months: int = 12
    features: List[str] = ["face_recognition", "liveness", "reports"]

# Initialize generator
generator = LicenseGenerator()
try:
    generator.load_private_key()
except:
    print("⚠️  Warning: private_key.pem not found. License generation will fail.")

@router.post("/generate")
async def generate_license(request: LicenseRequest):
    """Generate a new license file"""
    try:
        # Create license
        filename = generator.create_license(
            customer=request.customer_name,
            site_id=request.site_id,
            jetson_serial=request.jetson_serial,
            duration_months=request.duration_months,
            max_cameras=request.max_cameras,
            features=request.features
        )
        
        # Read the generated license
        with open(filename, 'r') as f:
            license_data = json.load(f)
        
        return {
            "success": True,
            "message": "License generated successfully",
            "license": license_data,
            "filename": filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate license: {str(e)}")

@router.get("/download/{site_id}")
async def download_license(site_id: str):
    """Download a generated license file"""
    filename = f"{site_id}.lic"
    
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="License file not found")
    
    return FileResponse(
        path=filename,
        filename=filename,
        media_type="application/json"
    )

@router.get("/list")
async def list_licenses():
    """List all generated licenses"""
    licenses = []
    
    for filename in os.listdir('.'):
        if filename.endswith('.lic'):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    data.pop('signature', None)
                    data['filename'] = filename
                    licenses.append(data)
            except:
                continue
    
    return {
        "licenses": sorted(licenses, key=lambda x: x.get('issued_date', ''), reverse=True)
    }

@router.delete("/{site_id}")
async def delete_license(site_id: str):
    """Delete a license file"""
    filename = f"{site_id}.lic"
    
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="License file not found")
    
    os.remove(filename)
    
    return {
        "success": True,
        "message": f"License {site_id} deleted"
    }
