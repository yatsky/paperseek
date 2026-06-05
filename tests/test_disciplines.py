import unittest
from unittest.mock import patch

from paperseek_core.disciplines import (
    apply_wos_discipline_filter,
    list_discipline_fields,
    normalize_discipline_ids,
    openalex_field_filter,
    wos_category_clause,
)
from paperseek_core.sources.providers import OpenAlexProvider


class FakeResponse:
    status_code = 200
    text = "{}"
    url = "https://api.openalex.org/works"

    def json(self):
        return {"meta": {"count": 0, "page": 1, "per_page": 1}, "results": []}


class DisciplineMappingTest(unittest.TestCase):
    def test_openalex_field_catalog_has_26_fields(self):
        fields = list_discipline_fields()
        self.assertEqual(len(fields), 26)
        self.assertEqual(fields[6]["id"], "17")
        self.assertEqual(fields[6]["label"], "Computer Science")

    def test_normalize_accepts_ids_urls_and_labels(self):
        values = ["https://openalex.org/fields/17", "Business, Management and Accounting", "17"]
        self.assertEqual(normalize_discipline_ids(values), ("17", "14"))

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


if __name__ == "__main__":
    unittest.main()
