from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import all route modules
from routes import workers, devices, zones, dashboard, team, enrollment

load_dotenv()

app = FastAPI(title="Critikality API", version="1.0.0")

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(workers.router)
app.include_router(devices.router)
app.include_router(zones.router)
app.include_router(dashboard.router)
app.include_router(team.router)
app.include_router(enrollment.router)

@app.get("/")
async def root():
    return {"message": "Critikality API - Running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
