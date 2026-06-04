import os
import tempfile
import unittest
from pathlib import Path

from paperseek import config_store


ENV_KEYS = (
    "DATA_SOURCE",
    "WOS_API_KEY",
    "OPENALEX_API_KEY",
    "OPENALEX_EMAIL",
    "CROSSREF_EMAIL",
    "LLM_API_KEY",
    "LLM_PROVIDER",
    "LLM_API_TYPE",
    "LLM_MODEL",
    "LLM_BASE_URL",
)


class ConfigStoreTest(unittest.TestCase):
    def test_set_list_and_mask_config_value(self):
        previous = {key: os.environ.get(key) for key in ("PAPERSEEK_CONFIG_FILE", *ENV_KEYS)}
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["PAPERSEEK_CONFIG_FILE"] = str(Path(tmp) / "config.json")
            for key in ENV_KEYS:
                os.environ.pop(key, None)
            try:
                config_store.set_config_value("LLM_API_KEY", "sk-test-123456")
                entries = config_store.list_config_entries()
                row = next(item for item in entries if item["key"] == "LLM_API_KEY")
                self.assertTrue(row["configured"])
                self.assertEqual(row["source"], "user_config")
                self.assertEqual(row["value"], "sk-t...3456")
                config_store.unset_config_value("LLM_API_KEY")
                self.assertNotIn("LLM_API_KEY", config_store.read_config())
            finally:
                for key, value in previous.items():
                    os.environ.pop(key, None)
                    if value is not None:
                        os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
