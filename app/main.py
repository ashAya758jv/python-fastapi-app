"""Application FastAPI utilisée pour les expériences CI du TP5."""

from fastapi import FastAPI

from .config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)


@app.get("/")
def root():
    return {"message": "the server is now active"}


@app.get("/health")
def health():
    return {"ok": True}
