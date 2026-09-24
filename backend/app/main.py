from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import (
    auth, cities, places, search, rag, itinerary, recommendations, agents, analytics
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Plan AI City - RAG-Powered City Intelligence & Personalized Planning Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
api_v1 = settings.API_V1_STR
app.include_router(auth.router, prefix=f"{api_v1}/auth", tags=["Authentication & User Profiles"])
app.include_router(cities.router, prefix=f"{api_v1}/cities", tags=["Cities"])
app.include_router(places.router, prefix=f"{api_v1}/places", tags=["Places & Categories"])
app.include_router(search.router, prefix=f"{api_v1}/search", tags=["Hybrid Search"])
app.include_router(rag.router, prefix=f"{api_v1}/rag", tags=["RAG & Knowledge Retrieval"])
app.include_router(itinerary.router, prefix=f"{api_v1}/itinerary", tags=["Intelligent Itinerary Planner"])
app.include_router(recommendations.router, prefix=f"{api_v1}/recommendations", tags=["ML Recommendations"])
app.include_router(agents.router, prefix=f"{api_v1}/agents", tags=["Multi-Agent Swarm Chat"])
app.include_router(analytics.router, prefix=f"{api_v1}/analytics", tags=["City Intelligence & Analytics"])

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return {}

# Silently handle browser extension telemetry pings (e.g. zybTracker, extension actions)
@app.get("/hybridaction/{rest_of_path:path}", include_in_schema=False)
def ignore_extension_telemetry(rest_of_path: str):
    return {"status": "ok"}

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Plan AI City API",
        "docs": "/docs",
        "health": "/health"
    }
