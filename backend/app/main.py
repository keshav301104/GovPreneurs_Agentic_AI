from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

app = FastAPI(title="GovPreneurs AI Backend")

# --- CORS CONFIGURATION ---
# This block is mandatory for your Next.js frontend to communicate with Python.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allows your Next.js frontend
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"], # Allows all headers
)
# --------------------------

# Mount our API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "GovPreneurs AI Pipeline is Online and Ready."}