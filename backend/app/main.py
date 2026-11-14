from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api import climate, vegetation, farms, crops, reports, health, analysis

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FieldShift - Plateforme d'analyse agricole intelligente",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(farms.router, prefix="/api/farms", tags=["Farms"])
app.include_router(climate.router, prefix="/api/climate", tags=["Climate"])
app.include_router(vegetation.router, prefix="/api/vegetation", tags=["Vegetation"])
app.include_router(crops.router, prefix="/api/crops", tags=["Crops"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "FieldShift API - Plateforme d'analyse agricole intelligente",
        "docs": "/docs",
    }