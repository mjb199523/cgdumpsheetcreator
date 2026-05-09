"""
Parse routes — Question Paper and LO Mapping parsing endpoints.

Key data flow:
  - Question papers: uploaded per (medium, class). Parser auto-detects subjects from Q ranges.
  - LO mappings: uploaded per (subject, class). Parser auto-detects from PDF header.
  - Stores are KEYED (not flat) so multiple files can be parsed without overwriting.
  - Resolve merges ALL parsed questions with ALL parsed LOs by matching (subject, class, qnum=item_id).
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.engines.question_parser import QuestionPaperParser
from app.engines.lo_mapping_parser import LOMappingParser
from app.engines.mapping_resolver import MappingResolver
from app.api.routes.upload import uploaded_files_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/parse", tags=["Parsing"])

# ─── Keyed stores ────────────────────────────────────────────────────────────
# Questions: keyed by file_id → list of ParsedQuestion
# This preserves all parsed files (no overwriting)
parsed_questions_by_file = {}  # file_id → [ParsedQuestion, ...]

# LO Mappings: keyed by file_id → list of LOMapping
parsed_lo_by_file = {}  # file_id → [LOMapping, ...]

# Merged data: aggregated from all parsed files
merged_data_store = {}


def _all_parsed_questions():
    """Get all parsed questions across all files."""
    all_q = []
    for qs in parsed_questions_by_file.values():
        all_q.extend(qs)
    return all_q


def _all_parsed_los():
    """Get all parsed LO mappings across all files."""
    all_lo = []
    for los in parsed_lo_by_file.values():
        all_lo.extend(los)
    return all_lo


@router.post("/question-paper/{file_id}")
async def parse_question_paper(
    file_id: str,
    medium: str = Query("", description="Medium (auto-detected from PDF if empty)"),
    class_level: int = Query(0, description="Class level (auto-detected from PDF if 0)"),
):
    """
    Parse an uploaded question paper file.
    Class, Medium, and Subject are auto-detected from the PDF header.
    Each question is tagged with its subject based on Q-number ranges.
    """
    file_meta = next((f for f in uploaded_files_store if f["file_id"] == file_id), None)
    if not file_meta:
        raise HTTPException(404, "File not found")

    parser = QuestionPaperParser()
    med = medium or file_meta.get("medium", "")
    cls = class_level or file_meta.get("class_level", 0)

    try:
        questions = parser.parse_file(file_meta["file_path"], med, cls)

        # Store keyed by file_id (no overwriting)
        parsed_questions_by_file[file_id] = questions

        # Update file status
        file_meta["status"] = "parsed"

        # Build per-subject summary
        subject_summary = {}
        for q in questions:
            subj = q.subject or "Unknown"
            if subj not in subject_summary:
                subject_summary[subj] = {"count": 0, "class_level": q.class_level, "medium": q.medium}
            subject_summary[subj]["count"] += 1

        # Detect class and medium from parsed data
        detected_class = questions[0].class_level if questions else cls
        detected_medium = questions[0].medium if questions else med

        return {
            "message": f"Parsed {len(questions)} questions",
            "total_questions": len(questions),
            "detected_class": detected_class,
            "detected_medium": detected_medium,
            "subject_breakdown": subject_summary,
            "questions": [q.model_dump() for q in questions],
            "images_extracted": len(parser.get_extracted_images()),
        }
    except Exception as e:
        logger.error(f"Parse error: {e}")
        raise HTTPException(500, f"Parsing failed: {str(e)}")


@router.post("/lo-mapping/{file_id}")
async def parse_lo_mapping(
    file_id: str,
    subject: str = Query("", description="Subject (auto-detected from PDF if empty)"),
    class_level: int = Query(0, description="Class level (auto-detected from PDF if 0)"),
):
    """
    Parse an uploaded LO mapping file.
    Subject and Class are auto-detected from the PDF header.
    """
    file_meta = next((f for f in uploaded_files_store if f["file_id"] == file_id), None)
    if not file_meta:
        raise HTTPException(404, "File not found")

    parser = LOMappingParser()
    subj = subject or file_meta.get("subject", "")
    cls = class_level or file_meta.get("class_level", 0)

    try:
        mappings = parser.parse_file(file_meta["file_path"], subj, cls)

        # Store keyed by file_id (no overwriting)
        parsed_lo_by_file[file_id] = mappings

        file_meta["status"] = "parsed"

        # Detect subject and class from parsed data
        detected_subject = mappings[0].subject if mappings else subj
        detected_class = mappings[0].class_level if mappings else cls

        # Summary
        lo_summary = {}
        for m in mappings:
            key = f"{m.subject} (Class {m.class_level})"
            if key not in lo_summary:
                lo_summary[key] = 0
            lo_summary[key] += 1

        return {
            "message": f"Parsed {len(mappings)} LO mappings",
            "total_mappings": len(mappings),
            "detected_subject": detected_subject,
            "detected_class": detected_class,
            "lo_summary": lo_summary,
            "mappings": [m.model_dump() for m in mappings],
        }
    except Exception as e:
        logger.error(f"LO parse error: {e}")
        raise HTTPException(500, f"LO mapping parsing failed: {str(e)}")


@router.post("/resolve-mappings")
async def resolve_mappings(
    medium: str = Query("", description="Medium override"),
):
    """
    Merge ALL parsed questions with ALL parsed LO mappings.
    Matches by (subject, class, question_number == item_id).
    """
    all_questions = _all_parsed_questions()
    all_los = _all_parsed_los()

    if not all_questions:
        raise HTTPException(400, "No parsed questions available. Parse question paper(s) first.")
    if not all_los:
        raise HTTPException(400, "No parsed LO mappings available. Parse LO mapping file(s) first.")

    resolver = MappingResolver()
    result = resolver.resolve(all_questions, all_los, medium)

    merged_data_store.clear()
    merged_data_store.update(result)
    merged_data_store["merged_questions_serialized"] = [
        q.model_dump() for q in result["merged_questions"]
    ]

    return {
        "message": f"Resolved {len(result['merged_questions'])} mappings",
        "total_merged": len(result["merged_questions"]),
        "total_questions": result["total_questions"],
        "total_lo_mappings": result["total_lo_mappings"],
        "unmatched_questions": result["unmatched_questions"],
        "unmatched_lo_ids": result["unmatched_lo_ids"],
        "match_rate": result["match_rate"],
        "subject_breakdown": result["subject_breakdown"],
        "merged_questions": merged_data_store["merged_questions_serialized"],
    }


@router.get("/questions")
async def get_parsed_questions():
    """Get all parsed questions across all files."""
    all_q = _all_parsed_questions()
    return {
        "total": len(all_q),
        "files_parsed": len(parsed_questions_by_file),
        "questions": [q.model_dump() for q in all_q],
    }


@router.get("/lo-mappings")
async def get_parsed_lo_mappings():
    """Get all parsed LO mappings across all files."""
    all_lo = _all_parsed_los()
    return {
        "total": len(all_lo),
        "files_parsed": len(parsed_lo_by_file),
        "mappings": [m.model_dump() for m in all_lo],
    }


@router.get("/merged")
async def get_merged_data():
    """Get merged question + LO data."""
    if not merged_data_store:
        return {"message": "No merged data available", "total": 0, "merged_questions": []}
    return {
        "total": len(merged_data_store.get("merged_questions", [])),
        "match_rate": merged_data_store.get("match_rate", 0),
        "unmatched_questions": merged_data_store.get("unmatched_questions", []),
        "unmatched_lo_ids": merged_data_store.get("unmatched_lo_ids", []),
        "subject_breakdown": merged_data_store.get("subject_breakdown", {}),
        "merged_questions": merged_data_store.get("merged_questions_serialized", []),
    }


@router.get("/summary")
async def get_parse_summary():
    """Get a summary of all parsed data — questions per file, LOs per file."""
    q_summary = {}
    for file_id, qs in parsed_questions_by_file.items():
        file_meta = next((f for f in uploaded_files_store if f["file_id"] == file_id), {})
        subject_counts = {}
        for q in qs:
            subject_counts[q.subject] = subject_counts.get(q.subject, 0) + 1
        q_summary[file_id] = {
            "filename": file_meta.get("original_name", ""),
            "total_questions": len(qs),
            "class_level": qs[0].class_level if qs else 0,
            "medium": qs[0].medium if qs else "",
            "subjects": subject_counts,
        }

    lo_summary = {}
    for file_id, los in parsed_lo_by_file.items():
        file_meta = next((f for f in uploaded_files_store if f["file_id"] == file_id), {})
        lo_summary[file_id] = {
            "filename": file_meta.get("original_name", ""),
            "total_mappings": len(los),
            "subject": los[0].subject if los else "",
            "class_level": los[0].class_level if los else 0,
        }

    return {
        "question_papers": q_summary,
        "lo_mappings": lo_summary,
        "total_questions": len(_all_parsed_questions()),
        "total_lo_mappings": len(_all_parsed_los()),
    }
