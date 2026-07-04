import re
from typing import List
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]
    score: float  # 0-1


class HypothesisValidator:
    """
    Validador de hipóteses científicas.

    Verifica falsificabilidade, testabilidade, especificidade e operacionalização.
    """

    def __init__(self):
        self._patterns = {
            "falsifiable": [
                r"(if|when|under|given).*(then|will|should)",
                r"(increases|decreases|affects|changes)",
                r"(greater|less|higher|lower|different)",
            ],
            "testable": [
                r"(measured|observed|calculated|detected)",
                r"(data|sample|test|experiment)",
                r"(statistically|significantly)",
            ],
            "specific": [
                r"(specifically|exactly|precisely)",
                r"(between|among|within)",
            ],
        }

    def validate(self, formulation: str) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        score = 0.0

        falsifiable = any(
            re.search(p, formulation, re.IGNORECASE) for p in self._patterns["falsifiable"]
        )
        if not falsifiable:
            errors.append("Hypothesis is not falsifiable")
        else:
            score += 0.3

        testable = any(
            re.search(p, formulation, re.IGNORECASE) for p in self._patterns["testable"]
        )
        if not testable:
            errors.append("Hypothesis is not testable")
        else:
            score += 0.3

        specific = any(
            re.search(p, formulation, re.IGNORECASE) for p in self._patterns["specific"]
        )
        if not specific:
            warnings.append("Hypothesis lacks specificity")
        else:
            score += 0.2

        if len(formulation.split()) < 10:
            warnings.append("Hypothesis is too short")
        else:
            score += 0.1

        has_conditions = any(
            w in formulation.lower() for w in ["when", "if", "under", "given", "with"]
        )
        if not has_conditions:
            warnings.append("Hypothesis should mention variables/conditions")
        else:
            score += 0.1

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=min(score, 1.0),
        )
