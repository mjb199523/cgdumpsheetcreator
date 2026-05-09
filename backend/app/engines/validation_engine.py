"""
Guardrail Validation Engine.
Rule-based, deterministic validation against SBA guardrails.
NO AI — all logic is config-driven.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import ValidationRule, ValidationError, ValidationReport, ValidationSeverity

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Deterministic rule-based validation engine."""

    def __init__(self):
        self.rule_handlers = {
            "not_null": self._check_not_null,
            "unique": self._check_unique,
            "no_spaces": self._check_no_spaces,
            "regex": self._check_regex,
            "numeric": self._check_numeric,
            "allowed_values": self._check_allowed_values,
            "datetime_format": self._check_datetime_format,
            "greater_than": self._check_greater_than,
            "conditional_required": self._check_conditional_required,
            "language_required": self._check_language_required,
            "cross_sheet_consistency": self._check_cross_sheet,
            "file_size_limit": self._check_file_size,
            "supported_media_formats": self._check_media_formats,
        }

    def validate(self, data: Dict[str, List[Dict[str, Any]]],
                 rules: List[Dict[str, Any]]) -> ValidationReport:
        """
        Validate data against rules.
        data: {sheet_name: [row_dicts]}
        rules: list of rule definitions
        """
        errors = []
        total_rules = 0

        for rule_def in rules:
            sheet = rule_def.get("sheet", "")
            column = rule_def.get("column", "")
            rule_type = rule_def.get("rule", "")
            params = rule_def.get("params", {})
            severity = ValidationSeverity(rule_def.get("severity", "critical"))
            message = rule_def.get("message", f"Validation failed: {rule_type} on {column}")

            sheet_data = data.get(sheet, [])
            if not sheet_data:
                continue

            handler = self.rule_handlers.get(rule_type)
            if not handler:
                logger.warning(f"Unknown rule type: {rule_type}")
                continue

            total_rules += 1

            if rule_type == "unique":
                errs = self._check_unique(sheet_data, sheet, column, severity, message)
                errors.extend(errs)
            elif rule_type == "cross_sheet_consistency":
                errs = self._check_cross_sheet(sheet_data, data, sheet, column, params, severity, message)
                errors.extend(errs)
            else:
                for row_idx, row in enumerate(sheet_data, 1):
                    val = row.get(column)
                    err = handler(val, row, sheet, column, row_idx, params, severity, message)
                    if err:
                        errors.append(err)

        critical = sum(1 for e in errors if e.severity == ValidationSeverity.CRITICAL)
        warnings = sum(1 for e in errors if e.severity == ValidationSeverity.WARNING)

        return ValidationReport(
            total_rules_checked=total_rules, total_errors=len(errors),
            critical_errors=critical, warnings=warnings, errors=errors,
            sheets_validated=list(data.keys()), is_valid=critical == 0,
        )

    # ─── Rule Handlers ──────────────────────────────────────────────────

    def _check_not_null(self, val, row, sheet, col, row_idx, params, severity, msg):
        if val is None or str(val).strip() == "":
            return ValidationError(sheet=sheet, row=row_idx, column=col, rule="not_null",
                                   message=msg, severity=severity, current_value=str(val) if val else "")
        return None

    def _check_unique(self, data, sheet, col, severity, msg):
        errors = []
        seen = {}
        for idx, row in enumerate(data, 1):
            val = row.get(col)
            if val is None or str(val).strip() == "":
                continue
            key = str(val).strip()
            if key in seen:
                errors.append(ValidationError(sheet=sheet, row=idx, column=col, rule="unique",
                    message=f"{msg} (duplicate of row {seen[key]})", severity=severity, current_value=key))
            else:
                seen[key] = idx
        return errors

    def _check_no_spaces(self, val, row, sheet, col, row_idx, params, severity, msg):
        if val and " " in str(val):
            return ValidationError(sheet=sheet, row=row_idx, column=col, rule="no_spaces",
                                   message=msg, severity=severity, current_value=str(val))
        return None

    def _check_regex(self, val, row, sheet, col, row_idx, params, severity, msg):
        if val and not re.match(params.get("pattern", ""), str(val)):
            return ValidationError(sheet=sheet, row=row_idx, column=col, rule="regex",
                                   message=msg, severity=severity, current_value=str(val))
        return None

    def _check_numeric(self, val, row, sheet, col, row_idx, params, severity, msg):
        if val is not None and str(val).strip() != "":
            try:
                float(str(val))
            except ValueError:
                return ValidationError(sheet=sheet, row=row_idx, column=col, rule="numeric",
                                       message=msg, severity=severity, current_value=str(val))
        return None

    def _check_allowed_values(self, val, row, sheet, col, row_idx, params, severity, msg):
        allowed = params.get("values", [])
        if val and str(val).strip() not in allowed:
            return ValidationError(sheet=sheet, row=row_idx, column=col, rule="allowed_values",
                message=f"{msg}. Allowed: {allowed}", severity=severity, current_value=str(val))
        return None

    def _check_datetime_format(self, val, row, sheet, col, row_idx, params, severity, msg):
        fmt = params.get("format", "%Y-%m-%d")
        if val:
            try:
                datetime.strptime(str(val).strip(), fmt)
            except ValueError:
                return ValidationError(sheet=sheet, row=row_idx, column=col, rule="datetime_format",
                                       message=msg, severity=severity, current_value=str(val))
        return None

    def _check_greater_than(self, val, row, sheet, col, row_idx, params, severity, msg):
        compare_col = params.get("compare_column", "")
        compare_val = row.get(compare_col)
        if val and compare_val:
            try:
                if str(val).strip() <= str(compare_val).strip():
                    return ValidationError(sheet=sheet, row=row_idx, column=col, rule="greater_than",
                                           message=msg, severity=severity, current_value=str(val))
            except Exception:
                pass
        return None

    def _check_conditional_required(self, val, row, sheet, col, row_idx, params, severity, msg):
        cond_col = params.get("condition_column", "")
        cond_val = params.get("condition_value", "")
        if str(row.get(cond_col, "")).strip() == cond_val:
            if val is None or str(val).strip() == "":
                return ValidationError(sheet=sheet, row=row_idx, column=col, rule="conditional_required",
                                       message=msg, severity=severity, current_value="")
        return None

    def _check_language_required(self, val, row, sheet, col, row_idx, params, severity, msg):
        if val is None or str(val).strip() == "":
            return ValidationError(sheet=sheet, row=row_idx, column=col, rule="language_required",
                                   message=msg, severity=severity, current_value="")
        return None

    def _check_cross_sheet(self, data, all_data, sheet, col, params, severity, msg):
        errors = []
        ref_sheet = params.get("reference_sheet", "")
        ref_col = params.get("reference_column", "")
        ref_data = all_data.get(ref_sheet, [])
        ref_values = {str(r.get(ref_col, "")).strip() for r in ref_data if r.get(ref_col)}
        for idx, row in enumerate(data, 1):
            val = row.get(col)
            if val and str(val).strip() not in ref_values:
                errors.append(ValidationError(sheet=sheet, row=idx, column=col, rule="cross_sheet_consistency",
                    message=f"{msg} ('{val}' not found in {ref_sheet}.{ref_col})",
                    severity=severity, current_value=str(val)))
        return errors

    def _check_file_size(self, val, row, sheet, col, row_idx, params, severity, msg):
        return None  # Checked externally

    def _check_media_formats(self, val, row, sheet, col, row_idx, params, severity, msg):
        formats = params.get("formats", [])
        if val and str(val).strip():
            ext = "." + str(val).split(".")[-1].lower() if "." in str(val) else ""
            if ext and ext not in formats:
                return ValidationError(sheet=sheet, row=row_idx, column=col, rule="supported_media_formats",
                                       message=msg, severity=severity, current_value=str(val))
        return None
