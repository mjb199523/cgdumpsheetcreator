"""
Naming convention utilities.
Standardized naming for IDs, files, and media assets.
"""


def generate_subject_code(subject: str) -> str:
    """Generate 3-letter subject code."""
    mapping = {
        "english": "ENG", "mathematics": "MAT", "math": "MAT", "maths": "MAT",
        "science": "SCI", "social science": "SSC", "social studies": "SST",
        "hindi": "HIN", "assamese": "ASM", "environmental studies": "EVS",
        "evs": "EVS", "general knowledge": "GKN", "computer": "COM",
    }
    return mapping.get(subject.lower(), subject.upper()[:3])


def generate_topic_id(subject: str, class_level: int, index: int = 1) -> str:
    code = generate_subject_code(subject)
    return f"{code}_{class_level}_TOPIC_{index:03d}"


def generate_assessment_id(subject: str, class_level: int,
                           assessment_type: str, index: int = 1) -> str:
    code = generate_subject_code(subject)
    atype = assessment_type.upper()[:3]
    return f"{code}_{class_level}_{atype}_{index:03d}"


def generate_question_id(subject: str, class_level: int,
                         question_number: int, medium: str = "") -> str:
    code = generate_subject_code(subject)
    if medium:
        med = medium.upper()[:3]
        return f"{code}_{class_level}_{med}_Q{question_number:03d}"
    return f"{code}_{class_level}_Q{question_number:03d}"


def generate_media_filename(subject: str, class_level: int,
                            question_number: int, asset_type: str = "IMG",
                            index: int = 1, ext: str = "png") -> str:
    """
    Generate media filename following convention:
    SUBJECT_CLASS_QUESTION_ASSETTYPE_INDEX.ext
    e.g., ENG_5_Q31_IMG_1.png
    """
    code = generate_subject_code(subject)
    return f"{code}_{class_level}_Q{question_number}_{asset_type}_{index}.{ext}"
