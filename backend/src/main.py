from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings

import src.database.all_models  # noqa: F401 — register all models


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from src.database.seed import seed_roles_and_admin
        await seed_roles_and_admin()
    except Exception:
        pass
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

from src.middlewares.security import RateLimitMiddleware, SecurityHeadersMiddleware  # noqa: E402

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────
from src.auth.router import router as auth_router  # noqa: E402
from src.users.router import router as users_router  # noqa: E402
from src.companies.router import router as companies_router  # noqa: E402
from src.delivery.router import router as delivery_router  # noqa: E402
from src.couriers.router import router as couriers_router  # noqa: E402
from src.notifications.router import router as notifications_router  # noqa: E402
from src.analytics.router import router as analytics_router  # noqa: E402
from src.tracking.router import router as tracking_router  # noqa: E402
from src.schemas.audit_router import router as audit_router  # noqa: E402
from src.ai.router import router as ai_router  # noqa: E402
from src.websockets.router import router as ws_router  # noqa: E402

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(companies_router, prefix="/api/companies", tags=["Companies"])
app.include_router(delivery_router, prefix="/api", tags=["Delivery"])
app.include_router(couriers_router, prefix="/api", tags=["Couriers"])
app.include_router(notifications_router, prefix="/api", tags=["Notifications"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
app.include_router(tracking_router, prefix="/api", tags=["Tracking"])
app.include_router(audit_router, prefix="/api", tags=["Audit"])
app.include_router(ai_router, prefix="/api", tags=["AI"])
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
