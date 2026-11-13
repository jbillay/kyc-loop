import pytest
import config
from tools.gleif_client import GleifError
from tools.gleif_search import gleif_search_entity
from tests.helpers import fake_response, fuzzy_body, record_body

def test_no_lei_in_suggestions(setup):
    setup.responses = [fake_response(200, fuzzy_body((None, "Alpha"), (None, "Alpha 2")))]
    result = gleif_search_entity("alpha")
    assert result.candidates == []
    assert result.failed_lookups == 0
    assert setup.sent == 1

def test_normal_search(setup):
    setup.responses = [
        fake_response(200, fuzzy_body(("LEI_A", "Alpha"), ("LEI_B", "Alpha 2"))),
        fake_response(200, record_body("LEI_B", "Alpha Holding")),
        fake_response(200, record_body("LEI_A", "Alpha SA")),
    ]
    result = gleif_search_entity("alpha")
    assert len(result.candidates) == 2
    assert result.failed_lookups == 0
    assert setup.sent == 3
    assert result.candidates[0].lei == "LEI_B"
    assert setup.urls[0] == "https://api.gleif.org/api/v1/fuzzycompletions"
    assert setup.urls[1].endswith("/lei-records/LEI_A")

def test_one_record_404(setup):
    setup.responses = [
        fake_response(200, fuzzy_body(("LEI_A", "Alpha"), ("LEI_B", "Alpha 2"))),
        fake_response(200, record_body("LEI_A", "Alpha SA")),
        fake_response(404),
    ]
    result = gleif_search_entity("alpha")
    assert len(result.candidates) == 1
    assert result.failed_lookups == 1
    assert setup.sent == 3
    assert result.candidates[0].lei == "LEI_A"

def test_all_records_fail(setup):
    setup.responses = [
        fake_response(200, fuzzy_body(("LEI_A", "Alpha"), ("LEI_B", "Alpha 2"))),
        fake_response(404),
        fake_response(404),
    ]
    with pytest.raises(GleifError, match="All LEI"):
        gleif_search_entity("alpha")

def test_fuzzy_unreachable(setup):
    setup.network_down = True
    with pytest.raises(GleifError, match="unreachable"):
        gleif_search_entity("alpha")
    assert setup.sent == 1

def test_budget_exhausted_during_search(setup, monkeypatch):
    monkeypatch.setattr(config, "GLEIF_MAX_CALLS", 2)
    setup.responses = [
        fake_response(200, fuzzy_body(("LEI_A", "A"), ("LEI_B", "B"), ("LEI_C", "C"))),
        fake_response(200, record_body("LEI_A", "Alpha SA")),
        fake_response(200, record_body("LEI_A", "Alpha SA")),
    ]
    with pytest.raises(GleifError, match="budget"):
        gleif_search_entity("alpha")
    assert setup.sent == 2