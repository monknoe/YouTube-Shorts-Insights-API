from fastapi import FastAPI,Query
from pydantic import BaseModel
import os
import signal

app = FastAPI()

@app.get("/")
def read_root():
    return {"day": 3, "message": "Welcome to Day 3!"}

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

class Address(BaseModel):
    city: str
    zipcode: str

class Person(BaseModel):
    name: str
    age: int
    address: Address

@app.post("/persons")
def create_person(person: Person):
    return {
        "message": "Person created!",
        "person": person
    }

@app.get("/convert")
def convert_value(value: int, unit: str = "cm"):#default unit is cm
    return {
        "original_value": value,
        "unit": unit,
        "converted": f"{value} {unit}"
    }

@app.get("/BMI")
def calculate_bmi(
    weight: float = Query(..., gt=0),
    height: float = Query(..., gt=0)
):
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    def bmi_category(bmi):
        if bmi < 18.5:
            return "Underweight"
        if bmi < 24:
            return "Normal weight"
        if bmi < 27:
            return "Overweight"
        return "Obesity"

    return {
        "BMI": round(bmi, 2),
        "Category": bmi_category(bmi)
    }

def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='Server shutting down...')

@app.on_event('shutdown')
def on_shutdown():
    print('Server shutting down...')