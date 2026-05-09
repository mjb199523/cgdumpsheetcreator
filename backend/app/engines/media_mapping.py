"""
Media Mapping Engine.
Maps extracted media files to questions using naming conventions.
"""
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.config import MEDIA_DIR

logger = logging.getLogger(__name__)


class MediaMappingEngine:
    """Maps media files to their corresponding questions."""

    @staticmethod
    def generate_media_path(subject: str, class_level: int, question_number: int,
                            asset_type: str = "IMG", index: int = 1, ext: str = "png") -> str:
        subj = subject.upper()[:3]
        return f"media/images/{subj}_{class_level}_Q{question_number}_{asset_type}_{index}.{ext}"

    @staticmethod
    def map_media_to_questions(media_files: Dict[str, List[str]],
                                subject: str, class_level: int) -> Dict[int, Dict]:
        mapping = {}
        for category, files in media_files.items():
            media_type = {"images": "image", "tables": "image", "audio": "audio",
                         "documents": "document"}.get(category, "image")
            for fpath in files:
                match = re.search(r'Q(\d+)', Path(fpath).stem)
                if match:
                    q_num = int(match.group(1))
                    if q_num not in mapping:
                        mapping[q_num] = {"media_type": media_type, "media_file_path": fpath}
        return mapping

    @staticmethod
    def validate_media_paths(paths: List[str]) -> Dict[str, bool]:
        results = {}
        for p in paths:
            full = MEDIA_DIR.parent / p if not Path(p).is_absolute() else Path(p)
            results[p] = full.exists()
        return results
