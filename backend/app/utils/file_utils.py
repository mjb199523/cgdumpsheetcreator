"""
File utilities for upload handling, path management, and ZIP creation.
"""
import os
import uuid
import shutil
import zipfile
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from app.config import UPLOAD_DIR, OUTPUT_DIR, MEDIA_DIR

logger = logging.getLogger(__name__)


def generate_file_id() -> str:
    """Generate a unique file ID."""
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def save_upload(file_content: bytes, original_filename: str,
                file_type: str = "general") -> dict:
    """
    Save an uploaded file to the uploads directory.
    Returns metadata about the saved file.
    """
    file_id = generate_file_id()
    ext = Path(original_filename).suffix.lower()
    safe_name = f"{file_id}{ext}"

    # Create type-specific subdirectory
    type_dir = UPLOAD_DIR / file_type
    type_dir.mkdir(parents=True, exist_ok=True)

    save_path = type_dir / safe_name
    with open(save_path, "wb") as f:
        f.write(file_content)

    return {
        "file_id": file_id,
        "original_name": original_filename,
        "file_type": file_type,
        "file_path": str(save_path),
        "file_size": len(file_content),
        "extension": ext,
    }


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension."""
    return Path(filename).suffix.lower()


def validate_file_extension(filename: str, allowed: list) -> bool:
    """Check if file extension is allowed."""
    return get_file_extension(filename) in allowed


def create_media_zip(output_name: str = "media_bundle.zip") -> str:
    """Create a ZIP file of the media directory."""
    zip_path = OUTPUT_DIR / output_name
    with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(str(MEDIA_DIR)):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(MEDIA_DIR.parent)
                zf.write(str(file_path), str(arcname))
    logger.info(f"Created media ZIP: {zip_path}")
    return str(zip_path)


def create_export_bundle(include_dump: bool = True, include_media: bool = True,
                         include_validation: bool = True) -> str:
    """Create a complete export bundle ZIP."""
    bundle_id = generate_file_id()
    bundle_name = f"export_bundle_{bundle_id}.zip"
    zip_path = OUTPUT_DIR / bundle_name

    with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zf:
        if include_dump:
            dump_path = OUTPUT_DIR / "dump_sheet.xlsx"
            if dump_path.exists():
                zf.write(str(dump_path), "dump_sheet.xlsx")

        if include_validation:
            val_path = OUTPUT_DIR / "validation_report.xlsx"
            if val_path.exists():
                zf.write(str(val_path), "validation_report.xlsx")

        if include_media:
            for root, dirs, files in os.walk(str(MEDIA_DIR)):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(OUTPUT_DIR)
                    zf.write(str(file_path), str(arcname))

    return str(zip_path)


def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """Remove files older than max_age_hours."""
    now = datetime.now()
    for item in directory.iterdir():
        if item.is_file():
            age = (now - datetime.fromtimestamp(item.stat().st_mtime)).total_seconds() / 3600
            if age > max_age_hours:
                item.unlink()
                logger.info(f"Cleaned up old file: {item.name}")


def get_output_files() -> list:
    """List all files in the output directory."""
    files = []
    for item in OUTPUT_DIR.iterdir():
        if item.is_file():
            files.append({
                "name": item.name,
                "path": str(item),
                "size": item.stat().st_size,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
            })
    return files


def clear_output_files():
    """Delete all files in the output directory."""
    for item in OUTPUT_DIR.iterdir():
        if item.is_file():
            item.unlink()
    logger.info("Cleared all output files")
