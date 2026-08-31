import os
import asyncio
import logging
import httpx
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

async def _self_ping_loop():
    """
    Background loop that pings the server every 4.5 minutes (270s)
    to prevent free cloud instances (like Render) from sleeping.
    """
    target_url = (
        os.getenv("SELF_PING_URL")
        or os.getenv("RENDER_EXTERNAL_URL")
        or (f"http://127.0.0.1:{settings.PORT}/health")
    ).strip()

    logger.info(f"Self-ping keep-alive loop initiated for target: {target_url}")
    # Initial grace delay
    await asyncio.sleep(60)

    async with httpx.AsyncClient(timeout=15.0) as client:
        while True:
            try:
                ping_url = target_url if target_url.endswith("/health") else f"{target_url.rstrip('/')}/health"
                resp = await client.get(ping_url)
                logger.info(f"[Keep-Alive] Self-ping status {resp.status_code} on {ping_url}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"[Keep-Alive] Self-ping note: {e}")
            
            # Sleep 4.5 minutes (270 seconds)
            await asyncio.sleep(270)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RELAY database...")
    await init_db()
    logger.info("RELAY Autonomous Operations Agent Engine Online.")
    
    # Start self-ping keep-alive background task
    ping_task = asyncio.create_task(_self_ping_loop())
    yield
    # Cleanup keep-alive task
    ping_task.cancel()
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

@app.get("/")
@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "RELAY Autonomous Operations Core",
        "version": settings.VERSION,
        "calle_mode": "LIVE_ENABLED" if settings.CALLE_API_KEY and not settings.FORCE_SIMULATION else "SANDBOX_SIMULATION",
        "keep_alive": "ACTIVE"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
