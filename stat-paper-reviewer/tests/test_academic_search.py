import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "academic_search.py"


def load_module():
    spec = importlib.util.spec_from_file_location("academic_search", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Response:
    def __init__(self, data):
        self.data = json.dumps(data).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.data


class AcademicSearchTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.module.API_KEY = "test-key"

    def test_api_key_is_required_and_input_params_are_not_mutated(self):
        self.module.API_KEY = None
        params = {"search": "query"}
        with self.assertRaisesRegex(RuntimeError, "API key is required"):
            self.module._add_api_key(params)
        self.assertEqual(params, {"search": "query"})

        self.module.API_KEY = "test-key"
        enriched = self.module._add_api_key(params)
        self.assertEqual(enriched["api_key"], "test-key")
        self.assertEqual(params, {"search": "query"})

    def test_name_resolution_never_merges_records(self):
        candidates = [
            {
                "id": "https://openalex.org/A1",
                "display_name": "A Researcher",
                "works_count": 20,
                "last_known_institutions": [{"display_name": "Example University"}],
            },
            {
                "id": "https://openalex.org/A2",
                "display_name": "A Researcher",
                "works_count": 10,
                "last_known_institutions": [{"display_name": "Example University"}],
            },
        ]
        with mock.patch.object(self.module, "fetch_author_candidates", return_value=candidates):
            result = self.module.resolve_author("A Researcher")
        self.assertEqual(result["ids"], ["A1"])
        self.assertEqual(len(result["candidates"]), 2)

    def test_search_uses_key_and_preserves_status_and_full_abstract(self):
        words = {"word": list(range(600))}
        payload = {
            "results": [
                {
                    "title": "A paper",
                    "doi": "https://doi.org/10.1/example",
                    "authorships": [{"author": {"display_name": "Author"}}],
                    "publication_year": 2026,
                    "publication_date": "2026-01-01",
                    "cited_by_count": 1,
                    "primary_location": {
                        "version": "publishedVersion",
                        "source": {"display_name": "Proceedings", "type": "conference"},
                    },
                    "type": "proceedings-article",
                    "is_retracted": True,
                    "open_access": {"is_oa": True},
                    "abstract_inverted_index": words,
                    "id": "https://openalex.org/W1",
                    "relevance_score": 1.0,
                }
            ]
        }
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            return Response(payload)

        with mock.patch.object(self.module.urllib.request, "urlopen", side_effect=fake_urlopen):
            results = self.module.search("query", limit=10)
        self.assertIn("api_key=test-key", captured["url"])
        self.assertIn("per_page=10", captured["url"])
        self.assertEqual(results[0]["source_type"], "conference")
        self.assertEqual(results[0]["version"], "publishedVersion")
        self.assertTrue(results[0]["is_retracted"])
        self.assertGreater(len(results[0]["abstract"]), 500)


if __name__ == "__main__":
    unittest.main()
