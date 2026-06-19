import json
import re
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
from paperseek_core.sources.providers import OpenAlexProvider, PaperIdentifiers, PaperRecord, ProviderSearchResult, SearchMetadata


class FakeResponse:
    url = "https://api.openalex.org/works"

    def __init__(self, payload=None, status_code=200):
        self._payload = payload or {"meta": {"count": 0, "page": 1, "per_page": 1}, "results": []}
        self.status_code = status_code
        self.text = "{}"

    def json(self):
        return self._payload


class BatchRankingLlm:
    def __init__(self, calls=None, fail_uid=""):
        self.calls = calls if calls is not None else []
        self.fail_uid = fail_uid
        self.last_response_info = {}

    def fork(self):
        return BatchRankingLlm(self.calls, fail_uid=self.fail_uid)

    def chat(self, messages, temperature=0.3):
        text = messages[-1]["content"]
        uids = re.findall(r"UID: ([^\n]+)", text)
        self.calls.append(tuple(uids))
        if self.fail_uid and self.fail_uid in uids:
            raise RuntimeError("simulated batch failure")
        return json.dumps([
            {"uid": uid, "score": int(uid.replace("W", "")), "reasoning": "ranked"}
            for uid in uids
        ])


def openalex_work(work_id, field_id):
    return {
        "id": f"https://openalex.org/{work_id}",
        "display_name": f"Work {work_id}",
        "primary_topic": {"field": {"id": f"https://openalex.org/fields/{field_id}"}},
        "referenced_works": [],
    }


def ranking_record(index):
    uid = f"W{index:02d}"
    return PaperRecord(uid=uid, title=f"Work {index}", raw={})


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

    def test_agent_ranks_large_candidate_sets_in_parallel_batches(self):
        calls = []
        llm = BatchRankingLlm(calls)
        config = SimpleNamespace(
            data_source="openalex",
            discipline_fields=(),
            expand_citations=False,
            ranking_batch_size=8,
            ranking_concurrency=4,
            openalex_api_key="",
            openalex_email="",
        )
        agent = PaperSeekAgent(config, llm)

        ranked = agent._rank_results("open innovation", [ranking_record(index) for index in range(40)])

        self.assertEqual(len(calls), 4)
        self.assertEqual(sorted(len(call) for call in calls), [10, 10, 10, 10])
        self.assertEqual(ranked[0]["document"].uid, "W39")
        self.assertEqual(ranked[-1]["document"].uid, "W00")

    def test_agent_keeps_results_when_one_parallel_ranking_batch_fails(self):
        calls = []
        llm = BatchRankingLlm(calls, fail_uid="W04")
        config = SimpleNamespace(
            data_source="openalex",
            discipline_fields=(),
            expand_citations=False,
            ranking_batch_size=4,
            ranking_concurrency=2,
            openalex_api_key="",
            openalex_email="",
        )
        agent = PaperSeekAgent(config, llm)

        ranked = agent._rank_results("open innovation", [ranking_record(index) for index in range(12)])

        self.assertEqual(len(ranked), 12)
        self.assertEqual(len(calls), 3)
        self.assertEqual(ranked[0]["document"].uid, "W11")
        failed_batch = {entry["document"].uid: entry for entry in ranked if entry["document"].uid in {"W04", "W05", "W06", "W07"}}
        self.assertTrue(failed_batch)
        self.assertTrue(all(entry["score"] == 0 for entry in failed_batch.values()))

    def test_ranking_stage_events_include_search_context(self):
        class FakeProvider:
            def search(self, query, limit=50, field_ids=()):
                return ProviderSearchResult(
                    metadata=SearchMetadata(total=2, page=1, limit=limit),
                    hits=[ranking_record(0), ranking_record(1)],
                )

        config = SimpleNamespace(
            data_source="openalex",
            discipline_fields=(),
            expand_citations=False,
            ranking_batch_size=8,
            ranking_concurrency=4,
            target_min=1,
            target_max=5,
            max_iterations=1,
            fetch_abstracts=False,
            openalex_api_key="",
            openalex_email="",
        )
        events = []
        agent = PaperSeekAgent(config, BatchRankingLlm())
        agent.provider = FakeProvider()
        agent._generate_query = lambda question: "open innovation"
        agent.search("open innovation", event_handler=events.append)

        ranking_events = [
            event for event in events
            if event.get("type") == "stage" and event.get("stage") == "ranking" and event.get("status") == "processing"
        ]
        self.assertEqual(len(ranking_events), 1)
        payload = ranking_events[0]["data"]
        self.assertEqual(payload["candidate_count"], 2)
        self.assertEqual(payload["final_query"], "open innovation")
        self.assertEqual(payload["total"], 2)
        self.assertEqual(payload["history"][0]["action"], "accept")
        self.assertEqual(payload["source"], "openalex")

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
