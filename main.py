from openai import OpenAI
import config
import time
from session import Session
from agent import run_agent
from events import Event, NeedConfirmation, Report, ToolCall, ToolResult, Error

client = OpenAI(api_key=config.key, base_url=config.base_url)

session = Session()
session.messages.append({"role": "system", "content": config.SYSTEM_PROMPT})

class AgentMonitoring:
    def __init__(self):
        self.nb_tool_calls = 0
        self.start_time = None
    def start_timer(self):
        self.start_time = time.perf_counter()
    def summary(self):
        elapsed_time = time.perf_counter() - self.start_time
        print(f"Total tool calls: {self.nb_tool_calls}, Time taken: {elapsed_time:.2f} seconds")
    def emit(self, event: Event) -> None:
        if isinstance(event, Report):
            print("Assistant:", event.content)
        elif isinstance(event, ToolCall):
            print("Tool called:", event.name, event.arguments)
            self.nb_tool_calls += 1
        elif isinstance(event, ToolResult):
            if event.is_error:
                print("Error:", event.result)
            else:
                print("Tool result:", event.result)
        elif isinstance(event, Error):
            print("Error:", event.message)
        else:
            print("Unknown event type:", event)

def ask_user_for_lei(need_confirmation: NeedConfirmation) -> str | None:
    print("Candidates for confirmation:")
    for i, candidate in enumerate(need_confirmation.candidates, start=1):
        print(f"{i}) LEI: {candidate.lei}, Legal Name: {candidate.legal_name}, Country: {candidate.country}, LEI STATUS: {candidate.lei_status}")
    print("0) None of the displayed candidates are valid.")
    while True:
        text = input("Please select the correct entity:")
        try:
            selected_option = int(text)
            if selected_option == 0:
                return_lei = None
                break
            elif 1 <= selected_option <= len(need_confirmation.candidates):
                return_lei = need_confirmation.candidates[selected_option - 1].lei
                break
            else:
                print("Please enter a valid number")
                continue
        except ValueError:
            print("Please enter a valid number")
            continue
    return return_lei

if __name__ == "__main__":
    while True:
        user_input = input("> ")
        if user_input.lower() == "quit":
            break
        monitoring = AgentMonitoring()
        monitoring.start_timer()
        run_agent(session, user_input, client, monitoring.emit, ask_user_for_lei)
        monitoring.summary()