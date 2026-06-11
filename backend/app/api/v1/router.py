"""Aggregates all v1 route modules."""

from fastapi import APIRouter

from app.api.v1.routes import auth, documents, graph, health, ingest, jobs, query

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(query.router)
api_router.include_router(graph.router)
api_router.include_router(ingest.router)
api_router.include_router(documents.router)
api_router.include_router(jobs.router)
