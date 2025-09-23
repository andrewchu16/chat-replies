from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .chats.router import router as chats_router
from .messages.router import router as messages_router
from .database import create_tables, close_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="Chat Replies Server",
    description="Server for the chat-replies project",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.debug else None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chats_router, prefix="/chats", tags=["chats"])
app.include_router(messages_router, prefix="/chats", tags=["messages"])

@app.get("/")
async def root():
    return {"message": "chat-replies server is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}
