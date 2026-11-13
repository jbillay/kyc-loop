from dataclasses import dataclass, field

@dataclass
class CandidateEntity:
    lei: str
    legal_name: str
    country: str | None
    city: str | None
    status: str | None        # entity.status (ACTIVE...)
    lei_status: str | None    # registration.status (ISSUED, LAPSED...)

@dataclass
class SearchResult:
    candidates: list[CandidateEntity]
    failed_lookups: int

@dataclass
class Address:
    lines: list[str]
    city: str | None
    region: str | None
    country: str | None
    postal_code: str | None

@dataclass
class LegalIdentity:
    legal_form_id: str | None
    category: str | None
    jurisdiction: str | None
    registry_id: str | None
    registered_as: str | None
    creation_date: str | None

@dataclass
class ReportingException:
    category: str | None
    reason: str | None
    reference: str | None
    valid_from: str | None
    valid_to: str | None

@dataclass
class EntityNode:
    lei: str
    legal_name: str
    country: str| None
    city: str | None
    status: str | None
    lei_status: str | None
    legal_form_id: str | None
    direct_parent_lei: str | None
    parent_exception: ReportingException | None

@dataclass
class ParentLink:
    node: EntityNode | None
    exception: ReportingException | None

@dataclass
class EntityDetails:
    lei: str
    legal_name: str
    direct_parent: ParentLink
    ultimate_parent: ParentLink
    status: str | None
    lei_status: str | None
    legal_address: Address | None
    headquarters_address: Address | None
    identity: LegalIdentity | None
    ancestors: list[EntityNode] = field(default_factory=list)
    descendants: list[EntityNode] = field(default_factory=list)
    descendants_total: int = 0
    truncated: bool = False
    structure_complete: bool = False
    api_calls: int = 0