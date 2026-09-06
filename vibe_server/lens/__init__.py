"""Continuum 5-Lens Review Package — 100% synchronized with SkyBrain."""
from vibe_server.lens.clean_code import CleanCodeLens
from vibe_server.lens.clean_architecture import CleanArchitectureLens
from vibe_server.lens.security import SecurityLens
from vibe_server.lens.performance import PerformanceLens
from vibe_server.lens.ai_conduct import AIConductLens
from vibe_server.lens.engine import FiveLensEngine

ALL_LENSES = [CleanCodeLens, CleanArchitectureLens, SecurityLens, PerformanceLens, AIConductLens]

__all__ = [
    "ALL_LENSES",
    "CleanCodeLens",
    "CleanArchitectureLens",
    "SecurityLens",
    "PerformanceLens",
    "AIConductLens",
    "FiveLensEngine",
]
