from models import ParentLink
from tools.gleif_details import get_entity_details
from tests.helpers import fake_response, load_fixture
from tools.gleif_client import GleifError
import pytest

def fetch_no_parents(setup, body=None, extra=None):
    if body is None:
        body = load_fixture("no_parent_lei_record.json")
    if extra is None:
        extra = [
            fake_response(200, load_fixture("direct_parent_reporting_exception.json")),
            fake_response(200, load_fixture("ultimate_parent_reporting_exception.json")),
        ]
    setup.responses = [fake_response(200, body), *extra]
    return get_entity_details("506700GE1G29325QX363")

def test_details_legal_name_no_parents(setup):
    details = fetch_no_parents(setup)
    assert details.legal_name == "Global Legal Entity Identifier Foundation"
    assert details.status == "ACTIVE"
    assert details.lei_status == "ISSUED"

def test_details_legal_address_no_parents(setup):
    details = fetch_no_parents(setup)
    assert details.legal_address.city == "Basel"
    assert details.legal_address.lines == ["St. Alban-Vorstadt 12"]
    assert details.legal_address.postal_code == "4052"
    assert details.legal_address.country == "CH"
    assert details.legal_address.region == "CH-BS"

def test_details_headquarters_address_no_parents(setup):
    details = fetch_no_parents(setup)
    assert details.headquarters_address.city == "Basel"
    assert details.headquarters_address.lines == ["St. Alban-Vorstadt 12"]
    assert details.headquarters_address.postal_code == "4052"
    assert details.headquarters_address.country == "CH"
    assert details.headquarters_address.region == "CH-BS"

def test_details_identity_no_parents(setup):
    details = fetch_no_parents(setup)
    assert details.identity.legal_form_id == "2JZ4"
    assert details.identity.registered_as == "CHE200595965"
    assert details.identity.jurisdiction == "CH"
    assert details.identity.registry_id == "RA000548"
    assert details.identity.category == "GENERAL"
    assert details.identity.creation_date == "2014-07-31T00:00:00Z"

def test_details_no_headquarters_address_no_parents(setup):
    body = load_fixture("no_parent_lei_record.json")
    del body["data"]["attributes"]["entity"]["headquartersAddress"]
    details = fetch_no_parents(setup, body)
    assert details.headquarters_address is None

def test_details_direct_parent_links_no_parents(setup):
    details = fetch_no_parents(setup)
    assert setup.urls[1].endswith("/direct-parent-reporting-exception")
    assert setup.urls[2].endswith("/ultimate-parent-reporting-exception")
    assert details.direct_parent.exception.reason == "NO_KNOWN_PERSON"
    assert details.direct_parent.node is None
    assert details.direct_parent.failed_lookups is False
    assert setup.sent == 3

def test_details_ultimate_parent_links_no_parents(setup):
    details = fetch_no_parents(setup)
    assert setup.urls[1].endswith("/direct-parent-reporting-exception")
    assert setup.urls[2].endswith("/ultimate-parent-reporting-exception")
    assert details.ultimate_parent.exception.reason == "NO_KNOWN_PERSON"
    assert details.ultimate_parent.node is None
    assert details.ultimate_parent.failed_lookups is False
    assert setup.sent == 3

def fetch_with_real_parents(setup, body=None, extra=None):
    if body is None:
        body = load_fixture("lei_record_with_parents.json")
    if extra is None:
        extra = [
            fake_response(200, load_fixture("direct_parent_record.json")),
            fake_response(200, load_fixture("ultimate_parent_record.json")),
        ]
    setup.responses = [fake_response(200, body), *extra]
    return get_entity_details("52990056L4CA6PJ3L270")

def test_details_legal_name_with_real_parents(setup):
    details = fetch_with_real_parents(setup)
    assert details.legal_name == "SIEMENS HEALTHCARE"
    assert details.status == "ACTIVE"
    assert details.lei_status == "ISSUED"

def test_details_direct_parent_links_with_real_parents(setup):
    details = fetch_with_real_parents(setup)
    assert setup.urls[1].endswith("/direct-parent")
    assert setup.urls[2].endswith("/ultimate-parent")
    assert details.direct_parent.exception is None
    assert details.direct_parent.node.lei == "W38RGI023J3WT1HWRP32"
    assert details.direct_parent.node.legal_name == "Siemens Aktiengesellschaft"
    assert details.direct_parent.node.country == "DE"
    assert details.direct_parent.node.city == "München"
    assert details.direct_parent.node.status == "ACTIVE"
    assert details.direct_parent.node.lei_status == "ISSUED"
    assert details.direct_parent.node.legal_form_id == "6QQB"
    assert details.direct_parent.failed_lookups is False
    assert setup.sent == 3

def test_details_ultimate_parent_links_with_real_parents(setup):
    details = fetch_with_real_parents(setup)
    assert setup.urls[1].endswith("/direct-parent")
    assert setup.urls[2].endswith("/ultimate-parent")
    assert details.ultimate_parent.exception is None
    assert details.ultimate_parent.node.lei == "W38RGI023J3WT1HWRP32"
    assert details.ultimate_parent.failed_lookups is False
    assert setup.sent == 3

def test_parent_link_outside_gleif_api(setup):
    body = load_fixture("lei_record_with_parents.json")
    body["data"]["relationships"]["direct-parent"]["links"]["lei-record"] = "https://other.example/x"
    with pytest.raises(GleifError, match="outside"):
        fetch_with_real_parents(setup, body)
    assert setup.sent == 1

@pytest.mark.parametrize("status", [404, 500, 503])
def test_parent_link_error_status(setup, status):
    details = fetch_no_parents(setup, extra=[fake_response(status, {"errors": []}), fake_response(status, {"errors": []})])
    assert setup.urls[1].endswith("/direct-parent-reporting-exception")
    assert setup.urls[2].endswith("/ultimate-parent-reporting-exception")
    assert details.legal_name == "Global Legal Entity Identifier Foundation"
    assert details.direct_parent.exception is None
    assert details.direct_parent.node is None
    assert details.direct_parent.failed_lookups is True
    assert details.ultimate_parent.exception is None
    assert details.ultimate_parent.node is None
    assert details.ultimate_parent.failed_lookups is True
    assert setup.sent == 3

def test_details_parent_link_removed_no_parents(setup):
    body = load_fixture("no_parent_lei_record.json")
    del body["data"]["relationships"]
    details = fetch_no_parents(setup, body, extra=[])
    assert details.direct_parent == ParentLink(node=None, exception=None, failed_lookups=False)
    assert details.ultimate_parent == ParentLink(node=None, exception=None, failed_lookups=False)
    assert details.direct_parent.failed_lookups is False

def test_parent_link_empty_200(setup):
    details = fetch_no_parents(setup, extra=[fake_response(200), fake_response(200)])
    assert details.direct_parent.exception is None
    assert details.direct_parent.node is None
    assert details.direct_parent.failed_lookups is True

@pytest.mark.parametrize("status", [404, 500, 503])
def test_details_error_status(setup, status):
    setup.responses = [fake_response(status)]
    with pytest.raises(GleifError, match=f"HTTP {status}"):
        get_entity_details("506700GE1G29325QX363")
    assert setup.sent == 1

def test_details_error_network_down(setup):
    setup.network_down = True
    setup.responses = [fake_response(200, load_fixture("no_parent_lei_record.json"))]
    with pytest.raises(GleifError, match="unreachable"):
        get_entity_details("506700GE1G29325QX363")
    assert setup.sent == 1
