from fastapi import FastAPI,Query
from pydantic import BaseModel
import os
import signal

app = FastAPI()

@app.get("/")
def read_root():
    return {"day": 4, "message": "Welcome to Day 4!"}

class User(BaseModel):
    name: str
    email: str
    age: int    

@app.post("/users")
def create_user(user: User):   
    return {
        "message": "User created!",
        "user": user
    }    

def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='Server shutting down...')

@app.on_event('shutdown')
def on_shutdown():
    print('Server shutting down...')