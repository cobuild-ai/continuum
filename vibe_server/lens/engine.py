"""5-Lens integrated analysis engine — synchronized with SkyBrain Strategy Pattern."""
from vibe_server.core.models import LensReport
from vibe_server.lens.clean_code import CleanCodeLens
from vibe_server.lens.clean_architecture import CleanArchitectureLens
from vibe_server.lens.security import SecurityLens
from vibe_server.lens.performance import PerformanceLens
from vibe_server.lens.ai_conduct import AIConductLens


class FiveLensEngine:
    """Orchestrates the 5-Lens quality & integrity evaluation (CleanCode, Architecture, Security, Performance, AIConduct)."""

    def __init__(self):
        self.clean_code_lens = CleanCodeLens()
        self.clean_arch_lens = CleanArchitectureLens()
        self.security_lens = SecurityLens()
        self.performance_lens = PerformanceLens()
        self.ai_conduct_lens = AIConductLens()

    def evaluate(self, prompt: str, target_files: list[str] = None) -> LensReport:
        evals = {
            "clean_code": self.clean_code_lens.evaluate(prompt, target_files),
            "clean_architecture": self.clean_arch_lens.evaluate(prompt, target_files),
            "security": self.security_lens.evaluate(prompt, target_files),
            "performance": self.performance_lens.evaluate(prompt, target_files),
            "ai_conduct": self.ai_conduct_lens.evaluate(prompt, target_files)
        }

        scores = [ev.score for ev in evals.values()]
        avg_score = round(sum(scores) / len(scores), 2)
        overall_passed = all(ev.passed for ev in evals.values())

        if overall_passed:
            summary = f"All 5 SkyBrain-aligned lenses passed with an average rating of {avg_score}/100. Ready for execution."
        else:
            failed = [name for name, ev in evals.items() if not ev.passed]
            summary = f"Review failed on lenses: {', '.join(failed)} (Average: {avg_score}/100). Adjustments required."

        return LensReport(
            overall_passed=overall_passed,
            average_score=avg_score,
            evaluations=evals,
            summary=summary
        )
