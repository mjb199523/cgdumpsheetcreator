"""
Media Extraction Engine.
Extracts images, tables, audio, and documents from question papers.
Saves media into structured folders and returns path mappings.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from app.config import MEDIA_DIR

logger = logging.getLogger(__name__)


class MediaExtractionEngine:
    """Extracts and manages media files from question papers."""

    def __init__(self):
        self.extracted_files = {"images": [], "tables": [], "audio": [], "documents": []}

    def extract_from_pdf(self, file_path: str, subject: str, class_level: int) -> Dict[str, List[str]]:
        """Extract all media from a PDF file."""
        file_path = Path(file_path)
        try:
            import fitz
            doc = fitz.open(str(file_path))
            img_counter = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                for img in page.get_images(full=True):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    if base_image:
                        img_counter += 1
                        ext = base_image.get("ext", "png")
                        subj = subject.upper()[:3]
                        fname = f"{subj}_{class_level}_Q{page_num + 1}_IMG_{img_counter}.{ext}"
                        path = MEDIA_DIR / "images" / fname
                        with open(path, "wb") as f:
                            f.write(base_image["image"])
                        rel_path = f"media/images/{fname}"
                        self.extracted_files["images"].append(rel_path)
            doc.close()
        except Exception as e:
            logger.error(f"Media extraction error: {e}")
        return self.extracted_files

    def extract_from_docx(self, file_path: str, subject: str, class_level: int) -> Dict[str, List[str]]:
        """Extract all media from a DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            img_counter = 0
            for rel in doc.part.rels.values():
                if "image" in rel.reltype:
                    img_counter += 1
                    blob = rel.target_part.blob
                    ext = os.path.splitext(rel.target_ref)[1] or ".png"
                    subj = subject.upper()[:3]
                    fname = f"{subj}_{class_level}_IMG_{img_counter}{ext}"
                    path = MEDIA_DIR / "images" / fname
                    with open(path, "wb") as f:
                        f.write(blob)
                    self.extracted_files["images"].append(f"media/images/{fname}")
        except Exception as e:
            logger.error(f"DOCX media extraction error: {e}")
        return self.extracted_files

    def get_media_mapping(self, questions_count: int, subject: str,
                          class_level: int) -> Dict[int, Dict[str, str]]:
        """Generate media path mapping for questions."""
        mapping = {}
        for img_path in self.extracted_files.get("images", []):
            fname = Path(img_path).stem
            # Try to extract question number from filename
            import re
            match = re.search(r'Q(\d+)', fname)
            if match:
                q_num = int(match.group(1))
                if q_num not in mapping:
                    mapping[q_num] = {"media_type": "image", "media_file_path": img_path}
        return mapping

    def get_all_extracted(self) -> Dict[str, List[str]]:
        return self.extracted_files

    def reset(self):
        self.extracted_files = {"images": [], "tables": [], "audio": [], "documents": []}
