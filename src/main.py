from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.channels.whatsapp import router as whatsapp_router
from src.channels.atalking import router as at_router
from src.store import init_db


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(title="Hakiki", version="0.1.0", lifespan=lifespan)
app.include_router(whatsapp_router)
app.include_router(at_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
