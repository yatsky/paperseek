from __future__ import annotations

from dataclasses import dataclass, field

from paperseek_core.disciplines import normalize_discipline_ids


@dataclass
class SearchConfig:
    data_source: str = "openalex"
    target_min: int = 5
    target_max: int = 50
    max_iterations: int = 5
    search_field: str = ""
    discipline_fields: tuple[str, ...] = field(default_factory=tuple)
    expand_citations: bool = True
    fetch_abstracts: bool = False
    citation_seed_count: int = 3
    citation_per_seed: int = 4
    citation_max_records: int = 40


@dataclass
class LLMConfig:
    provider: str = "openai"
    api_type: str = "openai_responses"
    model: str = "gpt-5.4-mini"
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""


@dataclass
class SourceConfig:
    wos_api_key: str = ""
    wos_db: str = "WOS"
    openalex_api_key: str = ""
    openalex_email: str = ""
    crossref_email: str = ""


@dataclass
class RuntimeConfig:
    data_source: str
    target_min: int
    target_max: int
    max_iterations: int
    search_field: str
    discipline_fields: tuple[str, ...]
    expand_citations: bool
    fetch_abstracts: bool
    citation_seed_count: int
    citation_per_seed: int
    citation_max_records: int
    llm_provider: str
    llm_api_type: str
    llm_model: str
    llm_base_url: str
    llm_api_key: str
    wos_api_key: str
    wos_db: str
    openalex_api_key: str
    openalex_email: str
    crossref_email: str


def build_runtime_config(
    search: SearchConfig | None = None,
    source: SourceConfig | None = None,
    llm: LLMConfig | None = None,
) -> RuntimeConfig:
    search = search or SearchConfig()
    source = source or SourceConfig()
    llm = llm or LLMConfig()
    return RuntimeConfig(
        data_source=(search.data_source or "openalex").lower(),
        target_min=search.target_min,
        target_max=search.target_max,
        max_iterations=search.max_iterations,
        search_field=search.search_field,
        discipline_fields=normalize_discipline_ids(search.discipline_fields),
        expand_citations=search.expand_citations,
        fetch_abstracts=search.fetch_abstracts,
        citation_seed_count=search.citation_seed_count,
        citation_per_seed=search.citation_per_seed,
        citation_max_records=search.citation_max_records,
        llm_provider=(llm.provider or "openai").lower(),
        llm_api_type=(llm.api_type or "openai_responses").lower(),
        llm_model=llm.model,
        llm_base_url=llm.base_url,
        llm_api_key=llm.api_key,
        wos_api_key=source.wos_api_key,
        wos_db=source.wos_db or "WOS",
        openalex_api_key=source.openalex_api_key,
        openalex_email=source.openalex_email,
        crossref_email=source.crossref_email,
    )
