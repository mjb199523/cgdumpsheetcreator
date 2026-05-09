"""
Multi-language Content Engine.
Handles language-specific column generation, translation placeholders, and medium mappings.
"""
from typing import List, Dict, Any
from app.config import SUPPORTED_LANGUAGES


class MultiLanguageEngine:
    """Manages multi-language content for dump sheets."""

    def __init__(self, selected_languages: List[str] = None):
        self.languages = selected_languages or SUPPORTED_LANGUAGES

    def generate_language_columns(self, base_column: str) -> List[Dict[str, str]]:
        columns = []
        for lang in self.languages:
            columns.append({
                "name": f"{base_column}_{lang.lower()}",
                "display": f"{base_column.replace('_', ' ').title()} ({lang})",
                "language": lang,
            })
        return columns

    def create_medium_mapping(self) -> Dict[str, str]:
        return {lang: lang for lang in self.languages}

    def populate_language_fields(self, data: Dict[str, Any], base_field: str,
                                  content: str) -> Dict[str, Any]:
        for lang in self.languages:
            key = f"{base_field}_{lang.lower()}"
            data[key] = content  # Same content as placeholder
        return data

    def get_required_language_columns(self) -> List[str]:
        base_fields = ["topic_name", "question_description"]
        cols = []
        for field in base_fields:
            for lang in self.languages:
                cols.append(f"{field}_{lang.lower()}")
        return cols
