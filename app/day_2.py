from fastapi import FastAPI

app = FastAPI()

# Day 2 - Basic route
@app.get("/")
def root():
    return {"message": "Day 2 ready!"}


# 1. Path Parameter Example
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}


# 2. Multiple Path Parameters
@app.get("/orders/{order_id}/items/{item_id}")
def get_order_item(order_id: int, item_id: int):
    return {"order_id": order_id, "item_id": item_id}


# 3. Query Parameters Example
@app.get("/search")
def search(keyword: str, limit: int = 10):
    return {"keyword": keyword, "limit": limit}


# 4. Mixed usage (path + query)
@app.get("/products/{product_id}")
def get_product(product_id: int, detail: bool = False):
    return {
        "product_id": product_id,
        "detail": detail
    }

# 5. Square a number
@app.get("/square/{number}")
def square_number(number: int):
    return {"number": number, "square": number ** 2}

# 6. Greet user
@app.get("/greet/{name}")   
def greet_user(name: str):
    return {"message": f"Hello, {name}!"}

# 7. convert values 
@app.get("/convert/{value}")
def convert_value(value: float, unit: str):
    if unit == "kg":
        result = value * 1000   # kg ¡÷ g
        return {"input": value, "unit": unit, "result": result, "result_unit": "g"}

    elif unit == "m":
        result = value * 100    # m ¡÷ cm
        return {"input": value, "unit": unit, "result": result, "result_unit": "cm"}

    else:
        return {"error": "unit must be 'kg' or 'm'"}
