from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

@dataclass
class EvalCase:
    id: str
    language: str
    category: str
    input: str
    expected_agent: str
    expected_behavior: str
    expected_language: str
    requires_rag: bool
    requires_external_api: bool
    priority: str
    expected_sources: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EvalCase":
        return cls(
            id=d["id"],
            language=d["language"],
            category=d["category"],
            input=d["input"],
            expected_agent=d["expected_agent"],
            expected_behavior=d["expected_behavior"],
            expected_language=d["expected_language"],
            requires_rag=d["requires_rag"],
            requires_external_api=d["requires_external_api"],
            priority=d["priority"],
            expected_sources=d.get("expected_sources", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvalResult:
    case_id: str
    provider: str
    response: str
    routing_detected: str
    latency_ms: float
    success: bool
    score: int
    metrics: Dict[str, Any]
    reasons: List[str]
    run_id: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
