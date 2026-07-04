from fastapi import FastAPI
from src.channels.whatsapp import router as whatsapp_router
from src.channels.atalking import router as at_router
from src.store import init_db

app = FastAPI(title="Hakiki", version="0.1.0")
app.include_router(whatsapp_router)
app.include_router(at_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}
