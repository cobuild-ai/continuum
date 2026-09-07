"""Conversational Vibe Coding Agent: Antigravity-style pair programming on mobile via local SkyBrain SLM."""
import json
import logging
import re
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from vibe_server.core.ai_client import AIEngineClient
from vibe_server.core.config import settings

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """Provides conversational pair-programming dialog and intent classification via Gemini Flash / SkyBrain."""

    def __init__(self, ai_client: Optional[AIEngineClient] = None, skybrain_url: Optional[str] = None):
        if ai_client:
            self.ai_client = ai_client
        elif skybrain_url:
            self.ai_client = AIEngineClient(
                provider="skybrain",
                skybrain_url=skybrain_url,
                skybrain_model=settings.skybrain_model
            )
        else:
            self.ai_client = AIEngineClient.from_settings(settings)

    def is_lens_audit_intent(self, message: str) -> bool:
        """
        Determines whether the user explicitly requests a 5-Lens quality & integrity audit.
        Only explicit requests (e.g. '5대 렌즈 진단', '코드 진단', '정적 분석') trigger this.
        """
        clean = message.strip().lower()
        lens_patterns = [
            r"(5대\s*렌즈|five-?lens).*(진단|평가|검증|점검|분석|스캔|리뷰)",
            r"^(5대\s*렌즈\s*진단|렌즈\s*진단|코드\s*진단|정적\s*분석)$",
            r"(코드\s*품질\s*점검|아키텍처\s*진단|보안\s*점검)\s*(해\s*줘|진행|수행|요청)",
            r"\b(run 5-lens|lens audit|lens check|static audit)\b",
        ]
        return any(re.search(p, clean) for p in lens_patterns)

    def is_code_task_intent(self, message: str) -> bool:
        """
        Determines whether the user's input is an action-oriented code task
        (file creation, bug fix, refactor, feature implement, test run) or a conversational inquiry/discussion.
        """
        clean = message.strip().lower()
        
        # 1. Action-oriented code task verbs and file mentions (Highest priority)
        task_verbs = [
            r"(만들어|생성해|추가해|구현해|짜줘|작성해|개발해|작업해|바꿔|수정해|고쳐|리팩토링)",
            r"(검증|테스트|빌드).*(해\s*줘|하자|하라|진행|수행|실행|부탁)",
            r"(검증|테스트|빌드)\s*(해|하라|하자|요청)",
            r"\b(create|add|implement|write|build|fix|refactor|delete|remove|generate|update|make)\b",
            r"\b(test|inspect|verify|run tests)\b",
            r"\b[a-zA-Z0-9_\-]+\.(py|kt|java|js|ts|html|css|json|sh|md)\b",  # mentions a file
        ]
        for pattern in task_verbs:
            if re.search(pattern, clean):
                return True

        # 2. Conversational / status / greeting patterns
        conversational_patterns = [
            r"^(안녕|하이|ㅎㅇ|hello\b|hi\b|hey\b)\s*$",
            r"^(안녕|하이|ㅎㅇ|hello|hi|hey)[!?,~\s]",
            r"(누구야|뭐야|뭐해|어떤 기능|어떻게 써|사용법|도움말|\bhelp\b|\binfo\b)",
            r"(설명해줘|알려줘|어때\?|어떤 구조야|파일 뭐 있어)",
            r"^(프로젝트\s*(상태|정보|조회|목록|설명)?$|현재\s*상태|깃\s*상태|상태\s*확인|\bstatus\b)",
        ]
        for pattern in conversational_patterns:
            if re.search(pattern, clean):
                return False

        # Default: if it's general text without action verbs, treat as conversational
        return False

    def chat(self, project_path: Path, message: str, history: List[Dict[str, str]] = None) -> str:
        """Interactively answers user questions about the project using Gemini Flash / SkyBrain."""
        project_name = project_path.name
        files_sample = [p.name for p in list(project_path.iterdir())[:12] if not p.name.startswith(".")]
        
        system_prompt = (
            f"You are Continuum, a mobile-first AI pair programmer for project '{project_name}'. "
            f"Project files: {', '.join(files_sample)}. "
            f"Respond directly and naturally in Korean in 2-4 concise, helpful sentences. "
            f"Discuss code, architecture, or answer questions cleanly."
        )

        return self.ai_client.generate_chat(system_prompt, message, history)
