from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers.item import router as item_router
import signal
import os

app = FastAPI()
# Ensure process termination works correctly
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return {"message": "Server shutting down..."}

@app.on_event("shutdown")
def on_shutdown():
    print("Server shutting down...")

# Initialize database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(item_router)
