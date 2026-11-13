from dataclasses import dataclass, field

from models import CandidateEntity

@dataclass
class Session:
    messages: list = field(default_factory=list)
    candidates: list[CandidateEntity] = field(default_factory=list)
    confirmed_lei: str | None = None