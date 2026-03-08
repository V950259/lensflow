from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import router as api_router
from .api.auth import router as auth_router
from .db import database, models

# Create DB Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="LensFlow API", version="1.0.0")

# Allow all origins for simplicity in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(api_router, prefix="/api/v1", tags=["api"])

@app.on_event("startup")
async def startup_event():
    # Initialize DB and resources if needed
    pass

@app.get("/health")
async def health_check():
    return {"status": "ok"}
