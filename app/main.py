from fastapi import FastAPI

app = FastAPI(title="Rai Bot")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
