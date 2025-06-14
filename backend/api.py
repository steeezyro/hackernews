from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

@app.get("/api/results")
def get_results():
    if os.path.exists("output.json"):
        with open("output.json", "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"error": "output.json not found"}, status_code=404)
