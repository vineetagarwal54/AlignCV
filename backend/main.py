from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def greet() -> str:
    return f"Hello!"
