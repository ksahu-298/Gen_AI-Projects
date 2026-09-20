import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.db.session import get_db_engine
from app.db.seed_data import seed_database
from app.api.router import api_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger("text_to_sql.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    Automatically initializes engine and seeds database tables if needed.
    """
    logger.info("Initializing Talk to Your Data backend engine...")
    try:
        engine = get_db_engine()
        seed_database(engine)
        logger.info("Database schema verification and seeding complete.")
    except Exception as e:
        logger.error(f"Error during database startup initialization: {e}")
    
    yield
    
    logger.info("Shutting down Talk to Your Data service.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade Natural Language to SQL Analytics Assistant with AST Guardrails, Self-Correction, Visualization and Plain-English Explanations.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount Static Files for Frontend UI
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
