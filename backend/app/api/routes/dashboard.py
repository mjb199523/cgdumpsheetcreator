"""
Dashboard routes — Statistics and processing overview.
"""
from fastapi import APIRouter
from app.api.routes.upload import uploaded_files_store
from app.api.routes.parse import parsed_questions_by_file, parsed_lo_by_file, merged_data_store, _all_parsed_questions, _all_parsed_los
from app.api.routes.export import last_generated_data, export_history
from app.config import MEDIA_DIR

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics."""
    # Count media files
    media_count = 0
    for cat in ["images", "tables", "audio", "documents"]:
        cat_dir = MEDIA_DIR / cat
        if cat_dir.exists():
            media_count += sum(1 for f in cat_dir.iterdir() if f.is_file())

    # Validation stats
    from app.api.routes.validate import last_validation_report
    val_report = last_validation_report.get("report")
    validation_issues = val_report.total_errors if val_report else 0
    critical_errors = val_report.critical_errors if val_report else 0

    # Mapping stats
    total_merged = len(merged_data_store.get("merged_questions", []))
    unmatched_q = len(merged_data_store.get("unmatched_questions", []))
    unmatched_lo = len(merged_data_store.get("unmatched_lo_ids", []))

    all_questions = _all_parsed_questions()
    all_los = _all_parsed_los()

    # Subject breakdown from parsed questions
    subject_counts = {}
    for q in all_questions:
        subj = q.subject or "Unknown"
        subject_counts[subj] = subject_counts.get(subj, 0) + 1

    return {
        "total_uploads": len(uploaded_files_store),
        "question_papers_uploaded": sum(1 for f in uploaded_files_store if f.get("file_type") == "question_paper"),
        "lo_mappings_uploaded": sum(1 for f in uploaded_files_store if f.get("file_type") == "lo_mapping"),
        "qp_files_parsed": len(parsed_questions_by_file),
        "lo_files_parsed": len(parsed_lo_by_file),
        "total_questions_parsed": len(all_questions),
        "total_lo_parsed": len(all_los),
        "total_merged": total_merged,
        "unmatched_questions": unmatched_q,
        "unmatched_lo_ids": unmatched_lo,
        "match_rate": merged_data_store.get("match_rate", 0),
        "subject_breakdown": subject_counts,
        "total_validation_issues": validation_issues,
        "critical_errors": critical_errors,
        "missing_mappings": unmatched_q + unmatched_lo,
        "total_media_files": media_count,
        "missing_media": 0,
        "missing_translations": 0,
        "total_exports": len(export_history),
        "recent_exports": export_history[-5:] if export_history else [],
        "dump_sheet_generated": bool(last_generated_data),
        "processing_status": {
            "upload": "complete" if uploaded_files_store else "pending",
            "parsing": "complete" if parsed_questions_by_file else "pending",
            "lo_mapping": "complete" if parsed_lo_by_file else "pending",
            "merging": "complete" if total_merged > 0 else "pending",
            "generation": "complete" if last_generated_data else "pending",
            "validation": "complete" if val_report else "pending",
            "export": "complete" if export_history else "pending",
        },
    }
