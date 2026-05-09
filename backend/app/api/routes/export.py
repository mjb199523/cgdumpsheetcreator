"""
Export routes — Dump sheet generation, Excel export, and file downloads.
"""
import os
import logging
from typing import Optional
from datetime import date
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from app.engines.dump_sheet_gen import DumpSheetGenerator
from app.engines.excel_export import ExcelExportEngine
from app.engines.validation_engine import ValidationEngine
from app.models.schemas import ProjectConfig, AssessmentType, Medium
from app.config import OUTPUT_DIR
from app.utils.file_utils import create_media_zip, create_export_bundle, get_output_files

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["Export"])

# In-memory store for last generated data
last_generated_data = {}
export_history = []


@router.post("/generate")
async def generate_dump_sheet(
    project_name: str = Query("Assessment Project"),
    subjects: str = Query("English", description="Comma-separated subjects"),
    classes: str = Query("5", description="Comma-separated class levels"),
    mediums: str = Query("English", description="Comma-separated mediums"),
    academic_year: str = Query("2025-26"),
    assessment_type: str = Query("PAT"),
    launch_date: str = Query("2025-06-01"),
    close_date: str = Query("2025-06-30"),
):
    """Generate a complete dump sheet from merged question data."""
    from app.api.routes.parse import merged_data_store

    if not merged_data_store or not merged_data_store.get("merged_questions"):
        raise HTTPException(400, "No merged data available. Complete the parse and resolve steps first.")

    try:
        medium_list = [Medium(m.strip()) for m in mediums.split(",") if m.strip() in [e.value for e in Medium]]
        if not medium_list:
            medium_list = [Medium.ASSAMESE]

        # Auto-detect subjects and classes from merged data if not explicitly provided
        merged_questions = merged_data_store["merged_questions"]
        if subjects.strip().lower() in ("auto", ""):
            detected_subjects = list(set(q.subject for q in merged_questions if q.subject))
        else:
            detected_subjects = [s.strip() for s in subjects.split(",")]

        detected_classes = list(set(q.class_level for q in merged_questions if q.class_level))
        if not detected_classes:
            detected_classes = [int(c.strip()) for c in classes.split(",")]

        config = ProjectConfig(
            project_name=project_name,
            subjects=detected_subjects,
            classes=detected_classes,
            mediums=medium_list,
            academic_year=academic_year,
            assessment_type=AssessmentType(assessment_type),
            launch_date=date.fromisoformat(launch_date),
            close_date=date.fromisoformat(close_date),
        )

        generator = DumpSheetGenerator(config)
        sheet_data = generator.generate(merged_data_store["merged_questions"])

        last_generated_data.clear()
        last_generated_data.update(sheet_data)

        return {
            "message": "Dump sheet data generated successfully",
            "topic_master_rows": len(sheet_data["topic_master"]),
            "assessment_master_rows": len(sheet_data["assessment_master"]),
            "question_master_rows": len(sheet_data["question_master"]),
        }
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(500, f"Dump sheet generation failed: {str(e)}")


@router.post("/excel")
async def export_to_excel(
    filename: str = Query("dump_sheet.xlsx"),
    languages: str = Query("English"),
    apply_validation: bool = Query(True),
):
    """Export generated dump sheet data to Excel workbook."""
    if not last_generated_data:
        raise HTTPException(400, "No dump sheet data available. Generate first.")

    try:
        langs = [l.strip() for l in languages.split(",")]
        output_path = str(OUTPUT_DIR / filename)

        # Run validation if requested
        validation_report = None
        if apply_validation:
            from app.api.routes.validate import last_validation_report
            if last_validation_report and "report" in last_validation_report:
                validation_report = last_validation_report["report"]

        exporter = ExcelExportEngine(languages=langs)
        result_path = exporter.export(last_generated_data, output_path, validation_report)

        export_history.append({
            "filename": filename,
            "path": result_path,
            "timestamp": str(date.today()),
            "rows": len(last_generated_data.get("question_master", [])),
        })

        return {
            "message": "Excel workbook exported successfully",
            "file_path": result_path,
            "download_url": f"/api/export/download/{filename}",
        }
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(500, f"Excel export failed: {str(e)}")


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Download an exported file."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, f"File not found: {filename}")
    return FileResponse(
        str(file_path),
        filename=filename,
        media_type="application/octet-stream",
    )


@router.post("/media-zip")
async def create_media_archive():
    """Create a ZIP of all media files."""
    try:
        zip_path = create_media_zip()
        return {
            "message": "Media ZIP created",
            "download_url": f"/api/export/download/{os.path.basename(zip_path)}",
        }
    except Exception as e:
        raise HTTPException(500, f"ZIP creation failed: {str(e)}")


@router.post("/bundle")
async def create_full_bundle(
    include_dump: bool = Query(True),
    include_media: bool = Query(True),
    include_validation: bool = Query(True),
):
    """Create a complete export bundle ZIP."""
    try:
        zip_path = create_export_bundle(include_dump, include_media, include_validation)
        return {
            "message": "Export bundle created",
            "download_url": f"/api/export/download/{os.path.basename(zip_path)}",
        }
    except Exception as e:
        raise HTTPException(500, f"Bundle creation failed: {str(e)}")


@router.get("/files")
async def list_output_files():
    """List all available output files."""
    return {"files": get_output_files()}


@router.get("/history")
async def get_export_history():
    """Get export history."""
    return {"history": export_history}


@router.post("/clear")
async def clear_export():
    """Clear all exported files."""
    try:
        from app.utils.file_utils import clear_output_files
        clear_output_files()
        export_history.clear()
        return {"message": "All export files cleared successfully"}
    except Exception as e:
        logger.error(f"Clear error: {e}")
        raise HTTPException(500, f"Failed to clear export files: {str(e)}")
