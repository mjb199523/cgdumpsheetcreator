"""
File upload routes.
Handles question paper and LO mapping uploads.
Auto-detects file types.

Upload paradigm:
  - Question Paper: tagged with medium + class (subjects auto-detected from Q ranges)
  - LO Mapping: tagged with subject + class (auto-detected from PDF header)
"""
import os
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.utils.file_utils import save_upload, validate_file_extension
from app.config import SUPPORTED_UPLOAD_TYPES
from app.models.schemas import ProcessingStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Upload"])

# In-memory store for uploaded files metadata
uploaded_files_store: List[dict] = []

# All allowed extensions across all types
ALL_ALLOWED = [".pdf", ".docx", ".xlsx", ".xls"]


def _detect_file_type(filename: str, hint: str = "") -> str:
    """Auto-detect file type from filename and extension."""
    ext = os.path.splitext(filename)[1].lower()
    name_lower = filename.lower()

    # Use hint if provided and valid
    if hint in ("question_paper", "lo_mapping", "sba_checklist"):
        return hint

    # Auto-detect from filename keywords
    if any(kw in name_lower for kw in ["lo mapping", "lo_mapping", "lomapping", "learning outcome",
                                        "mapping of learning"]):
        return "lo_mapping"
    if any(kw in name_lower for kw in ["checklist", "sba_checklist", "sba checklist"]):
        return "sba_checklist"
    if any(kw in name_lower for kw in ["question", "paper", "pat", "nipun", "sba",
                                        "periodic assessment", "class"]):
        return "question_paper"

    # Fallback by extension
    if ext in [".xlsx", ".xls"]:
        return "lo_mapping"
    if ext in [".pdf", ".docx"]:
        return "question_paper"

    return "question_paper"


@router.post("/files")
async def upload_files(
    files: List[UploadFile] = File(...),
    medium: str = Form(""),
    class_level: str = Form("0"),
    subject: str = Form(""),
    upload_type: str = Form("auto"),
):
    """
    Universal upload endpoint.

    For Question Papers: provide medium + class_level (subjects auto-detected)
    For LO Mappings: provide subject + class_level (auto-detected from PDF header)

    upload_type: "auto", "question_paper", or "lo_mapping"
    """
    results = []
    cls = 0
    try:
        cls = int(class_level)
    except (ValueError, TypeError):
        cls = 0

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALL_ALLOWED:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": f"Unsupported file type: {ext}. Allowed: {ALL_ALLOWED}",
            })
            continue

        # Detect file type
        detected_type = _detect_file_type(file.filename, upload_type if upload_type != "auto" else "")

        try:
            content = await file.read()
            meta = save_upload(content, file.filename, detected_type)
            meta.update({
                "medium": medium,
                "class_level": cls,
                "subject": subject,
                "detected_type": detected_type,
                "file_type": detected_type,
                "upload_time": datetime.now().isoformat(),
                "status": "uploaded",
            })
            uploaded_files_store.append(meta)
            results.append({
                "filename": file.filename,
                "status": "uploaded",
                "file_id": meta["file_id"],
                "detected_type": detected_type,
            })
        except Exception as e:
            logger.error(f"Upload error for {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e),
            })

    success_count = sum(1 for r in results if r.get("status") == "uploaded")
    return {
        "message": f"Uploaded {success_count} of {len(files)} file(s)",
        "results": results,
        "total_uploaded": success_count,
    }


# Keep legacy endpoints for backward compatibility
@router.post("/question-paper")
async def upload_question_paper(
    file: UploadFile = File(...),
    medium: str = Form(""),
    class_level: str = Form("0"),
):
    """Upload a question paper PDF or DOCX (tagged with medium + class)."""
    allowed = SUPPORTED_UPLOAD_TYPES["question_paper"]
    if not validate_file_extension(file.filename, allowed):
        raise HTTPException(400, f"Invalid file type. Allowed: {allowed}")

    cls = 0
    try:
        cls = int(class_level)
    except (ValueError, TypeError):
        pass

    content = await file.read()
    meta = save_upload(content, file.filename, "question_paper")
    meta.update({"medium": medium, "class_level": cls, "subject": "",
                 "upload_time": datetime.now().isoformat(), "status": "uploaded"})
    uploaded_files_store.append(meta)
    return {"message": "Question paper uploaded successfully", "file": meta}


@router.post("/lo-mapping")
async def upload_lo_mapping(
    file: UploadFile = File(...),
    subject: str = Form(""),
    class_level: str = Form("0"),
):
    """Upload an LO mapping PDF or Excel file (tagged with subject + class)."""
    allowed = SUPPORTED_UPLOAD_TYPES["lo_mapping"]
    if not validate_file_extension(file.filename, allowed):
        raise HTTPException(400, f"Invalid file type. Allowed: {allowed}")

    cls = 0
    try:
        cls = int(class_level)
    except (ValueError, TypeError):
        pass

    content = await file.read()
    meta = save_upload(content, file.filename, "lo_mapping")
    meta.update({"subject": subject, "class_level": cls, "medium": "",
                 "upload_time": datetime.now().isoformat(), "status": "uploaded"})
    uploaded_files_store.append(meta)
    return {"message": "LO mapping uploaded successfully", "file": meta}


@router.get("/list")
async def list_uploaded_files():
    """List all uploaded files."""
    return {"files": uploaded_files_store, "total": len(uploaded_files_store)}


@router.delete("/files/{file_id}")
async def delete_uploaded_file(file_id: str):
    """Delete an uploaded file."""
    global uploaded_files_store
    file_meta = next((f for f in uploaded_files_store if f["file_id"] == file_id), None)
    if not file_meta:
        raise HTTPException(404, "File not found")
    try:
        if os.path.exists(file_meta["file_path"]):
            os.remove(file_meta["file_path"])
    except Exception:
        pass
    uploaded_files_store = [f for f in uploaded_files_store if f["file_id"] != file_id]
    return {"message": "File deleted"}


@router.delete("/clear")
async def clear_all_uploads():
    """Clear all uploaded files."""
    global uploaded_files_store
    for f in uploaded_files_store:
        try:
            if os.path.exists(f["file_path"]):
                os.remove(f["file_path"])
        except Exception:
            pass
    uploaded_files_store.clear()
    return {"message": "All uploads cleared"}
