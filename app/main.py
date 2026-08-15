from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.movies import router as movies_router

app = FastAPI(
    title="Online Cinema API",
    description="A FastAPI-based Online Cinema API",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(movies_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Online Cinema API"}
