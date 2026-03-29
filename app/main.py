from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    expenses,
    investments,
    investors,
    rubrics,
    stats,
    transfers,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="FINOR API",
        description=(
            "Backend for FINOR - a village investment and project fund management platform. "
            "Two roles: Investor (personal code) and Treasurer (JWT)."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(rubrics.router)
    app.include_router(investments.router)
    app.include_router(expenses.router)
    app.include_router(transfers.router)
    app.include_router(investors.router)
    app.include_router(stats.router)

    return app


app = create_app()
