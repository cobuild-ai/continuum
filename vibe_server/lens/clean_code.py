"""Clean Code Lens — Robert C. Martin principles, SRP, DRY, expressive naming."""
import re
from vibe_server.core.models import FindingItem, LensCategory, LensEvaluation, Severity


class CleanCodeLens:
    """Evaluates proposed changes against Clean Code principles."""

    def evaluate(self, prompt: str, target_files: list[str] = None) -> LensEvaluation:
        findings: list[FindingItem] = []
        recommendations: list[str] = []
        score = 100

        # Pattern: monolithic mixing, lack of single responsibility
        if re.search(r"(everything in one file|god object|huge function)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.CLEAN_CODE,
                severity=Severity.HIGH,
                principle_violated="Single Responsibility Principle (SRP)",
                description="Prompt requests monolithic code or excessive responsibilities in a single unit.",
                suggestion="Decompose responsibilities into focused, single-purpose classes and functions."
            ))
            recommendations.append("Decompose responsibilities into dedicated domain modules.")
            score -= 35

        # Pattern: bypassing clean naming or quick dirty hacks
        if re.search(r"(quick hack|dirty code|ugly fix|ignore style)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.CLEAN_CODE,
                severity=Severity.MEDIUM,
                principle_violated="Expressive Naming & Cleanliness",
                description="Prompt suggests unmaintainable temporary hacks or dirty patterns.",
                suggestion="Refactor with expressive naming and maintainable abstractions."
            ))
            recommendations.append("Follow standard naming conventions and self-documenting code.")
            score -= 25

        passed = score >= 70
        return LensEvaluation(
            category=LensCategory.CLEAN_CODE,
            lens_name="Clean Code Lens",
            passed=passed,
            score=score,
            findings=findings,
            recommendations=recommendations
        )
