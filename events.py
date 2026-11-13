from dataclasses import dataclass
from models import CandidateEntity

@dataclass
class ToolCall:
    name: str
    arguments: dict

@dataclass
class Report:
    content: str

@dataclass
class ToolResult:
    tool_call: ToolCall
    result: str
    is_error: bool = False

@dataclass
class Error:
    message: str

@dataclass
class NeedConfirmation:
    candidates: list[CandidateEntity]

Event = ToolCall | ToolResult | Report | Error | NeedConfirmation