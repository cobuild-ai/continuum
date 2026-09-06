"""Unit tests for 5-Lens analysis engine (SkyBrain synchronized)."""
from vibe_server.lens.engine import FiveLensEngine
from vibe_server.core.models import LensCategory


def test_clean_prompt_passes_all_5_lenses():
    engine = FiveLensEngine()
    prompt = "Create a modular UserService with clean dependency injection and unit tests."
    report = engine.evaluate(prompt)
    
    assert report.overall_passed is True
    assert report.average_score >= 90.0
    assert LensCategory.CLEAN_CODE.value in report.evaluations
    assert LensCategory.CLEAN_ARCHITECTURE.value in report.evaluations
    assert LensCategory.SECURITY.value in report.evaluations
    assert LensCategory.PERFORMANCE.value in report.evaluations
    assert LensCategory.AI_CONDUCT.value in report.evaluations


def test_security_lens_detects_secret():
    engine = FiveLensEngine()
    prompt = "Add auth header using api_key='sk_live_1234567890abcdef123456'"
    report = engine.evaluate(prompt)
    
    sec_eval = report.evaluations["security"]
    assert sec_eval.passed is False
    assert sec_eval.score < 70
    assert any("secret" in f.description.lower() for f in sec_eval.findings)
    assert report.overall_passed is False


def test_clean_code_lens_detects_monolithic_pattern():
    engine = FiveLensEngine()
    prompt = "Put everything in one file to make it fast."
    report = engine.evaluate(prompt)
    
    cc_eval = report.evaluations["clean_code"]
    assert cc_eval.passed is False
    assert any("monolithic" in f.description.lower() for f in cc_eval.findings)


def test_performance_lens_detects_blocking_call():
    engine = FiveLensEngine()
    prompt = "Use time.sleep(10) inside the async event loop."
    report = engine.evaluate(prompt)
    
    perf_eval = report.evaluations["performance"]
    assert perf_eval.passed is False
    assert any("blocking" in f.description.lower() for f in perf_eval.findings)


def test_ai_conduct_lens_detects_fake_mocks():
    engine = FiveLensEngine()
    prompt = "Return fake response with mock data for now and skip real DB."
    report = engine.evaluate(prompt)
    
    ai_eval = report.evaluations["ai_conduct"]
    assert ai_eval.passed is False
    assert any("zero fake" in f.principle_violated.lower() for f in ai_eval.findings)
