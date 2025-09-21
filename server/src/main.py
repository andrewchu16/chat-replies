from fastapi import FastAPI
from contextlib import asynccontextmanager

from .chats.router import router as chats_router
from .messages.router import router as messages_router
from .config import settings
from .database import create_tables, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="LLM Chat API",
    description="API for an LLM chat website",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.debug else None
)

# Include routers
app.include_router(chats_router, prefix="/chats", tags=["chats"])
app.include_router(messages_router, prefix="/chats", tags=["messages"])

@app.get("/")
async def root():
    return {"message": "LLM Chat API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
