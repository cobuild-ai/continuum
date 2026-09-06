"""Security Lens — OWASP Top 10, path traversal, injection vectors, secret leakage."""
import re
from vibe_server.core.models import FindingItem, LensCategory, LensEvaluation, Severity


class SecurityLens:
    """Evaluates proposed changes against security vulnerabilities and isolation breaches."""

    def evaluate(self, prompt: str, target_files: list[str] = None) -> LensEvaluation:
        findings: list[FindingItem] = []
        recommendations: list[str] = []
        score = 100

        # Pattern: secret leakage or hardcoded credentials
        if re.search(r"(api[_-]?key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]|password\s*=|secret\s*=)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.SECURITY,
                severity=Severity.CRITICAL,
                principle_violated="Credential & Secret Protection",
                description="Plaintext secret or API key pattern detected in prompt.",
                suggestion="Externalize all credentials to environment variables (.env) or secret vaults."
            ))
            recommendations.append("Never commit plaintext secrets. Use environment variables.")
            score -= 50

        # Pattern: dangerous shell execution or unsanitized eval
        if re.search(r"(shell=True|eval\(|exec\(|os\.system\(.*[\+\$])", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.SECURITY,
                severity=Severity.CRITICAL,
                principle_violated="Command / Code Injection Prevention",
                description="Unsanitized dynamic evaluation or command execution detected.",
                suggestion="Use parameterized subprocess calls without shell=True."
            ))
            recommendations.append("Enforce strict input parameterization on all command executions.")
            score -= 40

        # Pattern: host filesystem escape
        if re.search(r"(\/etc\/shadow|\/root|\/etc\/sudoers)", prompt, re.I):
            findings.append(FindingItem(
                category=LensCategory.SECURITY,
                severity=Severity.HIGH,
                principle_violated="Filesystem Isolation Boundary",
                description="Attempted access or mutation of critical host operating system paths.",
                suggestion="Isolate file mutations strictly within the Docker sandbox volume."
            ))
            recommendations.append("Execute all host file changes inside the Docker sandbox.")
            score -= 40

        passed = score >= 70
        return LensEvaluation(
            category=LensCategory.SECURITY,
            lens_name="Security Lens",
            passed=passed,
            score=score,
            findings=findings,
            recommendations=recommendations
        )
