# KYC Investigator Agent

A framework-free AI agent that investigates a legal entity for KYC/AML purposes.
Built from scratch in Python (no LangChain, LlamaIndex, CrewAI...) as a hands-on way to learn Python and agentic AI: agent loop, tool use, human-in-the-loop, sub-agents, evals.

All data used for development and tests is **fictional or public**. No real client data.

## How it works

1. The user enters an entity name.
2. The agent searches **GLEIF** and proposes candidates.
3. A **human confirms** the entity (HITL).
4. The agent investigates autonomously over several turns (web, sanctions, memory).
5. It computes a justified risk score and writes a **Markdown report** with cited sources.

Key point: the call sequence is never hard-coded. **The model decides which tool to call at each turn.**

## Tech stack

- Python 3.11+ (developed on 3.12), `venv`
- LLM: Google Gemini (free tier) through its OpenAI-compatible endpoint, using the official `openai` SDK
- `requests`, `python-dotenv`, `pytest`
- Later: FastAPI + Server-Sent Events, GitHub Actions

## Quick start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# create a .env file with your Gemini key
python main.py
python -m pytest
```

## Progress

Last updated: 2026-11-15

| # | Milestone | Status |
|---|-----------|--------|
| 1 | Simple API call | Done |
| 2 | Conversation loop with history | Done |
| 3 | First tool + agent loop | Done |
| 4 | Events + CLI (no `print()` in the agent) | Done |
| 5 | GLEIF + HITL in CLI | In progress |
| 6 | Investigation tools as sub-agents + skills | Not started |
| 7 | Web UI (FastAPI + SSE) | Not started |
| 8 | Evals + CI/CD (GitHub Actions) | Not started |

### Milestone 5 detail

- [x] GLEIF client (rate limit, retries on 429, call budget, error handling)
- [x] `gleif_search_entity` with partial-failure tracking
- [x] HITL confirmation + guard-rail (no investigation tool before confirmation)
- [x] `get_entity_details` function: record, addresses, identity, direct and ultimate parent (tested)
- [ ] Wire `get_entity_details` into the agent (confirmed LEI injected by code, never by the model)
- [ ] Entity hierarchy: children, pagination, depth/node/call limits
- [ ] System prompt update (new tool, `failed_lookups`)
- [ ] Milestone wrap-up

### Tests

36 tests passing (`python -m pytest`): GLEIF client, search, details, agent guard-rail.

## Changelog

Newest first. Every commit adds a line here.

| Date | Commit | Summary |
|------|--------|---------|
| 2026-11-15 | README | Add README with progress tracking |
| 2026-11-15 | `659a084` | Add `get_entity_details` with parent links and error handling |
| 2026-11-14 | `b5284a3` | Initial commit: milestones 1-5 in progress |

## Contributing rule

Every commit must update this README (progress table, checklist, test count, changelog).
