import json
import logging
import os
import re
import socket
import time
import urllib.request
from typing import Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
SKYBRAIN_URL = "http://127.0.0.1:8000/v1/chat/completions"

# 1순위: gemini-3.8-flash (최상의 코딩 성능)
# 2순위: gemini-3.7-flash, gemini-2.5-flash (429/지연 시 비용 절감 및 백업)
# 3순위: Local SkyBrain (Qwen 3.8) (클라우드 모델 429/실패 시 $0 무과금 로컬 오프로딩)
GEMINI_FLASH_CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-2.5-flash",
]

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


class SkyBrainCircuitBreaker:
    """
    Active Connection Manager & Circuit Breaker for Local SkyBrain SLM.
    Uses ultra-fast 150ms socket probing with a 5s TTL cache so runtime calls
    never wait on timed-out HTTP connections when the daemon is offline.
    """
    _last_checked: float = 0.0
    _is_healthy: bool = False
    _ttl_seconds: float = 5.0

    @classmethod
    def is_alive(cls, url: str) -> bool:
        now = time.time()
        if now - cls._last_checked < cls._ttl_seconds:
            return cls._is_healthy

        cls._last_checked = now
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 8000)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.15)
                res = s.connect_ex((host, port))
                cls._is_healthy = (res == 0)
        except Exception:
            cls._is_healthy = False

        return cls._is_healthy


