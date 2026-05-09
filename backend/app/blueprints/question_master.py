"""
Generic Question Master Table Blueprint.
Defines the structure, columns, and validation rules for the Question Master sheet.
"""
from typing import List, Dict, Any


class QuestionMasterBlueprint:
    """Blueprint for the Generic Question Master Table sheet."""

    SHEET_NAME = "Generic Question Master Table"
    MAX_OPTIONS = 20

    @staticmethod
    def get_columns(languages: List[str] = None, max_options: int = 20) -> List[Dict[str, Any]]:
        """Generate column definitions dynamically based on languages and option count."""
        if languages is None:
            languages = ["English", "Assamese", "Hindi"]

        columns = [
            {"name": "serial_number", "display": "Serial Number", "type": "integer", "required": True},
            {"name": "assessment_id", "display": "Assessment ID", "type": "string", "required": True},
            {"name": "medium", "display": "Medium", "type": "string", "required": True,
             "allowed_values": languages},
            {"name": "medium_in_english", "display": "Medium in English", "type": "string", "required": True},
            {"name": "question_id", "display": "Question ID", "type": "string", "required": True, "unique": True},
            {"name": "question_type", "display": "Question Type", "type": "string", "required": True,
             "allowed_values": ["MCQ", "True/False", "Fill in the Blank", "Short Answer", "Long Answer"]},
            {"name": "text_input_type", "display": "text_input_type", "type": "string", "required": False},
            {"name": "text_limit_character", "display": "text_limit_character", "type": "integer", "required": False},
            {"name": "question_description", "display": "Question Description", "type": "string", "required": True},
        ]

        # Add language-specific question description columns
        for lang in languages:
            if lang.lower() == "english":
                continue
            columns.append({
                "name": f"question_description_{lang.lower()}",
                "display": f"Question Description ({lang})",
                "type": "string",
                "required": True,
            })

        columns.append(
            {"name": "question_description_english", "display": "Question Description in English",
             "type": "string", "required": True}
        )

        columns.extend([
            {"name": "media_type", "display": "media_type", "type": "string", "required": False,
             "allowed_values": ["image", "audio", "video", "document", ""]},
            {"name": "media_file_path", "display": "media_file_path", "type": "string", "required": False},
            {"name": "correct_answer", "display": "correct_answer", "type": "string", "required": True},
            {"name": "min_numeric_input", "display": "min_numeric_input", "type": "numeric", "required": False},
            {"name": "max_numeric_input", "display": "max_numeric_input", "type": "numeric", "required": False},
        ])

        # Add option columns (option_1 through option_N)
        for i in range(1, max_options + 1):
            columns.append({
                "name": f"option_{i}",
                "display": f"option_{i}",
                "type": "string",
                "required": i <= 4,  # First 4 options are required for MCQ
            })

        # Add outcome and classification columns
        columns.extend([
            {"name": "outcome_description", "display": "Outcome Description", "type": "string", "required": False},
            {"name": "domain", "display": "Domain", "type": "string", "required": True},
            {"name": "strand", "display": "Strand", "type": "string", "required": True},
            {"name": "learning_outcome", "display": "Learning Outcome", "type": "string", "required": True},
            {"name": "cognitive_level", "display": "Cognitive Level", "type": "string", "required": True,
             "allowed_values": ["Knowledge", "Understanding", "Application", "Analysis", "Synthesis", "Evaluation"]},
            {"name": "mode", "display": "Mode", "type": "string", "required": True,
             "allowed_values": ["Online", "Offline", "Both"]},
            {"name": "academic_year", "display": "academic_year", "type": "string", "required": True},
        ])

        return columns

    @staticmethod
    def get_validation_rules(languages: List[str] = None) -> List[Dict[str, Any]]:
        """Generate validation rules for Question Master Table."""
        if languages is None:
            languages = ["English", "Assamese", "Hindi"]

        rules = [
            {"sheet": "Generic Question Master Table", "column": "serial_number", "rule": "not_null",
             "severity": "critical", "message": "Serial Number is required"},
            {"sheet": "Generic Question Master Table", "column": "serial_number", "rule": "numeric",
             "severity": "critical", "message": "Serial Number must be numeric"},
            {"sheet": "Generic Question Master Table", "column": "assessment_id", "rule": "not_null",
             "severity": "critical", "message": "Assessment ID is required"},
            {"sheet": "Generic Question Master Table", "column": "assessment_id", "rule": "cross_sheet_consistency",
             "params": {"reference_sheet": "Assessment Master", "reference_column": "assessment_id"},
             "severity": "critical", "message": "Assessment ID must exist in Assessment Master sheet"},
            {"sheet": "Generic Question Master Table", "column": "medium", "rule": "not_null",
             "severity": "critical", "message": "Medium is required"},
            {"sheet": "Generic Question Master Table", "column": "question_id", "rule": "not_null",
             "severity": "critical", "message": "Question ID is required"},
            {"sheet": "Generic Question Master Table", "column": "question_id", "rule": "unique",
             "severity": "critical", "message": "Question ID must be unique"},
            {"sheet": "Generic Question Master Table", "column": "question_id", "rule": "no_spaces",
             "severity": "critical", "message": "Question ID must not contain spaces"},
            {"sheet": "Generic Question Master Table", "column": "question_type", "rule": "not_null",
             "severity": "critical", "message": "Question Type is required"},
            {"sheet": "Generic Question Master Table", "column": "question_description", "rule": "not_null",
             "severity": "critical", "message": "Question Description is required"},
            {"sheet": "Generic Question Master Table", "column": "correct_answer", "rule": "not_null",
             "severity": "critical", "message": "Correct Answer is required"},
            {"sheet": "Generic Question Master Table", "column": "domain", "rule": "not_null",
             "severity": "critical", "message": "Domain is required"},
            {"sheet": "Generic Question Master Table", "column": "strand", "rule": "not_null",
             "severity": "critical", "message": "Strand is required"},
            {"sheet": "Generic Question Master Table", "column": "learning_outcome", "rule": "not_null",
             "severity": "critical", "message": "Learning Outcome is required"},
            {"sheet": "Generic Question Master Table", "column": "cognitive_level", "rule": "not_null",
             "severity": "critical", "message": "Cognitive Level is required"},
            {"sheet": "Generic Question Master Table", "column": "mode", "rule": "not_null",
             "severity": "critical", "message": "Mode is required"},
            {"sheet": "Generic Question Master Table", "column": "academic_year", "rule": "not_null",
             "severity": "critical", "message": "Academic Year is required"},
            # Media validation
            {"sheet": "Generic Question Master Table", "column": "media_file_path", "rule": "conditional_required",
             "params": {"condition_column": "media_type", "condition_value": "image"},
             "severity": "critical", "message": "Media file path required when media type is set"},
            {"sheet": "Generic Question Master Table", "column": "media_file_path",
             "rule": "supported_media_formats",
             "params": {"formats": [".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4", ".wav"]},
             "severity": "warning", "message": "Media file must be in a supported format"},
        ]

        # Add language-specific rules
        for lang in languages:
            if lang.lower() == "english":
                continue
            col_name = f"question_description_{lang.lower()}"
            rules.append({
                "sheet": "Generic Question Master Table", "column": col_name,
                "rule": "language_required",
                "params": {"language": lang},
                "severity": "warning",
                "message": f"Question Description ({lang}) should be provided for multilingual support",
            })

        return rules

    @staticmethod
    def generate_question_id(subject: str, class_level: int, question_number: int, medium: str = "") -> str:
        """Generate a standardized Question ID. e.g. LANG1G301_Q001"""
        from app.rules.curriculum_registry import get_subject_code
        code = get_subject_code(subject)
        # Using 01 as a placeholder for assessment index
        return f"{code}G{class_level}01_Q{question_number:03d}"
