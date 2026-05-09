"""
Curriculum Registry — defines valid Medium → Class → Subject mappings
and Subject → Class Q-number ranges.

This is the master config that the platform uses to validate uploads
and auto-tag questions to subjects based on question number ranges.
"""

# ─── Medium → Class → Subjects with Q-number ranges ─────────────────────────
# Each question paper PDF = 1 medium + 1 class + multiple subjects inside.
# The Q-number ranges define which question numbers belong to which subject.

DEFAULT_SUBJECT_RANGES = {
    3: [
        {"subject": "Language 1", "start": 1, "end": 10},
        {"subject": "Language 2 (English)", "start": 11, "end": 20},
        {"subject": "Mathematics", "start": 21, "end": 30},
        {"subject": "EVS (The World Around Us)", "start": 31, "end": 40},
    ],
    4: [
        {"subject": "Language 1", "start": 1, "end": 10},
        {"subject": "Language 2 (English)", "start": 11, "end": 20},
        {"subject": "Mathematics", "start": 21, "end": 30},
        {"subject": "EVS (The World Around Us)", "start": 31, "end": 40},
    ],
    5: [
        {"subject": "Language 1", "start": 1, "end": 10},
        {"subject": "Language 2 (English)", "start": 11, "end": 20},
        {"subject": "Mathematics", "start": 21, "end": 30},
        {"subject": "EVS (The World Around Us)", "start": 31, "end": 40},
    ],
}

# Language 1 name per medium (the rest are common across mediums)
LANGUAGE_1_NAME = {
    "Assamese": "Assamese",
    "Bengali": "Bengali",
    "Bodo": "Bodo",
    "English": "English",
    "Hindi": "Hindi",
    "Karbi": "Karbi",
}

# All supported mediums
SUPPORTED_MEDIUMS = list(LANGUAGE_1_NAME.keys())

# ─── LO Mapping Subjects (subject-wise, class-wise) ────────────────────────
# LO files are organized per subject per class (medium-independent).
LO_SUBJECTS = [
    "Language 1",
    "Language 2 (English)",
    "Mathematics",
    "EVS (The World Around Us)",
]

# ─── Subject Short Codes for ID generation ──────────────────────────────────
# Used in Assessment ID, Question ID, etc.  e.g. LANG1G301
SUBJECT_CODES = {
    "assamese": "ASSM",
    "bengali": "BENG",
    "bodo": "BODO",
    "english": "ENGL",
    "hindi": "HIND",
    "karbi": "KARB",
    "garo": "GARO",
    "language 1": "LANG1",
    "language 2": "LANG2",
    "language 2 (english)": "LANG2",
    "mathematics": "MATH",
    "evs": "EVS",
    "evs (the world around us)": "EVS",
    "science": "SCI",
    "social science": "SSC",
    "general knowledge": "GK",
    "computer": "COMP",
}


def get_subject_code(subject: str) -> str:
    """Get short code for a subject. e.g. 'Language 1 (Assamese)' → 'LANG1'."""
    if not subject:
        return "GEN"
    s = subject.lower().strip()
    # Direct match
    if s in SUBJECT_CODES:
        return SUBJECT_CODES[s]
    # Try matching without parenthetical
    base = s.split("(")[0].strip()
    if base in SUBJECT_CODES:
        return SUBJECT_CODES[base]
    # Partial match
    for key, code in SUBJECT_CODES.items():
        if key in s or s in key:
            return code
    # Fallback: first 4 chars uppercase
    import re
    clean = re.sub(r'[^a-z0-9]', '', s)
    return clean[:4].upper() or "GEN"


def get_subject_ranges(class_level: int, medium: str = "") -> list:
    """
    Get the subject → Q-number range mapping for a given class.
    Replaces 'Language 1' with the actual medium language name.
    """
    ranges = DEFAULT_SUBJECT_RANGES.get(class_level, [])
    if not ranges:
        return []

    result = []
    lang1_name = LANGUAGE_1_NAME.get(medium, medium) if medium else "Language 1"
    for r in ranges:
        entry = dict(r)
        if entry["subject"] == "Language 1":
            entry["subject_display"] = f"Language 1 ({lang1_name})"
        else:
            entry["subject_display"] = entry["subject"]
        result.append(entry)
    return result


def get_subject_for_question(question_number: int, class_level: int, medium: str = "") -> str:
    """
    Given a question number, class level, and medium,
    return the subject that question belongs to.
    """
    ranges = get_subject_ranges(class_level, medium)
    for r in ranges:
        if r["start"] <= question_number <= r["end"]:
            return r["subject_display"]
    return "Unknown"


def get_subjects_for_class(class_level: int, medium: str = "") -> list:
    """Get list of subjects for a class+medium combo."""
    ranges = get_subject_ranges(class_level, medium)
    return [r["subject_display"] for r in ranges]
