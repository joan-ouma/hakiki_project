from fastapi import FastAPI
from src.channels.whatsapp import router as whatsapp_router

app = FastAPI(title="Hakiki", version="0.1.0")
app.include_router(whatsapp_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
