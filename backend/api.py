from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI()

# ✅ FIXED: Allow live frontend + localhost for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://hackernews-1.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve screenshots
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

@app.get("/api/results")
def get_results():
    if os.path.exists("output.json"):
        with open("output.json", "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"error": "output.json not found"}, status_code=404)
