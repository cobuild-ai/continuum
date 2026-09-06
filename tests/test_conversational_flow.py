"""Unit tests for ConversationalAgent intent classification and chat response."""
from pathlib import Path
from vibe_server.core.conversational_agent import ConversationalAgent


def test_intent_classification():
    agent = ConversationalAgent()

    # Conversational inquiries
    assert agent.is_code_task_intent("안녕") is False
    assert agent.is_code_task_intent("이 프로젝트 구조 설명해줘") is False
    assert agent.is_code_task_intent("어떤 기능이 있어?") is False
    assert agent.is_code_task_intent("Hello!") is False
    assert agent.is_code_task_intent("상태 확인") is False

    # Action-oriented code tasks
    assert agent.is_code_task_intent("hello.py 만들어줘") is True
    assert agent.is_code_task_intent("Create a login module in Python") is True
    assert agent.is_code_task_intent("Add unit tests for database connection") is True
    assert agent.is_code_task_intent("통계 계산 모듈 구현해") is True
    assert agent.is_code_task_intent("버그 고쳐줘") is True
    assert agent.is_code_task_intent("코드 품질 및 보안을 위한 5대 렌즈 종합 진단을 수행해 줘") is True
    assert agent.is_code_task_intent("프로젝트 빌드 및 단위 테스트를 검증해 줘") is True


def test_chat_fallback(tmp_path: Path):
    # Invalid url will trigger safe fallback
    agent = ConversationalAgent(skybrain_url="http://127.0.0.1:9999/invalid")
    (tmp_path / "main.py").write_text("print(1)")
    
    reply = agent.chat(tmp_path, "안녕")
    assert "Continuum AI" in reply
    assert tmp_path.name in reply
