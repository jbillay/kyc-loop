import pytest
import config
from tools.gleif_client import GleifClient, GleifError
from tests.helpers import fake_response

def test_200_direct(setup):
    setup.responses = [fake_response(200, {"ok": 1})]
    client = GleifClient()
    assert client.get("x") == (200, {"ok": 1})
    assert setup.sent == 1
    assert client.calls == 1
    assert setup.pauses == 0


def test_429_then_200(setup):
    setup.responses = [fake_response(429, None), fake_response(200, {"ok": 1})]
    client = GleifClient()
    assert client.get("x") == (200, {"ok": 1})
    assert setup.sent == 2
    assert client.calls == 2
    assert setup.pauses == 1

def test_404_without_json(setup):
    setup.responses = [fake_response(404, None)]
    client = GleifClient()
    assert client.get("x") == (404, None)
    assert setup.sent == 1
    assert client.calls == 1
    assert setup.pauses == 0

def test_429_four_times(setup):
    setup.responses = [fake_response(429)] * 4
    client = GleifClient()
    with pytest.raises(GleifError, match="retries"):
        client.get("x")
    assert setup.sent == 3        # combien de requêtes sont parties ?
    assert client.calls == 3      # compteur de ton client
    assert setup.pauses == 2      # nombre de pauses

def test_budget_2_only_429(setup, monkeypatch):
    monkeypatch.setattr(config, "GLEIF_MAX_CALLS", 2)
    setup.responses = [fake_response(429)] * 2
    client = GleifClient()
    with pytest.raises(GleifError, match="budget"):
        client.get("x")
    assert setup.sent == 2        # combien de requêtes sont parties ?
    assert client.calls == 2      # compteur de ton client
    assert setup.pauses == 1      # nombre de pauses

def test_budget_0(setup, monkeypatch):
    monkeypatch.setattr(config, "GLEIF_MAX_CALLS", 0)
    setup.responses = []
    client = GleifClient()
    with pytest.raises(GleifError, match="budget"):
        client.get("x")
    assert setup.sent == 0        # combien de requêtes sont parties ?
    assert client.calls == 0      # compteur de ton client
    assert setup.pauses == 0      # nombre de pauses

def test_network_down(setup):
    setup.network_down = True
    client = GleifClient()
    with pytest.raises(GleifError, match="unreachable"):
        client.get("x")
    assert setup.sent == 1        # combien de requêtes sont parties ?
    assert client.calls == 1      # compteur de ton client
    assert setup.pauses == 0      # nombre de pauses

def test_same_client_after_budget(setup, monkeypatch):
    monkeypatch.setattr(config, "GLEIF_MAX_CALLS", 2)
    setup.responses = [fake_response(200, {"ok": 1})] * 4
    client = GleifClient()

    assert client.get("x") == (200, {"ok": 1})
    assert client.get("x") == (200, {"ok": 1})
    with pytest.raises(GleifError, match="budget"):
        client.get("x")
    with pytest.raises(GleifError, match="budget"):
        client.get("x")
    assert setup.sent == 2
    assert client.calls == 2