"""Unit tests for the CI build-metadata injector (SOURCE-build provenance).

These tests gate ``scripts/build_pages_metadata.py`` only. The clinical
evidence gate (E-005) and other readiness decisions are untouched. Tests
use isolated temporary directories so they never touch the live ``docs/``
tree or any checked-in receipt.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_pages_metadata import (  # noqa: E402
    MetadataError,
    SENTINEL,
    build_metadata,
    build_run_url,
    inject_metadata,
    render_metadata_script,
)


VALID_40 = "0123abcdef" + ("0" * 30)  # 40-char hex
VALID_40_ALT = "deadbeef" * 5  # 40-char hex


def _minimal_html() -> str:
    return "<!doctype html><html><head></head><body></body></html>"


class BuildMetadataValidationTests(unittest.TestCase):
    """Validation behaviour for the SOURCE-build provenance inputs."""

    valid_args = {
        "commit": VALID_40,
        "built_at": "2026-09-07T12:00:00Z",
        "repository": "stancsz/frailty-index-deficit-accumulation-model",
        "run_id": "987654321",
    }

    def test_build_metadata_emits_source_only_provenance(self) -> None:
        payload = build_metadata(**self.valid_args)
        self.assertEqual(
            set(payload.keys()),
            {
                "commit",
                "short_commit",
                "built_at",
                "repository",
                "run_id",
                "run_url",
                "source",
            },
        )
        self.assertEqual(payload["source"], "ci")
        self.assertEqual(payload["short_commit"], "0123abc")
        self.assertEqual(
            payload["run_url"],
            "https://github.com/stancsz/frailty-index-deficit-accumulation-model/actions/runs/987654321",
        )
        forbidden = {
            "verify_job_passed",
            "python_tests_collected",
            "node_tests_collected",
            "passed",
            "ok",
            "ready",
            "tests_collected",
        }
        self.assertTrue(forbidden.isdisjoint(payload.keys()), payload)

    def test_build_metadata_rejects_non_hex_commit(self) -> None:
        with self.assertRaises(MetadataError):
            build_metadata(**dict(self.valid_args, commit="NOT-A-SHA".ljust(40, "0")))

    def test_build_metadata_rejects_short_commit(self) -> None:
        with self.assertRaises(MetadataError):
            build_metadata(**dict(self.valid_args, commit="abc"))

    def test_build_metadata_rejects_uppercase_commit(self) -> None:
        with self.assertRaises(MetadataError):
            build_metadata(**dict(self.valid_args, commit=("A" * 40)))

    def test_build_metadata_rejects_blank_commit(self) -> None:
        with self.assertRaises(MetadataError):
            build_metadata(**dict(self.valid_args, commit="   "))

    def test_build_metadata_rejects_malformed_repository(self) -> None:
        for bad_repo in [
            "",
            "/repo",
            "owner/",
            "owner/with space",
            "owner",
            "owner/repo/extra",
            "owner/repo<script>",
            "owner/.repo",
            "owner/_repo",
            "owner/repo@1",
        ]:
            with self.subTest(repository=bad_repo):
                with self.assertRaises(MetadataError):
                    build_metadata(**dict(self.valid_args, repository=bad_repo))

    def test_build_metadata_rejects_non_numeric_run_id(self) -> None:
        for bad_id in ["", "0", "abc", "-1", "1.5", "  ", "123456789012345678901"]:
            with self.subTest(run_id=bad_id):
                with self.assertRaises(MetadataError):
                    build_metadata(**dict(self.valid_args, run_id=bad_id))

    def test_build_metadata_rejects_non_utc_built_at(self) -> None:
        for bad_ts in [
            "",
            "2026-09-07 12:00:00",
            "2026-09-07T12:00:00+00:00",
            "2026-09-07T12:00:00",
            "not-a-date",
        ]:
            with self.subTest(built_at=bad_ts):
                with self.assertRaises(MetadataError):
                    build_metadata(**dict(self.valid_args, built_at=bad_ts))

    def test_build_run_url_format(self) -> None:
        self.assertEqual(
            build_run_url("owner/repo", "42"),
            "https://github.com/owner/repo/actions/runs/42",
        )


class InjectMetadataRenderingTests(unittest.TestCase):
    """Injection behaviour for the SOURCE-build provenance script."""

    def test_inject_metadata_writes_typed_safe_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "index.html"
            html_path.write_text(_minimal_html(), encoding="utf-8")
            metadata = build_metadata(
                commit=VALID_40,
                built_at="2026-09-07T12:00:00Z",
                repository="owner/repo",
                run_id="42",
            )
            inject_metadata(html_path=html_path, metadata=metadata)
            rendered = html_path.read_text(encoding="utf-8")
            self.assertIn(SENTINEL, rendered)
            match = re.search(
                r"<script>" + re.escape(SENTINEL) + r"(.*?)</script>", rendered
            )
            self.assertIsNotNone(match)
            payload = match.group(1).strip().rstrip(";")
            self.assertTrue(payload.startswith("window.__BUILD_META__ = "))
            parsed = json.loads(payload[len("window.__BUILD_META__ = ") :])
            self.assertEqual(parsed["commit"], VALID_40)
            self.assertEqual(parsed["source"], "ci")
            self.assertEqual(parsed["short_commit"], "0123abc")
            self.assertNotIn("</script>", parsed["run_url"].lower())

    def test_inject_metadata_rejects_double_injection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "index.html"
            metadata = build_metadata(
                commit=VALID_40,
                built_at="2026-09-07T12:00:00Z",
                repository="owner/repo",
                run_id="42",
            )
            script = render_metadata_script(metadata)
            html_path.write_text(
                "<html><head>" + script + "</head><body></body></html>",
                encoding="utf-8",
            )
            with self.assertRaises(MetadataError):
                inject_metadata(html_path=html_path, metadata=metadata)

    def test_inject_metadata_rejects_html_without_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "index.html"
            html_path.write_text("<html><body>oops</body></html>", encoding="utf-8")
            metadata = build_metadata(
                commit=VALID_40,
                built_at="2026-09-07T12:00:00Z",
                repository="owner/repo",
                run_id="42",
            )
            with self.assertRaises(MetadataError):
                inject_metadata(html_path=html_path, metadata=metadata)

    def test_render_metadata_script_refuses_script_breakout(self) -> None:
        with self.assertRaises(MetadataError):
            render_metadata_script(
                {
                    "commit": VALID_40,
                    "built_at": "2026-09-07T12:00:00Z",
                    "repository": "owner/repo",
                    "run_id": "1",
                    "run_url": "https://github.com/owner/repo/actions/runs/1</script>",
                    "source": "ci",
                }
            )


class WorkflowPlacementTests(unittest.TestCase):
    """The Pages workflow must inject provenance BEFORE uploading the artifact."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow_text = (ROOT / ".github" / "workflows" / "pages.yml").read_text(
            encoding="utf-8"
        )

    def test_workflow_runs_metadata_script_before_upload_artifact(self) -> None:
        upload_idx = self.workflow_text.find("actions/upload-pages-artifact")
        script_idx = self.workflow_text.find("scripts/build_pages_metadata.py")
        self.assertGreater(upload_idx, 0, "upload-pages-artifact step missing")
        self.assertGreater(script_idx, 0, "build_pages_metadata.py step missing")
        self.assertLess(script_idx, upload_idx)

    def test_workflow_passes_required_env_to_metadata_script(self) -> None:
        required = [
            "${{ github.sha }}",
            "${{ github.repository }}",
            "${{ github.run_id }}",
            "scripts/build_pages_metadata.py",
            "--commit",
            "--repository",
            "--run-id",
            "--built-at",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, self.workflow_text)

    def test_workflow_keeps_a_separate_verify_job(self) -> None:
        self.assertIn("jobs:", self.workflow_text)
        self.assertRegex(
            self.workflow_text,
            r"(?m)^  verify:",
            "verify job must remain before the deploy job",
        )

    def test_workflow_does_not_inject_receipt_or_test_counts(self) -> None:
        # SOURCE-build provenance only; no receipt or test-count coupling.
        self.assertNotIn("test-receipt.json", self.workflow_text)
        self.assertNotIn("python_tests_collected", self.workflow_text)
        self.assertNotIn("node_tests_collected", self.workflow_text)


class CliSmokeTests(unittest.TestCase):
    """Whole-script invocation against an isolated HTML file."""

    def test_cli_writes_metadata_into_isolated_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "index.html"
            html_path.write_text(_minimal_html(), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_pages_metadata.py"),
                    "--commit",
                    VALID_40_ALT,
                    "--built-at",
                    "2026-09-07T12:34:56Z",
                    "--repository",
                    "owner/repo",
                    "--run-id",
                    "7",
                    "--html",
                    str(html_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            stdout_payload = json.loads(result.stdout)
            rendered = html_path.read_text(encoding="utf-8")
            self.assertEqual(stdout_payload["commit"], VALID_40_ALT)
            self.assertEqual(stdout_payload["source"], "ci")
            self.assertIn(SENTINEL, rendered)
            self.assertIn("deadbeef", rendered)

    def test_cli_fails_loudly_on_invalid_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "index.html"
            html_path.write_text(_minimal_html(), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_pages_metadata.py"),
                    "--commit",
                    "nope",
                    "--built-at",
                    "2026-09-07T12:34:56Z",
                    "--repository",
                    "owner/repo",
                    "--run-id",
                    "7",
                    "--html",
                    str(html_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertNotIn(SENTINEL, html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
