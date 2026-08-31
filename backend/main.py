import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db
from backend.routes.missions import router as missions_router
from backend.routes.websocket import router as ws_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("relay")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RELAY database...")
    await init_db()
    logger.info("RELAY Autonomous Operations Agent Engine Online.")
    yield
    logger.info("RELAY Engine shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(missions_router, prefix=settings.API_PREFIX)
app.include_router(ws_router)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "RELAY Backend",
        "version": settings.VERSION,
        "calle_mode": "LIVE_ENABLED" if settings.CALLE_API_KEY and not settings.FORCE_SIMULATION else "SANDBOX_SIMULATION"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
