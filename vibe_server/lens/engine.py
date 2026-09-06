"""5-Lens integrated analysis engine — synchronized with SkyBrain Strategy Pattern and Real Source Analysis."""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from vibe_server.core.models import FindingItem, LensCategory, LensEvaluation, LensReport, Severity
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
        """Prompt-level preflight evaluation."""
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
            summary = f"5대 렌즈 정적 룰 검증 완료 (종합 점수: {avg_score}/100)."
        else:
            failed = [name for name, ev in evals.items() if not ev.passed]
            summary = f"5대 렌즈 검증 결함 감지: {', '.join(failed)} (종합 점수: {avg_score}/100)."

        return LensReport(
            overall_passed=overall_passed,
            average_score=avg_score,
            evaluations=evals,
            summary=summary
        )

    def evaluate_project(self, project_path: Path) -> LensReport:
        """Performs real static analysis across actual workspace source files (Zero Fake Protocol)."""
        sec_findings: List[FindingItem] = []
        code_findings: List[FindingItem] = []
        arch_findings: List[FindingItem] = []
        perf_findings: List[FindingItem] = []
        conduct_findings: List[FindingItem] = []

        # Scan real files
        source_extensions = {".py", ".kt", ".java", ".js", ".ts"}
        scanned_count = 0

        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "__pycache__", "build", ".gradle", "node_modules", ".idea"}]
            for fname in files:
                ext = Path(fname).suffix.lower()
                if ext not in source_extensions or fname.startswith("."):
                    continue

                file_path = Path(root) / fname
                rel_path = file_path.relative_to(project_path).as_posix()
                scanned_count += 1

                try:
                    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                except Exception:
                    continue

                # 1. Clean Code: Check file size (> 450 lines)
                if len(lines) > 450:
                    code_findings.append(FindingItem(
                        category=LensCategory.CLEAN_CODE,
                        severity=Severity.LOW,
                        principle_violated="Single Responsibility Principle",
                        description=f"File exceeds recommended 450 lines ({len(lines)} lines).",
                        suggestion="Consider decomposing into smaller, focused modules.",
                        file=rel_path,
                        line=1
                    ))

                for line_idx, line in enumerate(lines, start=1):
                    # 2. Security: Plaintext secret detection
                    if re.search(r'(api_key|secret_key|password)\s*=\s*["\'][A-Za-z0-9_\-]{20,}["\']', line, re.I):
                        sec_findings.append(FindingItem(
                            category=LensCategory.SECURITY,
                            severity=Severity.CRITICAL,
                            principle_violated="Hardcoded Credential Exposure",
                            description="Hardcoded secret or API key string detected.",
                            suggestion="Externalize secrets to environment variables or secret store.",
                            file=rel_path,
                            line=line_idx
                        ))

                    # 3. Security: eval() or shell=True
                    if re.search(r'\beval\(|\bexec\(|shell\s*=\s*True', line):
                        sec_findings.append(FindingItem(
                            category=LensCategory.SECURITY,
                            severity=Severity.HIGH,
                            principle_violated="Code/Command Injection Hazard",
                            description="Dangerous dynamic code evaluation or unparameterized shell command.",
                            suggestion="Use parameterized subprocess calls without shell=True.",
                            file=rel_path,
                            line=line_idx
                        ))

                    # 4. Clean Architecture: Layer violation (e.g. UI importing database directly)
                    if "ui" in rel_path and re.search(r'import.*sqlite|import.*postgres|import.*mysql', line):
                        arch_findings.append(FindingItem(
                            category=LensCategory.CLEAN_ARCHITECTURE,
                            severity=Severity.HIGH,
                            principle_violated="Separation of Concerns",
                            description="Direct database import in presentation/UI layer.",
                            suggestion="Access data through repository or domain use cases.",
                            file=rel_path,
                            line=line_idx
                        ))

                    # 5. Performance: Busy sleep or unbuffered sync loops
                    if re.search(r'time\.sleep\(0\.00', line):
                        perf_findings.append(FindingItem(
                            category=LensCategory.PERFORMANCE,
                            severity=Severity.MEDIUM,
                            principle_violated="CPU Busy Waiting",
                            description="Micro-sleep spinlock detected.",
                            suggestion="Use asynchronous events or notification locks.",
                            file=rel_path,
                            line=line_idx
                        ))

                    # 6. AI Conduct: Unresolved placeholder mock tags
                    if re.search(r'TODO:\s*fake|mock_pass_without_test', line, re.I):
                        conduct_findings.append(FindingItem(
                            category=LensCategory.AI_CONDUCT,
                            severity=Severity.HIGH,
                            principle_violated="Truth-First & Zero Fake Protocol",
                            description="Fake placeholder or unverified mock detected.",
                            suggestion="Replace with real implementation and automated tests.",
                            file=rel_path,
                            line=line_idx
                        ))

        # Calculate scores
        def calc_lens(cat: LensCategory, name: str, findings: List[FindingItem]) -> LensEvaluation:
            penalty = sum(30 if f.severity == Severity.CRITICAL else 20 if f.severity == Severity.HIGH else 10 for f in findings)
            score = max(40, 100 - penalty)
            passed = score >= 70
            recs = [f.suggestion for f in findings[:3]]
            return LensEvaluation(
                category=cat,
                lens_name=name,
                passed=passed,
                score=score,
                findings=findings[:5],  # Top 5 findings
                recommendations=recs
            )

        evals = {
            "clean_code": calc_lens(LensCategory.CLEAN_CODE, "Clean Code Lens", code_findings),
            "clean_architecture": calc_lens(LensCategory.CLEAN_ARCHITECTURE, "Clean Architecture Lens", arch_findings),
            "security": calc_lens(LensCategory.SECURITY, "Security Lens", sec_findings),
            "performance": calc_lens(LensCategory.PERFORMANCE, "Performance Lens", perf_findings),
            "ai_conduct": calc_lens(LensCategory.AI_CONDUCT, "AI Conduct Lens", conduct_findings)
        }

        scores = [ev.score for ev in evals.values()]
        avg_score = round(sum(scores) / len(scores), 1)
        overall_passed = all(ev.passed for ev in evals.values())
        total_findings = sum(len(ev.findings) for ev in evals.values())

        summary = (
            f"실제 소스코드 {scanned_count}개 파일 정적 분석 완료. "
            f"검출된 결함 {total_findings}건 (종합 점수: {avg_score}/100)."
        )

        return LensReport(
            overall_passed=overall_passed,
            average_score=avg_score,
            evaluations=evals,
            summary=summary
        )
