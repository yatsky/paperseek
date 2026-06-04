import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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


class CliManagementTest(unittest.TestCase):
    def run_cli(self, *args, env=None, cwd=None):
        merged_env = os.environ.copy()
        merged_env["PYTHONIOENCODING"] = "utf-8"
        python_path = [str(ROOT)]
        if merged_env.get("PYTHONPATH"):
            python_path.append(merged_env["PYTHONPATH"])
        merged_env["PYTHONPATH"] = os.pathsep.join(python_path)
        if env:
            merged_env.update(env)
        return subprocess.run(
            [sys.executable, "-m", "paperseek.cli", *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=merged_env,
            cwd=cwd,
        )

    def test_sources_json_contract(self):
        result = self.run_cli("sources", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual([item["id"] for item in payload["sources"]], ["openalex", "crossref", "wos"])

    def test_config_set_list_unset_uses_requested_config_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_file = str(Path(tmp) / "paperseek-config.json")
            env = {key: "" for key in ENV_KEYS}
            env.update({"PAPERSEEK_CONFIG_FILE": config_file, "PAPERSEEK_DOTENV_DISABLED": "1"})

            set_result = self.run_cli("config", "set", "LLM_API_KEY", "sk-test-abcdef", env=env)
            self.assertEqual(set_result.returncode, 0, set_result.stderr)

            list_result = self.run_cli("config", "list", "--json", env=env)
            self.assertEqual(list_result.returncode, 0, list_result.stderr)
            payload = json.loads(list_result.stdout)
            row = next(item for item in payload["entries"] if item["key"] == "LLM_API_KEY")
            self.assertEqual(row["value"], "sk-t...cdef")
            self.assertEqual(row["source"], "user_config")

            unset_result = self.run_cli("config", "unset", "LLM_API_KEY", env=env)
            self.assertEqual(unset_result.returncode, 0, unset_result.stderr)

            list_after_unset = self.run_cli("config", "list", "--json", env=env)
            self.assertEqual(list_after_unset.returncode, 0, list_after_unset.stderr)
            payload = json.loads(list_after_unset.stdout)
            self.assertFalse(any(item["key"] == "LLM_API_KEY" for item in payload["entries"]))

    def test_cli_loads_dotenv_from_working_directory_before_user_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "\n".join([
                    "DATA_SOURCE=openalex",
                    "OPENALEX_API_KEY=oa-env-test",
                    "LLM_PROVIDER=deepseek",
                    "LLM_API_TYPE=openai_chat",
                    "LLM_MODEL=deepseek-test",
                    "LLM_BASE_URL=https://api.deepseek.com",
                    "LLM_API_KEY=sk-env-test",
                ]),
                encoding="utf-8",
            )
            config_path = str(Path(tmp) / "paperseek-config.json")
            clean_env = {key: "" for key in ENV_KEYS}
            clean_env["PAPERSEEK_CONFIG_FILE"] = config_path

            result = self.run_cli("doctor", "--source", "openalex", "--json", env=clean_env, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            summaries = [check["summary"] for check in payload["checks"]]
            self.assertIn("LLM provider 'deepseek' is supported.", summaries)
            self.assertIn("Source-specific required configuration is present or not required.", summaries)


if __name__ == "__main__":
    unittest.main()
