from tools import TOOL_FUNCTIONS, TOOL_SCHEMAS, TOOL_WITH_CONFIRMED_LEI

def schema_of(name):
    # parcourt TOOL_SCHEMAS et retourne le schéma dont ["function"]["name"] == name
    for schema in TOOL_SCHEMAS:
        if schema["function"]["name"] == name:
            return schema
    return None

def test_get_entity_details_is_registered():
    assert "get_entity_details" in TOOL_FUNCTIONS

def test_get_entity_details_has_schema():
    schema = schema_of("get_entity_details")
    assert schema is not None

def test_get_entity_details_schema_has_no_lei_parameter():
    schema = schema_of("get_entity_details")
    assert schema is not None
    assert "lei" not in schema["function"]["parameters"]["properties"]

def test_confirmed_lei_tools_exist_in_registry():
    for tool_name in TOOL_WITH_CONFIRMED_LEI:
        assert tool_name in TOOL_FUNCTIONS
