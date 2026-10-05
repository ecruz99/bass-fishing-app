from fastapi import FastAPI

from app.routers import health

app = FastAPI(title="Bass Fishing API", version="0.1.0")

# Health stays outside /api/v1: it's for infrastructure, not part of the versioned API
app.include_router(health.router)
