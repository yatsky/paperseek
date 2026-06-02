import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillLauncherTest(unittest.TestCase):
    def test_launcher_delegates_to_full_package(self):
        result = subprocess.run(
            [sys.executable, "skills/paperseek/scripts/paperseek.py", "sources", "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual([item["id"] for item in payload["sources"]], ["openalex", "crossref", "wos"])

    def test_launcher_install_help_is_available(self):
        result = subprocess.run(
            [sys.executable, "skills/paperseek/scripts/paperseek.py", "--install-help"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PaperSeek package installation", result.stdout)
        self.assertIn("python -m pip install -e .", result.stdout)

    def test_skill_readme_documents_current_layout(self):
        readme = (ROOT / "skills" / "README.md").read_text(encoding="utf-8")
        self.assertIn("scripts/", readme)
        self.assertIn("paperseek.py", readme)
        self.assertIn("api/index.py", readme)
        self.assertIn("vercel.json", readme)
        self.assertIn("Dockerfile", readme)


if __name__ == "__main__":
    unittest.main()
