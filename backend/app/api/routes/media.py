"""
Media management routes.
"""
import os
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.config import MEDIA_DIR, OUTPUT_DIR
from app.engines.media_mapping import MediaMappingEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/media", tags=["Media"])


@router.get("/files")
async def list_media_files():
    """List all extracted media files."""
    files = {"images": [], "tables": [], "audio": [], "documents": []}
    for category in files:
        cat_dir = MEDIA_DIR / category
        if cat_dir.exists():
            for item in cat_dir.iterdir():
                if item.is_file():
                    files[category].append({
                        "name": item.name,
                        "path": f"media/{category}/{item.name}",
                        "size": item.stat().st_size,
                        "category": category,
                    })
    total = sum(len(v) for v in files.values())
    return {"files": files, "total": total}


@router.get("/stats")
async def media_stats():
    """Get media statistics."""
    stats = {}
    for category in ["images", "tables", "audio", "documents"]:
        cat_dir = MEDIA_DIR / category
        count = 0
        total_size = 0
        if cat_dir.exists():
            for item in cat_dir.iterdir():
                if item.is_file():
                    count += 1
                    total_size += item.stat().st_size
        stats[category] = {"count": count, "total_size_bytes": total_size}
    return {"stats": stats}


@router.delete("/files/{category}/{filename}")
async def delete_media_file(category: str, filename: str):
    """Delete a specific media file."""
    file_path = MEDIA_DIR / category / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    file_path.unlink()
    return {"message": f"Deleted {filename}"}


@router.delete("/clear")
async def clear_all_media():
    """Clear all media files."""
    import shutil
    for category in ["images", "tables", "audio", "documents"]:
        cat_dir = MEDIA_DIR / category
        if cat_dir.exists():
            shutil.rmtree(str(cat_dir))
            cat_dir.mkdir(parents=True, exist_ok=True)
    return {"message": "All media files cleared"}


@router.get("/validate-paths")
async def validate_media_paths():
    """Validate all media file paths referenced in dump sheet."""
    from app.api.routes.export import last_generated_data
    question_data = last_generated_data.get("question_master", [])
    paths = [r.get("media_file_path", "") for r in question_data if r.get("media_file_path")]
    results = MediaMappingEngine.validate_media_paths(paths)
    missing = [p for p, exists in results.items() if not exists]
    return {"total_paths": len(paths), "valid": len(paths) - len(missing),
            "missing": missing, "all_valid": len(missing) == 0}