class AIEngineClient:
    """Unified client orchestrating Cloud LLMs (Gemini, Claude, Codex/OpenAI) and optional Local SkyBrain SLM."""

    def __init__(
        self,
        provider: str = "gemini",  # "gemini" | "claude" | "codex" | "openai" | "skybrain"
        gemini_model: str = "gemini-3.8-flash",
        gemini_api_key: Optional[str] = None,
        gemini_api_url: str = GEMINI_API_URL,
        claude_model: str = "claude-3-7-sonnet-20250219",
        claude_api_key: Optional[str] = None,
        claude_api_url: str = CLAUDE_API_URL,
        openai_model: str = "gpt-4o",
        openai_api_key: Optional[str] = None,
        openai_api_url: str = OPENAI_API_URL,
        custom_api_url: str = "",
        skybrain_enabled: bool = False,
        skybrain_url: str = SKYBRAIN_URL,
        skybrain_model: str = "qwen3.8"
    ):
        self.provider = provider
        self.gemini_model = gemini_model
        self.gemini_api_key = self._resolve_api_key("GEMINI_API_KEY", gemini_api_key)
        self.gemini_api_url = gemini_api_url

        self.claude_model = claude_model
        self.claude_api_key = self._resolve_api_key("ANTHROPIC_API_KEY", claude_api_key)
        self.claude_api_url = claude_api_url

        self.openai_model = openai_model
        self.openai_api_key = self._resolve_api_key("OPENAI_API_KEY", openai_api_key)
        self.openai_api_url = openai_api_url
        self.custom_api_url = custom_api_url
        
        self.skybrain_enabled = skybrain_enabled
        self.skybrain_url = skybrain_url
        self.skybrain_model = skybrain_model

        target_url = self.custom_api_url or (
            self.claude_api_url if self.provider == "claude"
            else self.openai_api_url if self.provider in ("codex", "openai")
            else self.skybrain_url if self.provider == "skybrain"
            else "Google GenerativeLanguage"
        )
        logger.info(
            f"AIEngineClient initialized: provider={self.provider}, "
            f"model={self.active_model}, endpoint={target_url}, skybrain_enabled={self.skybrain_enabled}"
        )

    @classmethod
    def from_settings(cls, s=None) -> "AIEngineClient":
        """Factory method building client directly from application Settings."""
        if s is None:
            from vibe_server.core.config import settings as s
        return cls(
            provider=s.ai_provider,
            gemini_model=s.gemini_model,
            gemini_api_key=s.gemini_api_key,
            gemini_api_url=getattr(s, "gemini_api_url", GEMINI_API_URL),
            claude_model=s.claude_model,
            claude_api_key=s.claude_api_key,
            claude_api_url=getattr(s, "claude_api_url", CLAUDE_API_URL),
            openai_model=s.openai_model,
            openai_api_key=s.openai_api_key,
            openai_api_url=getattr(s, "openai_api_url", OPENAI_API_URL),
            custom_api_url=getattr(s, "custom_api_url", ""),
            skybrain_enabled=s.skybrain_enabled,
            skybrain_url=s.skybrain_url,
            skybrain_model=s.skybrain_model
        )

    @property
    def active_model(self) -> str:
        if self.provider == "gemini":
            return self.gemini_model
        elif self.provider == "claude":
            return self.claude_model
        elif self.provider in ("codex", "openai"):
            return self.openai_model
        elif self.provider == "skybrain":
            return self.skybrain_model
        return self.gemini_model

    @staticmethod
    def _resolve_api_key(env_var_name: str, explicit_key: Optional[str] = None) -> str:
        if explicit_key and explicit_key.strip():
            return explicit_key.strip()
        env_key = os.environ.get(env_var_name) or os.environ.get(f"CONTINUUM_{env_var_name}", "")
        if env_key and env_key.strip():
            return env_key.strip()
        zshrc_path = os.path.expanduser("~/.zshrc")
        if os.path.exists(zshrc_path):
            try:
                with open(zshrc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                match = re.search(rf'export\s+{env_var_name}=["\']?([^"\'\s]+)["\']?', content)
                if match:
                    return match.group(1).strip()
            except Exception:
                pass
        return ""

    @property
    def is_skybrain_available(self) -> bool:
        """Determines if SkyBrain is both enabled and actively reachable with zero-wait socket probing."""
        if not self.skybrain_enabled:
            return False
        return SkyBrainCircuitBreaker.is_alive(self.skybrain_url)

    def generate_chat(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generates conversational pair-programming responses."""
        if self.provider == "gemini" and self.gemini_api_key:
            reply = self._call_gemini_chat(system_prompt, user_prompt, history)
            if reply:
                return reply
        elif self.provider == "claude" and self.claude_api_key:
            reply = self._call_claude_chat(system_prompt, user_prompt, history)
            if reply:
                return reply
        elif self.provider in ("codex", "openai") and self.openai_api_key:
            reply = self._call_openai_chat(system_prompt, user_prompt, history)
            if reply:
                return reply

        # Fallback to local SkyBrain ONLY IF enabled AND actively online (Circuit Breaker verified)
        if self.is_skybrain_available:
            logger.info("Local SkyBrain connection verified online. Routing fallback...")
            return self._call_skybrain_chat(system_prompt, user_prompt, history)

        clean_msg = user_prompt.strip()
        return (
            f"⚠️ **Continuum AI Engine 알림**: {self.provider.upper()} ({self.active_model}) 클라우드 요청 처리 중 일시적인 지연이 발생했습니다.\n\n"
            f"- 요청 내용: **'{clean_msg[:40]}'**\n"
            f"- 잠시 후 다시 전송해 주시거나 `.env`의 API Key를 확인해 주세요."
        )

    def generate_code_files(self, prompt: str) -> Dict[str, str]:
        """Generates code files dictionary {rel_path: content}."""
        if self.provider == "gemini" and self.gemini_api_key:
            files = self._call_gemini_code(prompt)
            if files:
                return files
        elif self.provider == "claude" and self.claude_api_key:
            files = self._call_claude_code(prompt)
            if files:
                return files
        elif self.provider in ("codex", "openai") and self.openai_api_key:
            files = self._call_openai_code(prompt)
            if files:
                return files

        if self.is_skybrain_available:
            logger.info("Local SkyBrain connection verified online for code synthesis...")
            return self._call_skybrain_code(prompt)

        return {}

    # ------------------ Gemini Implementation ------------------
    def _call_gemini_chat(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        models_to_try = [self.gemini_model] + [m for m in GEMINI_FLASH_CANDIDATES if m != self.gemini_model]
        
        contents = []
        if history:
            for item in history[-4:]:
                role = "user" if item.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": item.get("content", "")}]})
        contents.append({"role": "user", "parts": [{"text": f"{system_prompt}\n\n사용자 입력: {user_prompt}"}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 600
            }
        }

        import time
        for model_name in models_to_try:
            url = GEMINI_API_URL.format(model=model_name, api_key=self.gemini_api_key)
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    logger.info(f"Generated chat via Gemini [{model_name}]")
                    return text
            except Exception as e:
                code = getattr(e, "code", str(e))
                logger.warning(f"Gemini model {model_name} failed ({code}), trying fallback...")
                if str(code) in ["429", "503"]:
                    time.sleep(1.0)

        return None

    def _call_gemini_code(self, prompt: str) -> Dict[str, str]:
        system_instruction = (
            "You are an expert autonomous software engineer working within an isolated sandbox. "
            "Given a user coding prompt, generate the required code files. "
            "You MUST respond ONLY with a valid JSON array of objects, where each object has: "
            '{"path": "relative/path/to/file.ext", "content": "file contents as raw text"}. '
            "Do NOT include markdown wrapping or explanation outside the JSON array."
        )
        models_to_try = [self.gemini_model] + [m for m in GEMINI_FLASH_CANDIDATES if m != self.gemini_model]

        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_instruction}\n\nCoding Task: {prompt}"}]}
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048
            }
        }

        import time
        for model_name in models_to_try:
            url = GEMINI_API_URL.format(model=model_name, api_key=self.gemini_api_key)
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    files = self._parse_json_files(raw, prompt)
                    if files:
                        logger.info(f"Generated code via Gemini [{model_name}] ({len(files)} files)")
                        return files
            except Exception as e:
                code = getattr(e, "code", str(e))
                logger.warning(f"Gemini code gen {model_name} failed ({code})...")
                if str(code) in ["429", "503"]:
                    time.sleep(1.0)

        return {}

    # ------------------ Claude Implementation ------------------
    def _call_claude_chat(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        messages = []
        if history:
            for item in history[-4:]:
                messages.append({"role": item.get("role", "user"), "content": item.get("content", "")})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.claude_model,
            "system": system_prompt,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.4
        }
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01"
        }
        try:
            req = urllib.request.Request(self.claude_api_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        return block.get("text", "").strip()
        except Exception as e:
            logger.warning(f"Claude chat call failed: {e}")
        return None

    def _call_claude_code(self, prompt: str) -> Dict[str, str]:
        system_instruction = (
            "You are an expert autonomous software engineer. "
            "Given a user coding prompt, generate required code files. "
            "Respond ONLY with a valid JSON array of objects: "
            '[{"path": "relative/path/to/file.ext", "content": "raw content"}].'
        )
        payload = {
            "model": self.claude_model,
            "system": system_instruction,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "temperature": 0.2
        }
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01"
        }
        try:
            req = urllib.request.Request(self.claude_api_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        text += block.get("text", "")
                return self._parse_json_files(text, prompt)
        except Exception as e:
            logger.warning(f"Claude code call failed: {e}")
        return {}

    # ------------------ OpenAI / Codex / Custom Gateway Implementation ------------------
    def _call_openai_chat(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for item in history[-4:]:
                messages.append({"role": item.get("role", "user"), "content": item.get("content", "")})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.openai_model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.4
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        target_url = self.custom_api_url or self.openai_api_url
        try:
            req = urllib.request.Request(target_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"OpenAI/Custom gateway chat call failed ({target_url}): {e}")
        return None

    def _call_openai_code(self, prompt: str) -> Dict[str, str]:
        system_instruction = (
            "You are an expert autonomous software engineer. "
            "Output ONLY a valid JSON array of objects: "
            '[{"path": "relative/path/to/file.ext", "content": "raw content"}].'
        )
        payload = {
            "model": self.openai_model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.2
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        target_url = self.custom_api_url or self.openai_api_url
        try:
            req = urllib.request.Request(target_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"]
                return self._parse_json_files(text, prompt)
        except Exception as e:
            logger.warning(f"OpenAI/Custom gateway code call failed ({target_url}): {e}")
        return {}

    # ------------------ SkyBrain Implementation ------------------
    def _call_skybrain_chat(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history[-4:])
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.skybrain_model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 500
        }

        try:
            req = urllib.request.Request(
                self.skybrain_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                clean = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
                clean = clean.split("</think>")[-1].strip()
                if clean:
                    return clean
        except Exception as e:
            logger.warning(f"SkyBrain chat failed: {e}")

        clean_msg = user_prompt.strip()
        proj_match = re.search(r"project ['\"]([^'\"]+)['\"]", system_prompt)
        proj_name = proj_match.group(1) if proj_match else "프로젝트"
        return (
            f"⚠️ **Continuum AI 알림**: {proj_name} 프로젝트에 대한 답변 생성 중 일시적인 AI 연결 지연이 발생했습니다.\n\n"
            f"- 요청 내용: **'{clean_msg[:40]}'**\n"
            f"- 원인: Google Cloud Gemini Flash 일시적 Quota 한도(429) 및 로컬 SkyBrain 대기 시간 초과\n"
            f"- 잠시 후 다시 메시지를 보내주시면 즉시 정상 응답됩니다."
        )

    def _call_skybrain_code(self, prompt: str) -> Dict[str, str]:
        system_prompt = (
            "You are an expert autonomous software engineer. "
            "Output ONLY a JSON array of objects: [{\"path\": \"...\", \"content\": \"...\"}]."
        )
        payload = {
            "model": self.skybrain_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1500
        }
        try:
            req = urllib.request.Request(
                self.skybrain_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"]
                return self._parse_json_files(text, prompt)
        except Exception as e:
            logger.warning(f"SkyBrain code gen failed: {e}")
            return {}

    def _parse_json_files(self, text: str, prompt: str = "") -> Dict[str, str]:
        clean_text = re.sub(r"^<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        json_match = re.search(r"\[\s*\{.*\}\s*\]", clean_text, re.DOTALL)
        if json_match:
            try:
                items = json.loads(json_match.group(0))
                files = {}
                for it in items:
                    if isinstance(it, dict) and "path" in it and "content" in it:
                        files[it["path"]] = it["content"]
                if files:
                    return files
            except Exception:
                pass

        file_mention = re.search(r'\b([a-zA-Z0-9_\-]+\.(py|kt|java|md|json|sh|html|txt))\b', prompt)
        default_name = file_mention.group(1) if file_mention else None

        code_block = re.search(r"```([a-zA-Z0-9_\-]+)?\s*(?:#|//)?\s*(?:filename:)?\s*([a-zA-Z0-9_./\-]+)?\n(.*?)```", clean_text, re.DOTALL)
        if code_block:
            detected = code_block.group(2) or default_name or "generated_code.py"
            return {detected.strip(): code_block.group(3)}

        if default_name and clean_text:
            return {default_name: clean_text}

        return {}
