"""
Pydantic models and schemas for the Assessment Content Operations Platform.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import date, datetime
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────────────────

class AssessmentType(str, Enum):
    SBA = "SBA"
    PAT = "PAT"
    NIPUN = "NIPUN"


class Medium(str, Enum):
    ASSAMESE = "Assamese"
    BENGALI = "Bengali"
    BODO = "Bodo"
    ENGLISH = "English"
    HINDI = "Hindi"
    KARBI = "Karbi"


class CognitiveLevel(str, Enum):
    KNOWLEDGE = "Knowledge"
    UNDERSTANDING = "Understanding"
    APPLICATION = "Application"
    ANALYSIS = "Analysis"
    SYNTHESIS = "Synthesis"
    EVALUATION = "Evaluation"


class ValidationSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestionType(str, Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "True/False"
    FILL_IN_BLANK = "Fill in the Blank"
    SHORT_ANSWER = "Short Answer"
    LONG_ANSWER = "Long Answer"


# ─── Input Schemas ───────────────────────────────────────────────────────────

class ProjectConfig(BaseModel):
    """Configuration for an assessment processing project."""
    project_name: str
    subjects: List[str]
    classes: List[int]
    mediums: List[Medium]
    academic_year: str
    assessment_type: AssessmentType
    launch_date: date
    close_date: date


class UploadedFile(BaseModel):
    """Metadata for an uploaded file."""
    file_id: str
    original_name: str
    file_type: str  # question_paper, lo_mapping, sba_checklist
    file_path: str
    upload_time: datetime
    file_size: int
    status: ProcessingStatus = ProcessingStatus.PENDING


# ─── Parsed Data Schemas ────────────────────────────────────────────────────

class ParsedOption(BaseModel):
    """A single option in a question."""
    label: str  # A, B, C, D
    text: str
    has_media: bool = False
    media_path: Optional[str] = None


class ParsedQuestion(BaseModel):
    """A parsed question from a question paper."""
    question_number: int
    question_id: str = ""
    question_text: str
    options: List[ParsedOption] = []
    question_type: QuestionType = QuestionType.MCQ
    section: Optional[str] = None
    subject: str = ""
    class_level: int = 0
    medium: str = ""
    has_image: bool = False
    image_paths: List[str] = []
    has_table: bool = False
    table_paths: List[str] = []
    has_audio: bool = False
    audio_paths: List[str] = []
    raw_text: str = ""


class LOMapping(BaseModel):
    """A learning outcome mapping entry."""
    item_id: int
    domain: str = ""
    strand: str = ""
    learning_outcome: str = ""
    cognitive_level: str = ""
    answer_key: str = ""
    subject: str = ""
    class_level: int = 0


class MergedQuestion(BaseModel):
    """A fully merged question with LO mapping data."""
    question_id: str
    question_number: int
    question_text: str
    options: Dict[str, str] = {}
    correct_answer: str = ""
    learning_outcome: str = ""
    cognitive_level: str = ""
    domain: str = ""
    strand: str = ""
    subject: str = ""
    class_level: int = 0
    medium: str = ""
    question_type: QuestionType = QuestionType.MCQ
    media_type: Optional[str] = None
    media_file_path: Optional[str] = None
    image_paths: List[str] = []
    table_paths: List[str] = []
    audio_paths: List[str] = []


# ─── Validation Schemas ─────────────────────────────────────────────────────

class ValidationRule(BaseModel):
    """A single validation rule definition."""
    sheet: str
    column: str
    rule: str  # not_null, unique, no_spaces, regex, etc.
    params: Dict[str, Any] = {}
    severity: ValidationSeverity = ValidationSeverity.CRITICAL
    message: Optional[str] = None


class ValidationError(BaseModel):
    """A single validation error instance."""
    sheet: str
    row: int
    column: str
    rule: str
    message: str
    severity: ValidationSeverity
    current_value: Optional[str] = None


class ValidationReport(BaseModel):
    """Complete validation report."""
    total_rules_checked: int = 0
    total_errors: int = 0
    critical_errors: int = 0
    warnings: int = 0
    errors: List[ValidationError] = []
    sheets_validated: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)
    is_valid: bool = True


# ─── Dashboard Schemas ───────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_projects: int = 0
    total_assessments: int = 0
    total_questions_parsed: int = 0
    total_validation_issues: int = 0
    missing_mappings: int = 0
    duplicate_ids: int = 0
    missing_media: int = 0
    missing_translations: int = 0
    recent_exports: List[Dict[str, Any]] = []
    processing_status: Dict[str, int] = {}


# ─── Export Schemas ──────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    """Request to export data."""
    project_id: str
    include_dump_sheet: bool = True
    include_media_zip: bool = False
    include_validation_report: bool = True
    include_error_summary: bool = True
    include_mapping_report: bool = False


class ExportResult(BaseModel):
    """Result of an export operation."""
    export_id: str
    files: List[Dict[str, str]] = []
    timestamp: datetime = Field(default_factory=datetime.now)
    status: ProcessingStatus = ProcessingStatus.COMPLETED


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    username: str
    full_name: str = ""
    role: str = "operator"
