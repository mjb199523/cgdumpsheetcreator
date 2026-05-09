"""
Dump Sheet Generator Engine.
Generates production-ready Excel workbooks matching PAT/NIPUN dump sheet structure.
Uses blueprint-driven architecture — no hardcoded workbook structures.
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import date
from app.models.schemas import MergedQuestion, ProjectConfig
from app.blueprints.topic_master import TopicMasterBlueprint
from app.blueprints.assessment_master import AssessmentMasterBlueprint
from app.blueprints.question_master import QuestionMasterBlueprint
from app.config import OUTPUT_DIR

logger = logging.getLogger(__name__)


class DumpSheetGenerator:
    """Generates complete dump sheet workbooks from merged question data."""

    def __init__(self, config: Optional[ProjectConfig] = None):
        self.config = config
        self.languages = [m.value for m in config.mediums] if config else ["English"]

    def generate(self, merged_questions: List[MergedQuestion],
                 output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate complete dump sheet workbook with all three sheets."""
        if not output_path:
            output_path = str(OUTPUT_DIR / "dump_sheet.xlsx")

        # Transform questions to replicate Language 1 questions across all Target Mediums
        merged_questions = self._transform_questions(merged_questions)

        # Generate data for each sheet
        topic_data = self._generate_topic_master(merged_questions)
        assessment_data = self._generate_assessment_master(merged_questions, topic_data)
        question_data = self._generate_question_master(merged_questions, assessment_data)

        return {
            "topic_master": topic_data,
            "assessment_master": assessment_data,
            "question_master": question_data,
            "output_path": output_path,
        }

    def _transform_questions(self, questions: List[MergedQuestion]) -> List[MergedQuestion]:
        """Apply business rules to replicate questions across mediums."""
        TARGET_MEDIUMS = ["Assamese", "English", "Bodo", "Bengali", "Garo", "Hindi", "Manipuri", "Hmar"]
        
        grouped = {}
        for q in questions:
            key = f"{q.subject}_{q.class_level}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(q)
            
        transformed = []
        
        for key, q_list in grouped.items():
            subject = q_list[0].subject
            class_level = q_list[0].class_level
            subj_lower = subject.lower()
            
            # Language subjects (excluding English)
            lang_1_keys = ["assamese", "bengali", "bodo", "garo", "hindi", "karbi"]
            is_lang_1 = any(k in subj_lower for k in lang_1_keys) and "english" not in subj_lower and "social" not in subj_lower
            
            if is_lang_1:
                # Identify the "Source" questions for this language subject
                # e.g. If subject is Assamese, prioritize Assamese medium paper
                source_qs = [q for q in q_list if 1 <= q.question_number <= 10]
                
                # Deduplicate, prioritizing the medium that matches the subject if possible
                dedup_lang = {}
                # Sort so that matching medium comes first
                sorted_qs = sorted(source_qs, key=lambda x: (
                    0 if (x.medium or "").lower() in subj_lower else 1,
                    x.question_number
                ))
                for q in sorted_qs:
                    if q.question_number not in dedup_lang:
                        dedup_lang[q.question_number] = q
                final_lang_qs = list(dedup_lang.values())[:10]
                
                for med in TARGET_MEDIUMS:
                    for q in final_lang_qs:
                        import copy
                        new_q = copy.deepcopy(q)
                        new_q.medium = med
                        new_q.subject = subject
                        transformed.append(new_q)
                        
            elif "english" in subj_lower and "social" not in subj_lower:
                # English medium gets Q1-10 from English medium paper
                eng_med_qs = [q for q in q_list if "english" in (q.medium or "").lower() and 1 <= q.question_number <= 10]
                if not eng_med_qs:
                    eng_med_qs = [q for q in q_list if 1 <= q.question_number <= 10]
                    
                dedup_eng = {}
                for q in sorted(eng_med_qs, key=lambda x: x.question_number):
                    if q.question_number not in dedup_eng:
                        dedup_eng[q.question_number] = q
                eng_med_qs = list(dedup_eng.values())[:10]
                
                # Other mediums get Q11-20 strictly from Assamese paper
                assamese_med_qs = [q for q in q_list if "assamese" in (q.medium or "").lower() and 11 <= q.question_number <= 20]
                if not assamese_med_qs:
                    assamese_med_qs = [q for q in q_list if 11 <= q.question_number <= 20]
                    
                dedup_other = {}
                for q in sorted(assamese_med_qs, key=lambda x: x.question_number):
                    if q.question_number not in dedup_other:
                        dedup_other[q.question_number] = q
                other_med_qs = list(dedup_other.values())[:10]
                
                for med in TARGET_MEDIUMS:
                    qs_to_copy = eng_med_qs if med.lower() == "english" else other_med_qs
                    if not qs_to_copy:
                        qs_to_copy = other_med_qs if other_med_qs else eng_med_qs
                        
                    for q in qs_to_copy:
                        import copy
                        new_q = copy.deepcopy(q)
                        new_q.medium = med
                        new_q.subject = subject
                        transformed.append(new_q)
                
            else:
                # Core subjects: EVS, Mathematics, Science, Social Science
                valid_q_list = []
                
                if "math" in subj_lower:
                    valid_q_list = [q for q in q_list if 21 <= q.question_number <= 30]
                elif "evs" in subj_lower:
                    valid_q_list = [q for q in q_list if 31 <= q.question_number <= 40]
                elif "social science" in subj_lower or "social" in subj_lower:
                    valid_q_list = [q for q in q_list if 31 <= q.question_number <= 40]
                elif "science" in subj_lower:
                    valid_q_list = [q for q in q_list if 1 <= q.question_number <= 10]
                else:
                    valid_q_list = q_list
                    
                if not valid_q_list:
                    valid_q_list = q_list

                # Group by medium (normalized to lowercase)
                med_groups = {}
                for q in valid_q_list:
                    m_key = (q.medium or "Auto-Detect").lower()
                    if m_key not in med_groups:
                        med_groups[m_key] = []
                    med_groups[m_key].append(q)
                        
                for m in med_groups:
                    dedup_m = {}
                    for q in sorted(med_groups[m], key=lambda x: x.question_number):
                        if q.question_number not in dedup_m:
                            dedup_m[q.question_number] = q
                    med_groups[m] = list(dedup_m.values())
                
                # Identify Assamese fallback (case-insensitive)
                assamese_qs = med_groups.get("assamese", [])
                if not assamese_qs:
                    assamese_qs = valid_q_list[:10]
                
                for med in TARGET_MEDIUMS:
                    m_lower = med.lower()
                    # Specific mapping: Garo, Manipuri, Hmar strictly use Assamese
                    if m_lower in ["garo", "manipuri", "hmar"]:
                        qs_to_copy = assamese_qs
                    else:
                        # Others (Assamese, English, Hindi, Bengali, Bodo) use their own if available
                        if m_lower in med_groups and len(med_groups[m_lower]) > 0:
                            qs_to_copy = med_groups[m_lower][:10]
                        else:
                            qs_to_copy = assamese_qs
                        
                    for q in qs_to_copy:
                        import copy
                        new_q = copy.deepcopy(q)
                        new_q.medium = med
                        transformed.append(new_q)

        # Sort the final list to meet Dumpsheet Structure logic:
        # Grade 3-5 vs 6-8, then class, subject, medium order
        def get_grade_group(c):
            return 1 if 3 <= c <= 5 else 2 if 6 <= c <= 8 else 3

        transformed.sort(key=lambda x: (
            get_grade_group(x.class_level),
            x.class_level,
            x.subject,
            TARGET_MEDIUMS.index(x.medium) if x.medium in TARGET_MEDIUMS else 99,
            x.question_number
        ))
                
        return transformed

    def _generate_topic_master(self, questions: List[MergedQuestion]) -> List[Dict[str, Any]]:
        """Generate Topic Master sheet data."""
        topics = {}
        for q in questions:
            key = f"{q.subject}_{q.class_level}"
            if key not in topics:
                topic_id = TopicMasterBlueprint.generate_topic_id(q.subject, q.class_level, len(topics) + 1)
                topic = {
                    "topic_id": topic_id,
                    "topic_name": f"{q.subject} Class {q.class_level} Assessment",
                    "subject": q.subject,
                    "class_level": q.class_level,
                    "mode": "Online",
                    "academic_year": self.config.academic_year if self.config else "2025-26",
                    "status": "Active",
                }
                for lang in self.languages:
                    topic[f"topic_name_{lang.lower()}"] = topic["topic_name"]
                topics[key] = topic
        return list(topics.values())

    def _generate_assessment_master(self, questions: List[MergedQuestion],
                                     topic_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate Assessment Master sheet data."""
        topic_map = {}
        for t in topic_data:
            key = f"{t['subject']}_{t['class_level']}"
            topic_map[key] = t["topic_id"]

        assessments = {}
        for q in questions:
            key = f"{q.subject}_{q.class_level}"
            if key not in assessments:
                topic_id = topic_map.get(key, "")
                atype = self.config.assessment_type.value if self.config else "PAT"
                assessment_id = AssessmentMasterBlueprint.generate_assessment_id(
                    q.subject, q.class_level)
                assessments[key] = {
                    "topic_id": topic_id,
                    "assessment_id": assessment_id,
                    "assessment_name": f"{q.subject} Class {q.class_level} {atype}",
                    "assessment_description": f"{atype} assessment for {q.subject} Class {q.class_level}",
                    "class_mapping": str(q.class_level),
                    "multiple_entry_config": "No",
                    "stream": "",
                    "launch_date": str(self.config.launch_date) if self.config else str(date.today()),
                    "close_date": str(self.config.close_date) if self.config else str(date.today()),
                    "timed_assessment": "No",
                    "time_given": "",
                    "negative_marking": "No",
                    "mode": "Online",
                    "survey_id": "",
                    "survey_name": "",
                    "academic_year": self.config.academic_year if self.config else "2025-26",
                    "status": "Draft",
                    "report_visibility": "Public",
                    "_subject": q.subject,
                }
        return list(assessments.values())

    def _generate_question_master(self, questions: List[MergedQuestion],
                                   assessment_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate Generic Question Master Table data."""
        assessment_map = {}
        for a in assessment_data:
            key = f"{a.get('_subject', '')}_{a['class_mapping']}"
            assessment_map[key] = a["assessment_id"]

        rows = []
        for idx, q in enumerate(questions, 1):
            key = f"{q.subject}_{q.class_level}"
            assessment_id = assessment_map.get(key, "")
            medium = q.medium or (self.languages[0] if self.languages else "English")

            row = {
                "serial_number": idx,
                "assessment_id": assessment_id,
                "medium": medium,
                "medium_in_english": medium,
                "question_id": q.question_id,
                "question_type": q.question_type.value if hasattr(q.question_type, 'value') else q.question_type,
                "text_input_type": "",
                "text_limit_character": "",
                "question_description": q.question_text,
                "question_description_english": q.question_text,
                "media_type": q.media_type or "",
                "media_file_path": q.media_file_path or "",
                "correct_answer": q.correct_answer,
                "min_numeric_input": "",
                "max_numeric_input": "",
                "outcome_description": "",
                "domain": q.domain,
                "strand": q.strand,
                "learning_outcome": q.learning_outcome,
                "cognitive_level": q.cognitive_level,
                "mode": "Online",
                "academic_year": self.config.academic_year if self.config else "2025-26",
            }

            # Add language columns
            for lang in self.languages:
                row[f"question_description_{lang.lower()}"] = q.question_text

            # Add options (up to 20)
            option_labels = sorted(q.options.keys()) if q.options else []
            for i in range(1, 21):
                if i <= len(option_labels):
                    row[f"option_{i}"] = q.options.get(option_labels[i - 1], "")
                else:
                    row[f"option_{i}"] = ""

            rows.append(row)

        return rows
