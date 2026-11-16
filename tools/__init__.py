
from .gleif_details import get_entity_details
from .gleif_search import gleif_search_entity

TOOL_WITHOUT_LEI = ["gleif_search_entity", "ask_user_confirmation"]
TOOL_WITH_CONFIRMED_LEI = ["get_entity_details"]

TOOL_FUNCTIONS = {
    "gleif_search_entity": gleif_search_entity,
    "get_entity_details": get_entity_details,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "gleif_search_entity",
            "description": "Searches for an entity by name and returns matching candidates that needs to be reviewed by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the entity to search for."}
                },
                "required": ["name"]
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_entity_details",
            "description": "Retrieves the details and parent entities of the entity confirmed by the user. Takes no argument.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []

            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ask_user_confirmation",
            "description": "Asks the user to confirm the entity they want to select before starting the KYC process.",
            "parameters": {"type": "object", "properties": {
                "user_message": {"type": "string", "description": "The message to display to the user to help with the confirmation."},
            }},
        },
    },
]
