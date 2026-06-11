from fastapi import FastAPI

API = FastAPI(root_path="/auth")

@API.get("/health")
def health():
    return {"status": "OK"}
