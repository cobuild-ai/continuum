"""AI Conduct Lens — Detects fake mocks, hardcoding, stubs, and silent exception swallowing."""
import re
from vibe_server.core.models import FindingItem, LensCategory, LensEvaluation, Severity


class AIConductLens:
    """Evaluates proposed changes against AI hallucination, stubs, and fake mock anti-patterns."""

    def evaluate(self, prompt: str, target_files: list[str] = None) -> LensEvaluation:
        findings: list[FindingItem] = []
        recommendations: list[str] = []
        score = 100

        # Pattern: fake mock data instead of real implementation
        if re.search(r"(fake response|mock data for now|hardcoded mock|placeholder return)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.AI_CONDUCT,
                severity=Severity.HIGH,
                principle_violated="Zero Fake Protocol",
                description="AI anti-pattern: Requesting fabricated mock data instead of authentic logic.",
                suggestion="Implement genuine logic or admit unknown state explicitly (Truth-First)."
            ))
            recommendations.append("Strictly follow Zero Fake Protocol. Never generate fabricated mock answers.")
            score -= 35

        # Pattern: silent exception swallowing
        if re.search(r"(except\s*:\s*pass|except\s+Exception\s*:\s*pass|silent ignore)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.AI_CONDUCT,
                severity=Severity.HIGH,
                principle_violated="Explicit Error Handling",
                description="Silent exception swallowing detected (hiding fatal system errors).",
                suggestion="Catch specific exceptions and log stack traces explicitly."
            ))
            recommendations.append("Never swallow exceptions silently. Log or re-raise errors.")
            score -= 30

        # Pattern: hardcoded local absolute paths or magic strings
        if re.search(r"(\/Users\/[a-zA-Z0-9_-]+|\/home\/[a-zA-Z0-9_-]+)", prompt):
            findings.append(FindingItem(
                category=LensCategory.AI_CONDUCT,
                severity=Severity.MEDIUM,
                principle_violated="Anti-Hardcoding & Portability",
                description="Host-specific absolute filesystem path detected in instruction.",
                suggestion="Anchor paths to workspace root or pass via environment variables."
            ))
            recommendations.append("Eliminate machine-dependent absolute paths.")
            score -= 20

        passed = score >= 70
        return LensEvaluation(
            category=LensCategory.AI_CONDUCT,
            lens_name="AI Conduct Lens",
            passed=passed,
            score=score,
            findings=findings,
            recommendations=recommendations
        )
