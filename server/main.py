from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import (
    APP_NAME, APP_VERSION, DEBUG, HOST, PORT, RELOAD,
    ALLOWED_ORIGINS
)

from src.api.ui_routes import router as ui_router

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers

app.include_router(ui_router, prefix="/ui", tags=["UI Services"])


@app.get("/")
async def root():
    return {"message": f"Welcome to {APP_NAME}", "version": APP_VERSION}

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)