from models import CandidateEntity, SearchResult
from session import Session
from agent import run_agent
from events import Report, ToolResult
from tools import TOOL_FUNCTIONS
from tests.helpers import FakeLLM, llm_response, tool_call, tool_messages
from tools.gleif_client import GleifError

fake_candidate = CandidateEntity(lei="12345678901234567890", legal_name="Fake Entity", country="US", city="New York", status="ACTIVE", lei_status="ISSUED")

def test_search_allowed_before_confirmation(monkeypatch):
    def fake_search(name):
        return SearchResult(candidates=[fake_candidate], failed_lookups=0)
    monkeypatch.setitem(TOOL_FUNCTIONS, "gleif_search_entity", fake_search)
    llm = FakeLLM([
        llm_response(tool_calls=[tool_call("c1", "gleif_search_entity", {"name": "alpha"})]),
        llm_response(content="done"),
    ])
    session = Session()
    events = []
    run_agent(session, "alpha", llm, events.append, lambda need: None)
    assert len(events) == 3
    assert events[0].name == "gleif_search_entity"
    assert isinstance(events[1], ToolResult)
    assert events[1].is_error == False
    assert session.candidates == [fake_candidate]

def test_investigate_not_allowed_before_confirmation(monkeypatch):
    calls = []
    def fake_search(name):
        return SearchResult(candidates=[fake_candidate], failed_lookups=0)
    def fake_investigate(**kwargs):
        calls.append(kwargs)            # chaque appel laisse une trace
        return True
    monkeypatch.setitem(TOOL_FUNCTIONS, "gleif_search_entity", fake_search)
    monkeypatch.setitem(TOOL_FUNCTIONS, "investigate_entity", fake_investigate)
    llm = FakeLLM([
        llm_response(tool_calls=[tool_call("c1", "gleif_search_entity", {"name": "alpha"})]),
        llm_response(tool_calls=[tool_call("c2", "investigate_entity", {"LEI": "12345678901234567890"})]),
        llm_response(content="done"),
    ])
    session = Session()
    events = []
    run_agent(session, "alpha", llm, events.append, lambda need: None)
    messages = tool_messages(session)
    assert len(events) == 5
    assert events[0].name == "gleif_search_entity"
    assert events[2].name == "investigate_entity"
    assert isinstance(events[1], ToolResult)
    assert isinstance(events[3], ToolResult)
    assert not events[1].is_error
    assert calls == []
    assert events[3].is_error
    assert events[3].tool_call.name == "investigate_entity"
    assert messages[1]["tool_call_id"] == "c2"
    assert "not allowed" in messages[1]["content"]
    assert "not allowed" in events[3].result
    assert session.candidates == [fake_candidate]
    assert isinstance(events[4], Report)

def test_trigger_entity_details(monkeypatch):
    session = Session()
    calls = []
    events = []
    def fake_search(name):
        return SearchResult(candidates=[fake_candidate], failed_lookups=0)
    def fake_investigate(**kwargs):
        calls.append(kwargs)            # chaque appel laisse une trace
        return True
    monkeypatch.setitem(TOOL_FUNCTIONS, "gleif_search_entity", fake_search)
    monkeypatch.setitem(TOOL_FUNCTIONS, "get_entity_details", fake_investigate)
    llm = FakeLLM([
        llm_response(tool_calls=[tool_call("c1", "gleif_search_entity", {"name": "alpha"})]),
        llm_response(tool_calls=[tool_call("c2", "ask_user_confirmation", {})]),
        llm_response(tool_calls=[tool_call("c3", "get_entity_details", {})]),
        llm_response(content="done"),
    ])
    run_agent(session, "alpha", llm, events.append, lambda need: need.candidates[0].lei)
    messages = tool_messages(session)
    assert len(messages) == 3
    assert len(events) == 7
    assert events[0].name == "gleif_search_entity"
    assert isinstance(events[1], ToolResult)
    assert events[1].is_error == False
    assert session.candidates == [fake_candidate]
    assert events[2].name == "ask_user_confirmation"
    assert messages[1]["tool_call_id"] == "c2"
    assert "User confirmed LEI" in messages[1]["content"]
    assert messages[2]["tool_call_id"] == "c3"
    assert isinstance(events[3], ToolResult)
    assert "User confirmed LEI" in events[3].result
    assert calls == [{"lei": "12345678901234567890"}]
    assert events[4].name == "get_entity_details"
    assert events[4].arguments == {"lei": "12345678901234567890"}
    assert isinstance(events[5], ToolResult)
    assert not events[5].is_error
 
def test_trigger_entity_details_with_wrong_lei(monkeypatch):
    session = Session()
    calls = []
    events = []
    def fake_search(name):
        return SearchResult(candidates=[fake_candidate], failed_lookups=0)
    def fake_investigate(**kwargs):
        calls.append(kwargs)
        return True
    monkeypatch.setitem(TOOL_FUNCTIONS, "gleif_search_entity", fake_search)
    monkeypatch.setitem(TOOL_FUNCTIONS, "get_entity_details", fake_investigate)
    llm = FakeLLM([
        llm_response(tool_calls=[tool_call("c1", "gleif_search_entity", {"name": "alpha"})]),
        llm_response(tool_calls=[tool_call("c2", "ask_user_confirmation", {})]),
        llm_response(tool_calls=[tool_call("c3", "get_entity_details", {"lei": "wrong_lei"})]),
        llm_response(content="done"),
    ])
    run_agent(session, "alpha", llm, events.append, lambda need: need.candidates[0].lei)
    messages = tool_messages(session)
    assert len(events) == 7
    assert events[0].name == "gleif_search_entity"
    assert isinstance(events[1], ToolResult)
    assert events[1].is_error == False
    assert session.candidates == [fake_candidate]
    assert events[2].name == "ask_user_confirmation"
    assert isinstance(events[3], ToolResult)
    assert calls == [{"lei": "12345678901234567890"}]
    assert events[4].name == "get_entity_details"
    assert events[4].arguments == {"lei": "12345678901234567890"}
    assert messages[2]["tool_call_id"] == "c3"
    assert isinstance(events[5], ToolResult)
    assert not events[5].is_error

def test_search_allowed_trigger_exception(monkeypatch):
    def fake_search(name):
        raise GleifError("Simulated search error")
    monkeypatch.setitem(TOOL_FUNCTIONS, "gleif_search_entity", fake_search)
    llm = FakeLLM([
        llm_response(tool_calls=[tool_call("c1", "gleif_search_entity", {"name": "alpha"})]),
        llm_response(content="done"),
    ])
    session = Session()
    events = []
    run_agent(session, "alpha", llm, events.append, lambda need: None)
    assert events[0].name == "gleif_search_entity"
    assert isinstance(events[1], ToolResult)
    assert events[1].tool_call.name == "gleif_search_entity"
    assert events[1].is_error == True
    assert "Simulated search error" in events[1].result
    assert isinstance(events[2], Report)
    assert len(events) == 3
    messages = tool_messages(session)
    assert len(messages) == 1, session.messages
    assert messages[0]["tool_call_id"] == "c1"
    assert "Simulated search error" in messages[0]["content"]
