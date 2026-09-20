from fastapi import APIRouter
from app.api.endpoints import query, schema, validate, eval, health, sample

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(query.router, tags=["Text-to-SQL Pipeline"])
api_router.include_router(schema.router, tags=["Database Schema"])
api_router.include_router(validate.router, tags=["SQL Validation"])
api_router.include_router(eval.router, tags=["Evaluation Suite"])
api_router.include_router(sample.router, tags=["Sample Queries"])
api_router.include_router(health.router, tags=["Health Check"])
