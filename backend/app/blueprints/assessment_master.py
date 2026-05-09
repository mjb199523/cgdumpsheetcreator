"""
Assessment Master Sheet Blueprint.
Defines the structure, columns, and validation rules for the Assessment Master sheet.
"""
from typing import List, Dict, Any


class AssessmentMasterBlueprint:
    """Blueprint for the Assessment Master sheet."""

    SHEET_NAME = "Assessment Master"

    @staticmethod
    def get_columns() -> List[Dict[str, Any]]:
        """Generate column definitions for Assessment Master."""
        columns = [
            {"name": "topic_id", "display": "Topic ID", "type": "string", "required": True},
            {"name": "assessment_id", "display": "Assessment ID", "type": "string", "required": True, "unique": True},
            {"name": "assessment_name", "display": "Assessment Name", "type": "string", "required": True},
            {"name": "assessment_description", "display": "Assessment Description", "type": "string", "required": False},
            {"name": "class_mapping", "display": "Class Mapping", "type": "string", "required": True},
            {"name": "multiple_entry_config", "display": "Multiple Entry Config", "type": "string", "required": False,
             "allowed_values": ["Yes", "No"]},
            {"name": "stream", "display": "Stream", "type": "string", "required": False},
            {"name": "launch_date", "display": "Launch Date", "type": "date", "required": True},
            {"name": "close_date", "display": "Close Date", "type": "date", "required": True},
            {"name": "timed_assessment", "display": "Timed Assessment", "type": "string", "required": True,
             "allowed_values": ["Yes", "No"]},
            {"name": "time_given", "display": "Time Given (minutes)", "type": "integer", "required": False},
            {"name": "negative_marking", "display": "Negative Marking", "type": "string", "required": True,
             "allowed_values": ["Yes", "No"]},
            {"name": "mode", "display": "Mode", "type": "string", "required": True,
             "allowed_values": ["Online", "Offline", "Both"]},
            {"name": "survey_id", "display": "Survey ID", "type": "string", "required": False},
            {"name": "survey_name", "display": "Survey Name", "type": "string", "required": False},
            {"name": "academic_year", "display": "Academic Year", "type": "string", "required": True},
            {"name": "status", "display": "Status", "type": "string", "required": True,
             "allowed_values": ["Draft", "Active", "Inactive", "Archived"]},
            {"name": "report_visibility", "display": "Report Visibility", "type": "string", "required": False,
             "allowed_values": ["Public", "Private", "Restricted"]},
        ]
        return columns

    @staticmethod
    def get_validation_rules() -> List[Dict[str, Any]]:
        """Generate validation rules for Assessment Master sheet."""
        rules = [
            {"sheet": "Assessment Master", "column": "topic_id", "rule": "not_null",
             "severity": "critical", "message": "Topic ID is required"},
            {"sheet": "Assessment Master", "column": "topic_id", "rule": "cross_sheet_consistency",
             "params": {"reference_sheet": "Topic Master", "reference_column": "topic_id"},
             "severity": "critical", "message": "Topic ID must exist in Topic Master sheet"},
            {"sheet": "Assessment Master", "column": "assessment_id", "rule": "not_null",
             "severity": "critical", "message": "Assessment ID is required"},
            {"sheet": "Assessment Master", "column": "assessment_id", "rule": "unique",
             "severity": "critical", "message": "Assessment ID must be unique"},
            {"sheet": "Assessment Master", "column": "assessment_id", "rule": "no_spaces",
             "severity": "critical", "message": "Assessment ID must not contain spaces"},
            {"sheet": "Assessment Master", "column": "assessment_name", "rule": "not_null",
             "severity": "critical", "message": "Assessment Name is required"},
            {"sheet": "Assessment Master", "column": "class_mapping", "rule": "not_null",
             "severity": "critical", "message": "Class Mapping is required"},
            {"sheet": "Assessment Master", "column": "launch_date", "rule": "not_null",
             "severity": "critical", "message": "Launch Date is required"},
            {"sheet": "Assessment Master", "column": "launch_date", "rule": "datetime_format",
             "params": {"format": "%Y-%m-%d"},
             "severity": "critical", "message": "Launch Date must be in YYYY-MM-DD format"},
            {"sheet": "Assessment Master", "column": "close_date", "rule": "not_null",
             "severity": "critical", "message": "Close Date is required"},
            {"sheet": "Assessment Master", "column": "close_date", "rule": "datetime_format",
             "params": {"format": "%Y-%m-%d"},
             "severity": "critical", "message": "Close Date must be in YYYY-MM-DD format"},
            {"sheet": "Assessment Master", "column": "close_date", "rule": "greater_than",
             "params": {"compare_column": "launch_date"},
             "severity": "critical", "message": "Close Date must be after Launch Date"},
            {"sheet": "Assessment Master", "column": "timed_assessment", "rule": "not_null",
             "severity": "critical", "message": "Timed Assessment field is required"},
            {"sheet": "Assessment Master", "column": "time_given", "rule": "conditional_required",
             "params": {"condition_column": "timed_assessment", "condition_value": "Yes"},
             "severity": "critical", "message": "Time Given is required when Timed Assessment is Yes"},
            {"sheet": "Assessment Master", "column": "negative_marking", "rule": "not_null",
             "severity": "critical", "message": "Negative Marking field is required"},
            {"sheet": "Assessment Master", "column": "mode", "rule": "not_null",
             "severity": "critical", "message": "Mode is required"},
            {"sheet": "Assessment Master", "column": "academic_year", "rule": "not_null",
             "severity": "critical", "message": "Academic Year is required"},
            {"sheet": "Assessment Master", "column": "status", "rule": "not_null",
             "severity": "critical", "message": "Status is required"},
        ]
        return rules

    @staticmethod
    def generate_assessment_id(subject: str, class_level: int) -> str:
        """Generate a standardized Assessment ID. e.g. ASSG03, MATG04"""
        from app.rules.curriculum_registry import get_subject_code
        code = get_subject_code(subject)
        return f"{code}G{class_level}"
