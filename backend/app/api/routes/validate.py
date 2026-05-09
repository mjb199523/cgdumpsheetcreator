"""
Validation routes — Run guardrail validations on generated dump sheet data.
"""
import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from app.engines.validation_engine import ValidationEngine
from app.engines.excel_export import ExcelExportEngine
from app.blueprints.topic_master import TopicMasterBlueprint
from app.blueprints.assessment_master import AssessmentMasterBlueprint
from app.blueprints.question_master import QuestionMasterBlueprint
from app.config import OUTPUT_DIR

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/validate", tags=["Validation"])

# In-memory validation report store
last_validation_report = {}


def _load_default_rules():
    rules_path = Path(__file__).resolve().parent.parent.parent / "rules" / "validation_rules.json"
    if rules_path.exists():
        with open(rules_path, "r") as f:
            return json.load(f)
    return []


@router.post("/run")
async def run_validation(languages: str = Query("English", description="Comma-separated languages")):
    """Run full guardrail validation on the current dump sheet data."""
    from app.api.routes.export import last_generated_data

    if not last_generated_data:
        raise HTTPException(400, "No dump sheet data generated yet. Generate a dump sheet first.")

    langs = [l.strip() for l in languages.split(",")]

    # Collect all rules from blueprints + JSON
    all_rules = []
    all_rules.extend(TopicMasterBlueprint.get_validation_rules(langs))
    all_rules.extend(AssessmentMasterBlueprint.get_validation_rules())
    all_rules.extend(QuestionMasterBlueprint.get_validation_rules(langs))
    all_rules.extend(_load_default_rules())

    # Deduplicate rules by (sheet, column, rule)
    seen = set()
    unique_rules = []
    for r in all_rules:
        key = (r["sheet"], r["column"], r["rule"])
        if key not in seen:
            seen.add(key)
            unique_rules.append(r)

    # Build data dict for validation
    data = {
        "Topic Master": last_generated_data.get("topic_master", []),
        "Assessment Master": last_generated_data.get("assessment_master", []),
        "Generic Question Master Table": last_generated_data.get("question_master", []),
    }

    engine = ValidationEngine()
    report = engine.validate(data, unique_rules)

    last_validation_report.clear()
    last_validation_report["report"] = report
    last_validation_report["serialized"] = report.model_dump()
    last_validation_report["serialized"]["errors"] = [
        {**e.model_dump(), "severity": e.severity.value} for e in report.errors
    ]

    return {
        "message": "Validation complete",
        "is_valid": report.is_valid,
        "total_rules_checked": report.total_rules_checked,
        "total_errors": report.total_errors,
        "critical_errors": report.critical_errors,
        "warnings": report.warnings,
        "sheets_validated": report.sheets_validated,
        "errors": last_validation_report["serialized"]["errors"],
    }


@router.get("/report")
async def get_validation_report():
    """Get the last validation report."""
    if not last_validation_report:
        return {"message": "No validation report available", "errors": [], "is_valid": True}
    return last_validation_report.get("serialized", {})


@router.get("/export-report")
async def export_validation_report():
    """Export validation report as Excel file."""
    if not last_validation_report or "report" not in last_validation_report:
        raise HTTPException(400, "No validation report available")

    exporter = ExcelExportEngine()
    output_path = str(OUTPUT_DIR / "validation_report.xlsx")
    exporter.export_validation_report(last_validation_report["report"], output_path)

    return {
        "message": "Validation report exported",
        "file_path": output_path,
        "download_url": "/api/export/download/validation_report.xlsx",
    }


@router.get("/summary")
async def get_validation_summary():
    """Get a summary of validation issues grouped by sheet and severity."""
    if not last_validation_report or "report" not in last_validation_report:
        return {"sheets": {}, "total_errors": 0}

    report = last_validation_report["report"]
    summary = {}
    for err in report.errors:
        sheet = err.sheet
        if sheet not in summary:
            summary[sheet] = {"critical": 0, "warning": 0, "info": 0, "columns": {}}
        summary[sheet][err.severity.value] = summary[sheet].get(err.severity.value, 0) + 1
        col = err.column
        if col not in summary[sheet]["columns"]:
            summary[sheet]["columns"][col] = 0
        summary[sheet]["columns"][col] += 1

    return {"sheets": summary, "total_errors": report.total_errors, "is_valid": report.is_valid}
