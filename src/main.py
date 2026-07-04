from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.channels import whatsapp, atalking

app = FastAPI(title="Hakiki Backend")

# Include routers
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
app.include_router(atalking.router, prefix="/at", tags=["AfricasTalking"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Hakiki Backend is running."}
