from fastapi import FastAPI

from app import config  # valida as variáveis de ambiente na subida do app

app = FastAPI(title="Rai Bot")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
