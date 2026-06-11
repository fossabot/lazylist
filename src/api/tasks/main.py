from fastapi import FastAPI

API = FastAPI(root_path="/tasks")

@API.get("/health")
def health():
    return {"status": "OK"}
