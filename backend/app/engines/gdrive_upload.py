"""
Google Drive Upload Engine (MVP v2 - Stub).
Provides interface for uploading media to Google Drive and generating shareable URLs.
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class GDriveUploadEngine:
    """Handles Google Drive upload operations. Full implementation in MVP v2."""

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path
        self.is_configured = False

    def configure(self, credentials_path: str) -> bool:
        self.credentials_path = credentials_path
        self.is_configured = True
        logger.info("Google Drive configured (stub)")
        return True

    def upload_folder(self, local_path: str, drive_folder_name: str = "") -> Dict:
        if not self.is_configured:
            return {"status": "not_configured", "message": "Google Drive not configured. Available in MVP v2."}
        return {"status": "stub", "message": "Google Drive upload will be available in MVP v2."}

    def get_shareable_url(self, file_id: str) -> str:
        return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

    def replace_local_paths_with_urls(self, data: List[Dict], url_map: Dict[str, str]) -> List[Dict]:
        for row in data:
            path = row.get("media_file_path", "")
            if path and path in url_map:
                row["media_file_path"] = url_map[path]
        return data
