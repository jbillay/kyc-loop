import json
from types import SimpleNamespace
from pathlib import Path

def fake_response(status, body=None):
    def json():
        if body is None:
            raise ValueError("no json")
        return body
    return SimpleNamespace(status_code=status, json=json)

def fuzzy_body(*items):
    """items : liste de (lei, nom). lei=None -> suggestion sans entité."""
    data = []
    for lei, name in items:
        item = {"type": "fuzzycompletions", "attributes": {"value": name}}
        if lei:
            item["relationships"] = {"lei-records": {"data": {"type": "lei-records", "id": lei}}}
        data.append(item)
    return {"data": data}

def record_body(lei, name, country="XX", city="Ville", status="ACTIVE", lei_status="ISSUED"):
    return {"data": {"attributes": {
        "lei": lei,
        "entity": {"legalName": {"name": name},
                   "legalAddress": {"country": country, "city": city},
                   "status": status},
        "registration": {"status": lei_status}}}}

def load_fixture(name):
    path = Path(__file__).parent / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))

class FakeLLM:
    def __init__(self, responses):
        self.responses = responses
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))
    def _create(self, **kwargs):
        return self.responses.pop(0)

def llm_response(content=None, tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])

def tool_call(call_id, name, arguments: dict):
    function = SimpleNamespace(name=name, arguments=json.dumps(arguments))
    return SimpleNamespace(id=call_id, function=function)

def tool_messages(session):
    return [m for m in session.messages if isinstance(m, dict) and m["role"] == "tool"]