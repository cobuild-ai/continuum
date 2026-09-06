"""Performance Lens — Resource lifecycles (sockets/SSL), blocking I/O on hot paths, complexity."""
import re
from vibe_server.core.models import FindingItem, LensCategory, LensEvaluation, Severity


class PerformanceLens:
    """Evaluates proposed changes for resource leaks, blocking I/O, and latency hazards."""

    def evaluate(self, prompt: str, target_files: list[str] = None) -> LensEvaluation:
        findings: list[FindingItem] = []
        recommendations: list[str] = []
        score = 100

        # Pattern: blocking calls in asynchronous pipelines
        if re.search(r"(time\.sleep|blocking call in async|sync request in event loop)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.PERFORMANCE,
                severity=Severity.HIGH,
                principle_violated="Non-Blocking Asynchronous I/O",
                description="Synchronous blocking operations detected in asynchronous pipeline.",
                suggestion="Replace with asyncio.sleep or run in an isolated thread pool."
            ))
            recommendations.append("Use non-blocking asynchronous primitives to avoid freezing the event loop.")
            score -= 35

        # Pattern: unclosed resources or memory leaks
        if re.search(r"(unclosed connection|no timeout|infinite loop without break)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.PERFORMANCE,
                severity=Severity.MEDIUM,
                principle_violated="Resource Lifecycle Management",
                description="Potential unmanaged resource lifecycle or missing connection timeout.",
                suggestion="Enforce context managers (with / async with) and explicit timeouts."
            ))
            recommendations.append("Always set explicit socket/HTTP timeouts and release connections.")
            score -= 25

        passed = score >= 70
        return LensEvaluation(
            category=LensCategory.PERFORMANCE,
            lens_name="Performance Lens",
            passed=passed,
            score=score,
            findings=findings,
            recommendations=recommendations
        )
