"""
Topic Master Sheet Blueprint.
Defines the structure, columns, and validation rules for the Topic Master sheet.
"""
from typing import List, Dict, Any


class TopicMasterBlueprint:
    """Blueprint for the Topic Master sheet."""

    SHEET_NAME = "Topic Master"

    @staticmethod
    def get_columns(languages: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate column definitions dynamically based on selected languages.
        """
        if languages is None:
            languages = ["English", "Assamese", "Hindi"]

        columns = [
            {"name": "topic_id", "display": "Topic ID", "type": "string", "required": True, "unique": True},
            {"name": "topic_name", "display": "Topic Name", "type": "string", "required": True},
        ]

        # Add language-specific columns dynamically
        for lang in languages:
            columns.append({
                "name": f"topic_name_{lang.lower()}",
                "display": f"Topic Name ({lang})",
                "type": "string",
                "required": True,
            })

        columns.extend([
            {"name": "subject", "display": "Subject", "type": "string", "required": True},
            {"name": "class_level", "display": "Class", "type": "integer", "required": True},
            {"name": "mode", "display": "Mode", "type": "string", "required": True,
             "allowed_values": ["Online", "Offline", "Both"]},
            {"name": "academic_year", "display": "Academic Year", "type": "string", "required": True},
            {"name": "status", "display": "Status", "type": "string", "required": False,
             "allowed_values": ["Active", "Inactive", "Draft"]},
        ])

        return columns

    @staticmethod
    def get_validation_rules(languages: List[str] = None) -> List[Dict[str, Any]]:
        """Generate validation rules for Topic Master sheet."""
        if languages is None:
            languages = ["English", "Assamese", "Hindi"]

        rules = [
            {"sheet": "Topic Master", "column": "topic_id", "rule": "not_null",
             "severity": "critical", "message": "Topic ID is required"},
            {"sheet": "Topic Master", "column": "topic_id", "rule": "unique",
             "severity": "critical", "message": "Topic ID must be unique"},
            {"sheet": "Topic Master", "column": "topic_id", "rule": "no_spaces",
             "severity": "critical", "message": "Topic ID must not contain spaces"},
            {"sheet": "Topic Master", "column": "topic_id", "rule": "regex",
             "params": {"pattern": r"^[A-Za-z0-9_]+$"},
             "severity": "critical", "message": "Topic ID must contain only alphanumeric characters and underscores"},
            {"sheet": "Topic Master", "column": "topic_name", "rule": "not_null",
             "severity": "critical", "message": "Topic Name is required"},
            {"sheet": "Topic Master", "column": "subject", "rule": "not_null",
             "severity": "critical", "message": "Subject is required"},
            {"sheet": "Topic Master", "column": "class_level", "rule": "not_null",
             "severity": "critical", "message": "Class is required"},
            {"sheet": "Topic Master", "column": "class_level", "rule": "numeric",
             "severity": "critical", "message": "Class must be numeric"},
            {"sheet": "Topic Master", "column": "mode", "rule": "allowed_values",
             "params": {"values": ["Online", "Offline", "Both"]},
             "severity": "critical", "message": "Mode must be Online, Offline, or Both"},
            {"sheet": "Topic Master", "column": "academic_year", "rule": "not_null",
             "severity": "critical", "message": "Academic Year is required"},
            {"sheet": "Topic Master", "column": "academic_year", "rule": "regex",
             "params": {"pattern": r"^\d{4}-\d{2,4}$"},
             "severity": "warning", "message": "Academic Year should be in format YYYY-YY or YYYY-YYYY"},
        ]

        # Add language-specific validation rules
        for lang in languages:
            col_name = f"topic_name_{lang.lower()}"
            rules.append({
                "sheet": "Topic Master", "column": col_name, "rule": "not_null",
                "severity": "critical", "message": f"Topic Name ({lang}) is required",
            })

        return rules

    @staticmethod
    def generate_topic_id(subject: str, class_level: int, index: int) -> str:
        """Generate a standardized Topic ID. e.g. LANG1G301"""
        from app.rules.curriculum_registry import get_subject_code
        code = get_subject_code(subject)
        return f"{code}G{class_level}{index:02d}"
