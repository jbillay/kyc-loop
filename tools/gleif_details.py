import config
from tools.gleif_client import GleifClient, GleifError
from models import Address, EntityDetails, LegalIdentity, ParentLink, ReportingException

def _to_address(raw: dict | None) -> Address | None:
    if raw is None:
        return None
    return Address(
        lines=raw.get("addressLines", []),
        city=raw.get("city", None),
        region=raw.get("region", None),
        country=raw.get("country", None),
        postal_code=raw.get("postalCode", None)
    )

def _to_legal_identity(raw: dict | None) -> LegalIdentity | None:
    if raw is None:
        return None
    return LegalIdentity(
        legal_form_id=raw.get("legalForm", {}).get("id", None),
        category=raw.get("category", None),
        jurisdiction=raw.get("jurisdiction", None),
        registry_id=raw.get("registeredAt", {}).get("id", None),
        registered_as=raw.get("registeredAs", None),
        creation_date=raw.get("creationDate", None)
    )

def _to_exception(raw: dict | None) -> ReportingException | None:
    if raw is None:
        return None
    attributes = raw.get("attributes", {})
    return ReportingException(
        category=attributes.get("category", None),
        # reason, reference, valid_from (validFrom), valid_to (validTo)
    )

def _to_entity_details(client, record: dict) -> EntityDetails:
    attributes = record.get("attributes", {})
    relationships = record.get("relationships", {})
    lei = attributes.get("lei", "")
    legal_name = attributes.get("entity", {}).get("legalName", {}).get("name", None)
    status = attributes.get("entity", {}).get("status", None)
    lei_status = attributes.get("registration", {}).get("status", None)
    direct_parent = relationships.get("direct-parent", {})
    ultimate_parent = relationships.get("ultimate-parent", {})
    legal_address = _to_address(attributes.get("entity", {}).get("legalAddress", None))
    headquarters_address = _to_address(attributes.get("entity", {}).get("headquartersAddress", None))
    identity = _to_legal_identity(attributes.get("entity", {}))
    return EntityDetails(
        lei=lei,
        legal_name=legal_name,
        status=status,
        lei_status=lei_status,
        direct_parent=_fetch_parent_link(client, direct_parent.get("links", {}).get("reporting-exception", None)),
        ultimate_parent=_fetch_parent_link(client, ultimate_parent.get("links", {}).get("reporting-exception", None)),
        legal_address=legal_address,
        headquarters_address=headquarters_address,
        identity=identity
    )

def _fetch_parent_link(client, link: str) -> ParentLink:
    if not link.startswith(config.GLEIF_API_URL):
        raise GleifError(f"Unexpected link outside GLEIF API: {link}")
    path = link[len(config.GLEIF_API_URL):]
    print(f"Fetching parent link: {path}")
    status, body = client.get(path)
    return ParentLink(
        node=None,
        exception=None
    )

def get_entity_details(lei: str):
    client = GleifClient()
    status, body = client.get(f"/lei-records/{lei}")
    if status != 200:
        raise GleifError(f"GLEIF details fetch failed (HTTP {status})")
    return _to_entity_details(client, body.get("data", {}))