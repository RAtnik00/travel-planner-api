from fastapi import FastAPI

app = FastAPI(title="Travel Planner API")


@app.get("/")
def read_root():
    return {"message": "Travel Planner API is running"}