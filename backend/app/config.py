"""
Assessment Content Operations Platform - Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output")
MEDIA_DIR = OUTPUT_DIR / "media"

# Create directories
for d in [UPLOAD_DIR, OUTPUT_DIR, MEDIA_DIR, MEDIA_DIR / "images", MEDIA_DIR / "tables", MEDIA_DIR / "audio", MEDIA_DIR / "documents"]:
    d.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Supported languages
SUPPORTED_LANGUAGES = ["Assamese", "Bengali", "Bodo", "English", "Hindi", "Karbi"]

# Supported file types
SUPPORTED_UPLOAD_TYPES = {
    "question_paper": [".pdf", ".docx"],
    "lo_mapping": [".pdf", ".docx", ".xlsx", ".xls"],
    "sba_checklist": [".xlsx", ".xls"],
}

# Assessment types
ASSESSMENT_TYPES = ["SBA", "PAT", "NIPUN"]

# Media config
MAX_FILE_SIZE_MB = 50
SUPPORTED_MEDIA_FORMATS = [".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4", ".wav", ".pdf"]
