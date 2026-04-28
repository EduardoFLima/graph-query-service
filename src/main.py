from fastapi import FastAPI

from src.adapters.inbound.api.chat_router import router as chat_router

app = FastAPI()
app.include_router(chat_router)

@app.get("/health")
def get_health():
    return { "status": "OK" }