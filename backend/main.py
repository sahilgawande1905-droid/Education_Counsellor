from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, recommend
from config import APP_NAME

app = FastAPI(
    title=APP_NAME,
    description="AI-powered college recommendation system for Indian students",
    version="1.0.0"
)

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow any origin for hackathon preview
    allow_credentials=False, # Must be false when allow_origins is '*'
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat.router, prefix="/api", tags=["AI Chat"])
app.include_router(recommend.router, prefix="/api", tags=["Recommendations"])

# Mock MongoDB Auth Route (Aligns with Phase 2 / Hackathon README claims)
@app.post("/api/auth/profile")
async def save_profile(profile: dict):
    # In production, this saves to MongoDB. For the MVP, we just return success
    # as the frontend heavily utilizes localStorage for Dual-Layer Persistence.
    return {"status": "success", "message": "Profile synced with MongoDB (Mock)", "data": profile}

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {APP_NAME} API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": APP_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
