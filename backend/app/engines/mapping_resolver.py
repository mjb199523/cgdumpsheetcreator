"""
Mapping Resolver Engine.
Merges question paper data with LO mapping data.

Key logic:
  - Questions are keyed by (subject, class, question_number)
  - LO mappings are keyed by (subject, class, item_id)
  - Match: question_number == item_id within the same subject + class
  - LO mappings are medium-independent (same LO applies across all mediums)
"""
import logging
from typing import List, Dict, Optional
from app.models.schemas import ParsedQuestion, LOMapping, MergedQuestion

logger = logging.getLogger(__name__)


class MappingResolver:
    """Merges parsed questions with LO mappings by matching Question Number to Item ID
    within the same subject + class context."""

    def resolve(self, questions: List[ParsedQuestion], lo_mappings: List[LOMapping],
                medium: str = "") -> Dict:
        """
        Resolve mappings between questions and LO data.

        Matching strategy:
          1. Try exact match by (subject_normalized, class_level, question_number == item_id)
          2. If no subject match, try matching by (class_level, question_number == item_id)
             using the LO's subject to fill in.
          3. Fallback: match by item_id only.

        Returns dict with merged questions, unmatched questions, unmatched LOs,
        and a per-subject breakdown.
        """
        # Build LO lookup: (subject_key, class_level, item_id) → LOMapping
        lo_by_subject_class_id = {}
        lo_by_class_id = {}
        lo_by_id = {}

        for m in lo_mappings:
            subj_key = self._normalize_subject(m.subject)
            lo_by_subject_class_id[(subj_key, m.class_level, m.item_id)] = m
            lo_by_class_id[(m.class_level, m.item_id)] = m
            lo_by_id[m.item_id] = m

        merged = []
        unmatched_questions = []
        matched_lo_keys = set()

        for q in questions:
            lo = None
            match_type = ""
            q_subj_key = self._normalize_subject(q.subject)

            # Strategy 1: exact (subject, class, qnum)
            key1 = (q_subj_key, q.class_level, q.question_number)
            if key1 in lo_by_subject_class_id:
                lo = lo_by_subject_class_id[key1]
                match_type = "exact"
                matched_lo_keys.add(key1)

            # Strategy 2: (class, qnum) — LO subject matches Q's subject range
            if not lo:
                key2 = (q.class_level, q.question_number)
                if key2 in lo_by_class_id:
                    lo = lo_by_class_id[key2]
                    match_type = "class_id"

            # Strategy 3: just item_id
            if not lo:
                if q.question_number in lo_by_id:
                    lo = lo_by_id[q.question_number]
                    match_type = "id_only"

            if lo:
                options_dict = {opt.label: opt.text for opt in q.options}
                subj = q.subject or lo.subject
                cls = q.class_level or lo.class_level
                # Use question's medium if detected, otherwise use the global fallback
                med = q.medium if (q.medium and q.medium != "Auto-Detect") else medium
                if not med:
                    med = "Assamese"  # Ultimate fallback to Assamese if nothing detected or provided

                # Build question ID
                from app.blueprints.question_master import QuestionMasterBlueprint
                q_id = QuestionMasterBlueprint.generate_question_id(subj, cls, q.question_number, med)

                media_type = None
                media_path = None
                if q.image_paths:
                    media_type = "image"
                    media_path = q.image_paths[0]
                elif q.audio_paths:
                    media_type = "audio"
                    media_path = q.audio_paths[0]

                merged.append(MergedQuestion(
                    question_id=q_id, question_number=q.question_number,
                    question_text=q.question_text, options=options_dict,
                    correct_answer=lo.answer_key, learning_outcome=lo.learning_outcome,
                    cognitive_level=lo.cognitive_level, domain=lo.domain, strand=lo.strand,
                    subject=subj, class_level=cls, medium=med,
                    question_type=q.question_type, media_type=media_type,
                    media_file_path=media_path, image_paths=q.image_paths,
                    table_paths=q.table_paths, audio_paths=q.audio_paths,
                ))
            else:
                unmatched_questions.append({
                    "question_number": q.question_number,
                    "subject": q.subject,
                    "class_level": q.class_level,
                })

        # Find unmatched LOs
        all_lo_ids = set()
        for m in lo_mappings:
            all_lo_ids.add(m.item_id)
        matched_qnums = set(mq.question_number for mq in merged)
        unmatched_lo_ids = sorted(all_lo_ids - matched_qnums)

        # Per-subject breakdown
        subject_breakdown = {}
        for mq in merged:
            subj = mq.subject
            if subj not in subject_breakdown:
                subject_breakdown[subj] = {"total": 0, "class_level": mq.class_level}
            subject_breakdown[subj]["total"] += 1

        logger.info(f"Resolved: {len(merged)} merged, {len(unmatched_questions)} unmatched Qs, "
                     f"{len(unmatched_lo_ids)} unmatched LOs")
        logger.info(f"Subject breakdown: {subject_breakdown}")

        return {
            "merged_questions": merged,
            "unmatched_questions": unmatched_questions,
            "unmatched_lo_ids": unmatched_lo_ids,
            "total_questions": len(questions),
            "total_lo_mappings": len(lo_mappings),
            "match_rate": len(merged) / max(len(questions), 1) * 100,
            "subject_breakdown": subject_breakdown,
        }

    @staticmethod
    def _normalize_subject(subject: str) -> str:
        """Normalize a subject name for comparison."""
        if not subject:
            return ""
        # Lowercase, strip, remove common prefixes/suffixes
        s = subject.lower().strip()
        # Remove parenthetical content for fuzzy matching
        # "EVS (The World Around Us)" → "evs"
        # "Language 1 (Assamese)" → "language 1"
        s = s.split("(")[0].strip()
        return s

    @staticmethod
    def _make_subject_code(subject: str) -> str:
        """Create a short code from subject name for IDs."""
        import re
        if not subject:
            return "GEN"
        # Remove parenthetical and clean
        clean = subject.split("(")[0].strip()
        code = re.sub(r'[^A-Za-z0-9]', '', clean).upper()[:3]
        return code or "GEN"
