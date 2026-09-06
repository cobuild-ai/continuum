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
            self.ai_client = AIEngineClient(
                provider=settings.ai_provider,
                gemini_model=settings.gemini_model,
                gemini_api_key=settings.gemini_api_key,
                skybrain_url=settings.skybrain_url,
                skybrain_model=settings.skybrain_model
            )

    def is_code_task_intent(self, message: str) -> bool:
        """
        Determines whether the user's input is an action-oriented code task
        (file creation, bug fix, refactor, feature implement) or a conversational inquiry/discussion.
        """
        clean = message.strip().lower()
        
        # 1. Action-oriented code task verbs and file mentions (Highest priority)
        task_verbs = [
            r"(만들어|생성해|추가해|구현해|짜줘|작성해|개발해|작업해|바꿔|수정해|고쳐|리팩토링)",
            r"(진단|검증|평가|점검|스캔|테스트|빌드).*(해\s*줘|하자|하라|진행|수행|실행|부탁)",
            r"(진단|검증|평가|점검|스캔|테스트|빌드)\s*(해|하라|하자|요청)",
            r"(5대\s*렌즈|five-?lens).*(진단|평가|검증|수행|실행|해\s*줘|돌려)",
            r"\b(create|add|implement|write|build|fix|refactor|delete|remove|generate|update|make)\b",
            r"\b(diagnose|evaluate|audit|test|inspect|verify|run)\b",
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
