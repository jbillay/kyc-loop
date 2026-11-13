from models import CandidateEntity, SearchResult
from tools.gleif_client import GleifError, GleifClient

def _to_candidate_entity(record: dict) -> CandidateEntity:
    attributes = record.get("attributes", {})
    entity = attributes.get("entity", {})
    lei = attributes.get("lei", "")
    legal_name = entity.get("legalName", {}).get("name", None)
    country = entity.get("legalAddress", {}).get("country", None)
    city = entity.get("legalAddress", {}).get("city", None)
    status = entity.get("status", None)
    lei_status = attributes.get("registration", {}).get("status", None)
    return CandidateEntity(
        lei=lei,
        legal_name=legal_name,
        country=country,
        city=city,
        status=status,
        lei_status=lei_status
    )

def _fuzzy_search(client: GleifClient, name: str) -> list[dict]:
    lei_entities = []
    status, body = client.get("/fuzzycompletions",
                            **{"field": "entity.legalName", "q": name})
    if status != 200:
        raise GleifError(f"GLEIF search failed (HTTP {status})")
    original_entities = body.get("data", [])
    for entity in original_entities:
        if entity.get('relationships'):
            lei_entities.append(entity)
    return lei_entities

def _fetch_record(client: GleifClient, lei: str) -> CandidateEntity | None:
    status, body = client.get(f"/lei-records/{lei}")
    if status != 200:
        return None
    return _to_candidate_entity(body.get("data", {}))

def gleif_search_entity(name: str) -> SearchResult:
    entities = []
    failed_lookups = 0
    client = GleifClient()
    fuzzy_results = _fuzzy_search(client, name)
    nb_lei_returned = len(fuzzy_results)
    for result in fuzzy_results:
        lei = result['relationships']['lei-records']['data']['id']
        if lei:
            record = _fetch_record(client, lei)
            if record:
                entities.append(record)
            else:
                failed_lookups += 1
    if failed_lookups > 0 and nb_lei_returned == failed_lookups:
        raise GleifError("All LEI lookups failed.")
    return SearchResult(candidates=entities, failed_lookups=failed_lookups)