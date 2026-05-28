"""Aggregates all v1 route modules."""

from fastapi import APIRouter

from app.api.v1.routes import auth, health, query

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(query.router)
