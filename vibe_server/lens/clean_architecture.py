"""Clean Architecture Lens — Uncle Bob dependency rule, boundary isolation, Contract Facade."""
import re
from vibe_server.core.models import FindingItem, LensCategory, LensEvaluation, Severity


class CleanArchitectureLens:
    """Evaluates proposed changes against Clean Architecture boundary and dependency rules."""

    def evaluate(self, prompt: str, target_files: list[str] = None) -> LensEvaluation:
        findings: list[FindingItem] = []
        recommendations: list[str] = []
        score = 100

        # Pattern: direct database/infrastructure access from UI/API layer
        if re.search(r"(ui directly calls db|db in view|bypass service layer)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.CLEAN_ARCHITECTURE,
                severity=Severity.HIGH,
                principle_violated="Dependency Inversion Principle (DIP)",
                description="Direct coupling between UI presentation and low-level database/infrastructure.",
                suggestion="Introduce a domain service and repository interface to decouple layers."
            ))
            recommendations.append("Enforce strict boundary isolation between presentation and persistence.")
            score -= 35

        # Check target files architecture
        if target_files:
            has_core = any("core" in f for f in target_files)
            has_ui = any("mobile" in f or "ui" in f for f in target_files)
            if has_core and has_ui and len(target_files) < 3:
                findings.append(FindingItem(
                    category=LensCategory.CLEAN_ARCHITECTURE,
                    severity=Severity.MEDIUM,
                    principle_violated="Layer Boundary Isolation",
                    description="Direct modification linking UI and core without mediator layer.",
                    suggestion="Introduce an abstraction or state machine layer between UI and core."
                ))
                recommendations.append("Isolate UI state from core orchestration logic.")
                score -= 20

        passed = score >= 70
        return LensEvaluation(
            category=LensCategory.CLEAN_ARCHITECTURE,
            lens_name="Clean Architecture Lens",
            passed=passed,
            score=score,
            findings=findings,
            recommendations=recommendations
        )
