from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "translation_status.py"


class TranslationStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.run_command("git", "init", "-q")
        self.run_command("git", "config", "user.email", "tests@example.invalid")
        self.run_command("git", "config", "user.name", "Translation status tests")
        (self.repo / "docs" / "nl").mkdir(parents=True)
        (self.repo / ".github").mkdir()
        (self.repo / ".github" / "docs-versions.yml").write_text(
            "versions:\n"
            "  - language: en\n"
            "    branch: release/8.0\n"
            "  - language: nl\n"
            "    branch: translation/8.0/nl\n",
            encoding="utf-8",
        )
        for name, content in {
            "current.md": "current source\n",
            "changed.md": "changed source\n",
            "missing.md": "missing translation\n",
            "unknown.md": "unknown review\n",
        }.items():
            (self.repo / "docs" / name).write_text(content, encoding="utf-8")
        for name in ("current.md", "changed.md", "unknown.md"):
            (self.repo / "docs" / "nl" / name).write_text(
                f"Dutch {name}\n", encoding="utf-8"
            )
        self.run_command("git", "add", ".")
        self.run_command("git", "commit", "-qm", "source and translations")
        self.run_command("git", "branch", "release/8.0")

        current_hash = hashlib.sha256(b"current source\n").hexdigest()
        (self.repo / "translation-status.yml").write_text(
            "schema_version: 1\n"
            "locale: nl\n"
            "source_ref: release/8.0\n"
            "reviewed:\n"
            f"  current.md:\n    source_sha256: {current_hash}\n"
            f"  changed.md:\n    source_sha256: \"{'0' * 64}\"\n",
            encoding="utf-8",
        )
        self.run_command("git", "add", "translation-status.yml")
        self.run_command("git", "commit", "-qm", "translation status")
        self.run_command("git", "branch", "translation/8.0/nl")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_command(
        self, *command: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )

    def tool(
        self, *arguments: str, check: bool = False
    ) -> subprocess.CompletedProcess[str]:
        return self.run_command(
            "python3",
            str(SCRIPT),
            "--locale",
            "nl",
            "--source-ref",
            "release/8.0",
            *arguments,
            check=check,
        )

    def test_report_classifies_all_four_states_and_is_read_only(self) -> None:
        before = (self.repo / "translation-status.yml").read_bytes()
        result = self.tool()
        self.assertEqual(0, result.returncode, result.stderr)
        after = (self.repo / "translation-status.yml").read_bytes()
        self.assertEqual(before, after)
        self.assertIn("Up to date:           1", result.stdout)
        self.assertIn("Needs review:         1", result.stdout)
        self.assertIn("Not translated:       1", result.stdout)
        self.assertIn("Unknown:              1", result.stdout)

    def test_mark_reviewed_only_updates_status_file(self) -> None:
        translation = self.repo / "docs" / "nl" / "unknown.md"
        before = translation.read_bytes()
        result = self.tool("--mark-reviewed", "docs/nl/unknown.md")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(before, translation.read_bytes())
        expected = hashlib.sha256(b"unknown review\n").hexdigest()
        self.assertIn(expected, (self.repo / "translation-status.yml").read_text())
        self.assertIn("Marked reviewed", result.stdout)

    def test_missing_source_ref_has_actionable_error(self) -> None:
        result = self.tool("--source-ref", "does-not-exist", check=False)
        self.assertEqual(2, result.returncode)
        self.assertIn("is not available locally; fetch it first", result.stderr)

    def test_source_ref_falls_back_to_origin_tracking_branch(self) -> None:
        self.run_command(
            "git", "update-ref", "refs/remotes/origin/release/8.0", "release/8.0"
        )
        self.run_command("git", "branch", "-D", "release/8.0")
        result = self.tool()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("English source:    release/8.0", result.stdout)

    def test_invalid_locale_is_rejected(self) -> None:
        result = self.run_command(
            "python3", str(SCRIPT), "--locale", "../nl", check=False
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("invalid locale", result.stderr)

    def test_all_languages_overview_reads_translation_branch(self) -> None:
        before = (self.repo / "translation-status.yml").read_bytes()
        result = self.run_command(
            "python3",
            str(SCRIPT),
            "--all",
            "--source-ref",
            "release/8.0",
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(before, (self.repo / "translation-status.yml").read_bytes())
        self.assertIn("Translation status overview", result.stdout)
        self.assertIn("nl               1             1               1        1", result.stdout)
        self.assertIn("translation/8.0/nl", result.stdout)

    def test_all_languages_falls_back_to_current_worktree(self) -> None:
        self.run_command("git", "branch", "-D", "translation/8.0/nl")
        result = self.run_command(
            "python3", str(SCRIPT), "--all", "--source-ref", "HEAD", check=False
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("worktree (translation/8.0/nl not created)", result.stdout)
        self.assertIn("their existing translations are Unknown", result.stdout)


if __name__ == "__main__":
    unittest.main()
