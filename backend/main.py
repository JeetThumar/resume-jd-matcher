from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

# Load config early so environment is ready
from resume_matcher.config import settings

from resume_matcher.parser import parse_uploaded_file, extract_text_from_txt
from resume_matcher.matcher import match_resume_to_jd

app = FastAPI(title="Resume JD Matcher API")

# Allow CORS for the Vite frontend (local dev + Vercel production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",           # local Vite dev server
        "http://127.0.0.1:5173",           # local Vite (alternate)
        "https://resume-jd-matcher.vercel.app",  # Vercel production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    api_key_configured = False
    if settings is not None:
        api_key_configured = bool(settings.gemini_api_key)
    return {"status": "ok", "api_key_configured": api_key_configured}

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    jd_text: str = Form(None),
    jd_file: UploadFile = File(None),
):
    """
    Accepts a resume PDF and a job description (either as text or file),
    extracts the text, and calls the Gemini API to match them.
    """
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF file.")
    
    if not jd_text and not jd_file:
        raise HTTPException(status_code=400, detail="Must provide either jd_text or jd_file.")

    try:
        # 1. Parse Resume
        resume_bytes = await resume.read()
        resume_content = parse_uploaded_file(resume_bytes, resume.filename)
        
        # 2. Parse JD
        if jd_text:
            jd_content = jd_text
        else:
            jd_bytes = await jd_file.read()
            jd_content = parse_uploaded_file(jd_bytes, jd_file.filename)
            
        # 3. Call LLM Matcher
        result = match_resume_to_jd(resume_content, jd_content)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=f"Configuration Error: {e}")
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=f"LLM API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
