from tools.gleif_details import get_entity_details
from tests.helpers import fake_response, load_fixture

def fetch(setup, body=None, extra=()):
    if body is None:
        body = load_fixture("no_parent_lei_record.json")
    setup.responses = [fake_response(200, body), *extra]
    return get_entity_details("506700GE1G29325QX363")

def test_details_legal_name(setup):
    details = fetch(setup)
    assert details.legal_name == "Global Legal Entity Identifier Foundation"
    assert details.status == "ACTIVE"
    assert details.lei_status == "ISSUED"

def test_details_legal_address(setup):
    details = fetch(setup)
    assert details.legal_address.city == "Basel"
    assert details.legal_address.lines == ["St. Alban-Vorstadt 12"]
    assert details.legal_address.postal_code == "4052"
    assert details.legal_address.country == "CH"
    assert details.legal_address.region == "CH-BS"

def test_details_identity(setup):
    details = fetch(setup)
    assert details.identity.legal_form_id == "2JZ4"
    assert details.identity.registered_as == "CHE200595965"
    assert details.identity.jurisdiction == "CH"
    assert details.identity.registry_id == "RA000548"
    assert details.identity.category == "GENERAL"
    assert details.identity.creation_date == "2014-07-31T00:00:00Z"

def test_details_no_headquarters_address(setup):
    body = load_fixture("lei_record.json")
    del body["data"]["attributes"]["entity"]["headquartersAddress"]
    details = fetch(setup, body)
    assert details.headquarters_address is None

def test_details_direct_parent_links(setup):
    extra=[fake_response(200, load_fixture("direct_parent_reporting_exception.json")), fake_response(200, load_fixture("ultimate_parent_reporting_exception.json"))]
    details = fetch(setup, body=None, extra=extra)
    assert setup.urls[1].endswith("/direct-parent-reporting-exception")
    assert setup.urls[2].endswith("/ultimate-parent-reporting-exception")
    assert details.direct_parent.exception.reason == "NO_KNOWN_PERSON"
    assert details.direct_parent.node is None
    assert setup.sent == 3

def test_details_ultimate_parent_links(setup):
    extra=[fake_response(200, load_fixture("direct_parent_reporting_exception.json")), fake_response(200, load_fixture("ultimate_parent_reporting_exception.json"))]
    details = fetch(setup, body=None, extra=extra)
    assert setup.urls[1].endswith("/direct-parent-reporting-exception")
    assert setup.urls[2].endswith("/ultimate-parent-reporting-exception")
    assert details.ultimate_parent.exception.reason == "NO_KNOWN_PERSON"
    assert details.ultimate_parent.node is None
    assert setup.sent == 3