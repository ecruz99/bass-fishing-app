from fastapi import FastAPI

from app.error_handlers import register_error_handlers
from app.routers import auth, health

app = FastAPI(title="Bass Fishing API", version="0.1.0")
register_error_handlers(app)

# Health stays outside /api/v1: it's for infrastructure, not part of the versioned API
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
