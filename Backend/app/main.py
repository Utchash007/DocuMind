import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env variables from the root directory (.env is in d:\AI_Projects\Documind)
root_dir = Path(__file__).resolve().parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="DocuMind Backend", version="1.0.0")

# CORS middleware to allow Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to Frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to DocuMind API"}

@app.get("/health")
def health_check():
    # Verify environment keys are loaded
    groq_api_key = os.getenv("GROQ_API_KEY")
    chroma_host = os.getenv("CHROMA_HOST")
    
    return {
        "status": "healthy",
        "config_status": {
            "groq_api_key_loaded": bool(groq_api_key),
            "chroma_host_loaded": bool(chroma_host),
        }
    }
