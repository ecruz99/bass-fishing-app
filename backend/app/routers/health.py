from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Report that the API process is up. Used by Render and the keep-warm ping."""
    return {"status": "ok"}
