import unittest
from types import SimpleNamespace
from unittest.mock import patch

from paperseek_core.agent import PaperSeekAgent
from paperseek_core.disciplines import (
    apply_wos_discipline_filter,
    list_discipline_fields,
    normalize_discipline_ids,
    openalex_field_filter,
    wos_category_clause,
)
from paperseek_core.sources.providers import OpenAlexProvider, PaperIdentifiers, PaperRecord


class FakeResponse:
    url = "https://api.openalex.org/works"

    def __init__(self, payload=None, status_code=200):
        self._payload = payload or {"meta": {"count": 0, "page": 1, "per_page": 1}, "results": []}
        self.status_code = status_code
        self.text = "{}"

    def json(self):
        return self._payload


def openalex_work(work_id, field_id):
    return {
        "id": f"https://openalex.org/{work_id}",
        "display_name": f"Work {work_id}",
        "primary_topic": {"field": {"id": f"https://openalex.org/fields/{field_id}"}},
        "referenced_works": [],
    }


class DisciplineMappingTest(unittest.TestCase):
    def test_openalex_field_catalog_has_26_fields(self):
        fields = list_discipline_fields()
        self.assertEqual(len(fields), 26)
        self.assertEqual(fields[6]["id"], "17")
        self.assertEqual(fields[6]["label"], "Computer Science")

    def test_normalize_accepts_ids_urls_and_labels(self):
        values = ["https://openalex.org/fields/17", "Business, Management and Accounting", "17"]
        self.assertEqual(normalize_discipline_ids(values), ("17", "14"))

    def test_normalize_accepts_semicolon_separated_labels_with_commas(self):
        values = "Computer Science;Business, Management and Accounting"
        self.assertEqual(normalize_discipline_ids(values), ("17", "14"))

    def test_normalize_keeps_comma_support_for_pure_id_lists(self):
        self.assertEqual(normalize_discipline_ids("17,14"), ("17", "14"))

    def test_source_specific_mappings(self):
        self.assertEqual(openalex_field_filter(["17", "14"]), "primary_topic.field.id:17|14")
        self.assertIn("WC=(", wos_category_clause(["17"]))
        self.assertIn("Computer Science, Artificial Intelligence", wos_category_clause(["17"]))

    def test_wos_filter_is_appended_once(self):
        query = apply_wos_discipline_filter("TS=(open innovation)", ["17"])
        self.assertIn("TS=(open innovation) AND WC=(", query)
        self.assertEqual(apply_wos_discipline_filter(query, ["17"]), query)

    def test_openalex_provider_sends_field_filter(self):
        captured = {}

        def fake_get(_, __, *, params=None, headers=None, timeout=30, query="", attempts=3):
            captured.update(params or {})
            return FakeResponse(), {"method": "GET", "url": FakeResponse.url, "status": 200, "elapsed_ms": 1}

        with patch("paperseek_core.sources.providers.get_with_retries", side_effect=fake_get):
            result = OpenAlexProvider().search("open innovation", limit=1, field_ids=("17", "14"))

        self.assertEqual(result.metadata.total, 0)
        self.assertEqual(captured["filter"], "primary_topic.field.id:17|14")

    def test_agent_passes_discipline_fields_to_openalex_citation_expansion(self):
        captured = {}

        class FakeOpenAlexProvider(OpenAlexProvider):
            def citation_neighbors_with_graph(self, seeds, per_seed=4, max_records=40, field_ids=None):
                captured["field_ids"] = field_ids
                return {"records": [], "nodes": [], "edges": []}

        config = SimpleNamespace(
            data_source="openalex",
            discipline_fields=("17", "14"),
            expand_citations=True,
            citation_seed_count=1,
            citation_per_seed=2,
            citation_max_records=10,
            target_max=5,
            openalex_api_key="",
            openalex_email="",
        )
        agent = PaperSeekAgent(config, object())
        seed = PaperRecord(
            uid="https://openalex.org/Wseed",
            title="Seed",
            identifiers=PaperIdentifiers(openalex="https://openalex.org/Wseed"),
            raw={"referenced_works": []},
        )
        agent.provider = FakeOpenAlexProvider()
        agent._rank_results = lambda question, candidates: [{"document": seed, "score": 10}]

        agent._prepare_candidates("open innovation", [seed])

        self.assertEqual(captured["field_ids"], ("17", "14"))

    def test_openalex_citation_expansion_filters_neighbors_by_field(self):
        captured = {}

        def fake_get(_, url, *, params=None, headers=None, timeout=30, query="", attempts=3):
            if url.endswith("/Wback_in"):
                return FakeResponse(openalex_work("Wback_in", "17")), {"method": "GET", "url": url, "status": 200, "elapsed_ms": 1}
            if url.endswith("/Wback_out"):
                return FakeResponse(openalex_work("Wback_out", "14")), {"method": "GET", "url": url, "status": 200, "elapsed_ms": 1}
            captured["forward_filter"] = (params or {}).get("filter", "")
            return FakeResponse({
                "meta": {"count": 2, "page": 1, "per_page": 2},
                "results": [openalex_work("Wforward_in", "17"), openalex_work("Wforward_out", "14")],
            }), {"method": "GET", "url": url, "status": 200, "elapsed_ms": 1}

        seed = PaperRecord(
            uid="https://openalex.org/Wseed",
            title="Seed",
            identifiers=PaperIdentifiers(openalex="https://openalex.org/Wseed"),
            raw={
                "referenced_works": [
                    "https://openalex.org/Wback_in",
                    "https://openalex.org/Wback_out",
                ]
            },
        )

        with patch("paperseek_core.sources.providers.get_with_retries", side_effect=fake_get):
            citation_data = OpenAlexProvider().citation_neighbors_with_graph(
                [seed],
                per_seed=4,
                max_records=10,
                field_ids=("17",),
            )

        self.assertEqual(captured["forward_filter"], "cites:Wseed,primary_topic.field.id:17")
        record_ids = {record.uid for record in citation_data["records"]}
        self.assertIn("https://openalex.org/Wback_in", record_ids)
        self.assertIn("https://openalex.org/Wforward_in", record_ids)
        self.assertNotIn("https://openalex.org/Wback_out", record_ids)
        self.assertNotIn("https://openalex.org/Wforward_out", record_ids)
        node_ids = {node["id"] for node in citation_data["nodes"]}
        self.assertIn("https://openalex.org/Wback_in", node_ids)
        self.assertIn("https://openalex.org/Wforward_in", node_ids)
        self.assertNotIn("https://openalex.org/Wback_out", node_ids)
        self.assertNotIn("https://openalex.org/Wforward_out", node_ids)


if __name__ == "__main__":
    unittest.main()
