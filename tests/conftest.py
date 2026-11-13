import pytest
import requests
import config
from types import SimpleNamespace

@pytest.fixture
def setup(monkeypatch):
    state = SimpleNamespace(responses=[], sent=0, pauses=0, network_down=False)
    state.urls = []

    def fake_get(*args, **kwargs):
        state.urls.append(args[0])
        state.sent += 1
        if state.network_down:
            raise requests.ConnectionError("no network")
        return state.responses.pop(0)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr("tools.gleif_client.time.sleep",
                        lambda s: setattr(state, "pauses", state.pauses + 1))
    monkeypatch.setattr(config, "GLEIF_MAX_CALLS", 30)
    monkeypatch.setattr(config, "GLEIF_MAX_RETRIES", 3)
    return state
