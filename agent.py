
import json
import config
from models import SearchResult
from session import Session
from tools import TOOL_SCHEMAS, TOOL_FUNCTIONS, TOOL_WITH_CONFIRMED_LEI, TOOL_WITHOUT_LEI
from collections.abc import Callable
from events import Event, Report, ToolCall, ToolResult, Error, NeedConfirmation
from dataclasses import asdict, is_dataclass

def _default(obj):
    if is_dataclass(obj):
        return asdict(obj)
    return str(obj)

def _serialize(obj):
    if isinstance(obj, str):
        return obj
    return json.dumps(obj, default=_default, ensure_ascii=False)

def _confirm_entity(session: Session, ask: Callable[[NeedConfirmation], str| None]) -> tuple[str, bool]:
    is_error = False
    if session.candidates is None or len(session.candidates) == 0:
        return_result = "Search for candidates first."
        is_error = True
    else:
        existing_leis = [c.lei for c in session.candidates]
        returned_lei = ask(NeedConfirmation(candidates=session.candidates))
        if returned_lei and returned_lei in existing_leis:
            session.confirmed_lei = returned_lei
            return_result = f"User confirmed LEI: {returned_lei}"
        elif returned_lei:
            session.confirmed_lei = None
            return_result = "User did not confirm a valid LEI. Ask the user to select a LEI from the provided candidates."
            is_error = True
        else:
            session.confirmed_lei = None
            return_result = "User did not confirm any LEI. Stop the process and ask the user to select a LEI from the provided candidates."
            is_error = True
    return return_result, is_error

def error_missing_lei(name: str) -> tuple[str, bool]:
    return_result = f"The tool {name} is not allowed to execute without a confirmed LEI. Call gleif_search, then ask_user_confirmation, before using this tool."
    return return_result, True

def get_tool_result(session: Session, name: str, args: dict) -> tuple[str, bool]:
    is_error = False
    result = TOOL_FUNCTIONS[name](**args)  # appel de la fonction correspondante
    if result is not None:
        return_result = _serialize(result)
    else:
        return_result = "No result returned."
        is_error = True
    if isinstance(result, SearchResult):
        session.candidates = result.candidates
        session.confirmed_lei = None
    return return_result, is_error

def run_agent(session: Session, user_input: str, client, emit: Callable[[Event], None], ask: Callable[[NeedConfirmation], str| None]) -> None:
    session.messages.append({"role": "user", "content": user_input})

    for turn in range(config.max_turns):
        response = client.chat.completions.create(
            model=config.model,
            messages=session.messages,
            tools=TOOL_SCHEMAS)
        message = response.choices[0].message
        session.messages.append(message)

        if not message.tool_calls:
            emit(Report(content=message.content))
            return

        for call in message.tool_calls:
            try:
                tool_call = None
                name = call.function.name
                if name == "ask_user_confirmation":
                    tool_call = ToolCall(name=name, arguments={})
                    emit(tool_call)
                    (return_result, is_error) = _confirm_entity(session, ask)
                elif name not in TOOL_WITHOUT_LEI and not session.confirmed_lei:
                    args = json.loads(call.function.arguments)
                    tool_call = ToolCall(name=name, arguments=args)
                    emit(tool_call)
                    (return_result, is_error) = error_missing_lei(tool_call.name)
                else:
                    args = json.loads(call.function.arguments)
                    if name in TOOL_WITH_CONFIRMED_LEI:
                        args["lei"] = session.confirmed_lei
                    tool_call = ToolCall(name=name, arguments=args)
                    emit(tool_call)
                    (return_result, is_error) = get_tool_result(session, name, args)
                emit(ToolResult(tool_call=tool_call, result=return_result, is_error=is_error))
            except Exception as e:
                return_result = f"Error occurred while executing {name}: {e}"
                emit(ToolResult(tool_call=tool_call, result=return_result, is_error=True))
            session.messages.append({"role": "tool", "content": return_result, "tool_call_id": call.id})
    emit(Error(message="Maximum turns reached without a final answer."))