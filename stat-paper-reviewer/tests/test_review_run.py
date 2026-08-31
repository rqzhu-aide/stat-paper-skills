import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "review_run.py"


def load_module():
    spec = importlib.util.spec_from_file_location("review_run", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReviewRunTests(unittest.TestCase):
    def run_cli(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_doctor_reports_protocol_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            main.write_text("paper", encoding="utf-8")
            result = self.run_cli(
                "doctor", "--root", base / "bundle", "--main", main
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(
                payload["protocol"]["skill_name"], "stat-paper-reviewer"
            )
            self.assertEqual(payload["protocol"]["skill_version"], "1.2")
            self.assertGreater(payload["protocol"]["file_count"], 2)
            self.assertRegex(payload["protocol"]["sha256"], r"^[0-9a-f]{64}$")

    def test_init_is_portable_from_unrelated_cwd_with_spaces_and_unicode(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_dir = base / "source space"
            source_dir.mkdir()
            main = source_dir / "manuscript-α.pdf"
            supplement = source_dir / "supplement.pdf"
            main.write_bytes(b"main")
            supplement.write_bytes(b"main")
            root = base / "review bundle"
            unrelated = base / "other cwd"
            unrelated.mkdir()
            result = self.run_cli(
                "init", "--root", root, "--profile", "full",
                "--main", main, "--supplement", supplement, cwd=unrelated,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "review_run.json").read_text(encoding="utf-8"))
            self.assertTrue(all("\\" not in item["path"] for item in manifest["inputs"]))
            self.assertEqual(manifest["inputs"][1]["duplicate_of"], "main-001")
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(manifest["workflow_version"], "1.2")
            self.assertIn("literature", manifest["required_stages"])
            self.assertEqual(
                manifest["protocol"]["skill_name"], "stat-paper-reviewer"
            )
            self.assertEqual(manifest["protocol"]["skill_version"], "1.2")
            self.assertTrue(
                all(
                    item["path"].startswith("protocol/")
                    and "\\" not in item["path"]
                    for item in manifest["protocol"]["files"]
                )
            )
            self.assertIn(
                "SKILL.md",
                {item["source_path"] for item in manifest["protocol"]["files"]},
            )
            moved = base / "moved review"
            root.rename(moved)
            status = self.run_cli("status", "--root", moved, cwd=unrelated)
            self.assertEqual(status.returncode, 0, status.stderr)
            status_payload = json.loads(status.stdout)
            self.assertEqual(status_payload["integrity"], "ok")
            self.assertEqual(
                status_payload["skill"],
                {
                    "name": "stat-paper-reviewer",
                    "version": "1.2",
                    "protocol_sha256": manifest["protocol"]["sha256"],
                },
            )

    def test_protocol_snapshot_tampering_fails_integrity(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            main.write_text("paper", encoding="utf-8")
            root = base / "bundle"
            initialized = self.run_cli(
                "init", "--root", root, "--profile", "focused", "--main", main
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            manifest = json.loads(
                (root / "review_run.json").read_text(encoding="utf-8")
            )
            skill_record = next(
                item
                for item in manifest["protocol"]["files"]
                if item["source_path"] == "SKILL.md"
            )
            snapshot = root.joinpath(*skill_record["path"].split("/"))
            snapshot.write_text(
                snapshot.read_text(encoding="utf-8") + "\nchanged\n",
                encoding="utf-8",
            )

            status = self.run_cli("status", "--root", root)
            self.assertNotEqual(status.returncode, 0)
            payload = json.loads(status.stdout)
            self.assertEqual(payload["integrity"], "failed")
            self.assertTrue(
                any("protocol file" in error for error in payload["errors"]),
                payload["errors"],
            )

    def test_full_literature_limit_requires_acknowledgment(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            artifact = base / "stage.md"
            report = base / "report.md"
            main.write_text("paper", encoding="utf-8")
            artifact.write_text("durable stage evidence", encoding="utf-8")
            report.write_text(
                "Novelty was not assessable because no search route was available.",
                encoding="utf-8",
            )
            root = base / "bundle"
            initialized = self.run_cli("init", "--root", root, "--main", main)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            for stage in (
                "source_map",
                "first_reader",
                "fact_base",
                "claim_chain",
            ):
                recorded = self.run_cli(
                    "stage", "--root", root, "--name", stage,
                    "--artifact", artifact,
                )
                self.assertEqual(recorded.returncode, 0, recorded.stderr)
            missing_note = self.run_cli(
                "stage", "--root", root, "--name", "literature",
                "--artifact", artifact, "--outcome", "not_assessable",
            )
            self.assertNotEqual(missing_note.returncode, 0)
            self.assertIn("--note is required", missing_note.stderr)
            literature = self.run_cli(
                "stage", "--root", root, "--name", "literature",
                "--artifact", artifact, "--outcome", "not_assessable",
                "--note", "No scholarly search route was available.",
            )
            self.assertEqual(literature.returncode, 0, literature.stderr)
            for stage in ("patterned_prose", "synthesis", "qa"):
                recorded = self.run_cli(
                    "stage", "--root", root, "--name", stage,
                    "--artifact", artifact,
                )
                self.assertEqual(recorded.returncode, 0, recorded.stderr)

            rejected = self.run_cli(
                "finalize", "--root", root, "--report", report
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("cannot finalize without --acknowledge-limits", rejected.stderr)
            accepted = self.run_cli(
                "finalize", "--root", root, "--report", report,
                "--acknowledge-limits",
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            status = self.run_cli("status", "--root", root)
            payload = json.loads(status.stdout)
            self.assertEqual(payload["status"], "finalized")
            self.assertEqual(payload["limited_stages"], ["literature"])

    def test_failed_initialization_leaves_no_partial_bundle(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            main.write_text("paper", encoding="utf-8")
            root = base / "bundle"
            args = module.build_parser().parse_args(
                ["init", "--root", str(root), "--main", str(main)]
            )
            with mock.patch.object(module, "atomic_json", side_effect=OSError("interrupted")):
                with self.assertRaises(OSError):
                    module.init_run(args)
            self.assertFalse(root.exists())
            self.assertEqual(list(base.glob(".bundle.init-*")), [])

    def test_existing_empty_root_is_restored_when_commit_fails(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            main.write_text("paper", encoding="utf-8")
            root = base / "bundle"
            root.mkdir()
            args = module.build_parser().parse_args(
                ["init", "--root", str(root), "--main", str(main)]
            )
            original_replace = module.os.replace

            def fail_directory_commit(source, destination):
                if Path(destination) == root:
                    raise OSError("commit failed")
                return original_replace(source, destination)

            with mock.patch.object(module.os, "replace", side_effect=fail_directory_commit):
                with self.assertRaisesRegex(OSError, "commit failed"):
                    module.init_run(args)
            self.assertTrue(root.is_dir())
            self.assertEqual(list(root.iterdir()), [])
            self.assertEqual(list(base.glob(".bundle.init-*")), [])

    def test_finalize_fails_closed_until_required_stages_exist(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            report = base / "report.md"
            main.write_text("paper", encoding="utf-8")
            report.write_text("review", encoding="utf-8")
            root = base / "bundle"
            initialized = self.run_cli("init", "--root", root, "--main", main)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            finalized = self.run_cli("finalize", "--root", root, "--report", report)
            self.assertNotEqual(finalized.returncode, 0)
            self.assertIn("incomplete required stages", finalized.stderr)

    def test_manifest_cannot_omit_profile_required_stages(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            main.write_text("paper", encoding="utf-8")
            root = base / "bundle"
            initialized = self.run_cli("init", "--root", root, "--main", main)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)

            manifest_path = root / "review_run.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["required_stages"].remove("qa")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            status = self.run_cli("status", "--root", root)
            self.assertNotEqual(status.returncode, 0)
            self.assertIn(
                "required_stages does not match the selected profile",
                status.stderr,
            )
            self.assertNotIn("Traceback", status.stderr)

    def test_focused_lifecycle_finalizes_and_detects_later_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            artifact = base / "stage.md"
            report = base / "report.md"
            main.write_text("paper", encoding="utf-8")
            artifact.write_text("durable stage evidence", encoding="utf-8")
            report.write_text("bounded review", encoding="utf-8")
            root = base / "bundle"
            initialized = self.run_cli(
                "init", "--root", root, "--profile", "focused", "--main", main
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            for stage in ("source_map", "fact_base", "synthesis", "qa"):
                recorded = self.run_cli(
                    "stage", "--root", root, "--name", stage,
                    "--artifact", artifact,
                )
                self.assertEqual(recorded.returncode, 0, recorded.stderr)
            finalized = self.run_cli(
                "finalize", "--root", root, "--report", report
            )
            self.assertEqual(finalized.returncode, 0, finalized.stderr)
            status = self.run_cli("status", "--root", root)
            self.assertEqual(status.returncode, 0, status.stderr)
            payload = json.loads(status.stdout)
            self.assertEqual(payload["status"], "finalized")
            self.assertEqual(payload["integrity"], "ok")

            copied_main = next((root / "inputs").iterdir())
            copied_main.write_text("tampered", encoding="utf-8")
            tampered = self.run_cli("status", "--root", root)
            self.assertNotEqual(tampered.returncode, 0)
            self.assertEqual(json.loads(tampered.stdout)["integrity"], "failed")

    def test_delegated_stage_requires_producer(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            artifact = base / "source-map.md"
            main.write_text("paper", encoding="utf-8")
            artifact.write_text("source map", encoding="utf-8")
            root = base / "bundle"
            initialized = self.run_cli(
                "init", "--root", root, "--profile", "focused",
                "--delegated", "--main", main,
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            rejected = self.run_cli(
                "stage", "--root", root, "--name", "source_map",
                "--artifact", artifact,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("--producer is required", rejected.stderr)

    def test_replacing_upstream_stage_invalidates_synthesis_and_qa(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            artifact = base / "stage.md"
            report = base / "report.md"
            main.write_text("paper", encoding="utf-8")
            artifact.write_text("first evidence", encoding="utf-8")
            report.write_text("review", encoding="utf-8")
            root = base / "bundle"
            initialized = self.run_cli(
                "init", "--root", root, "--profile", "focused", "--main", main
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            for stage in ("source_map", "fact_base", "synthesis", "qa"):
                recorded = self.run_cli(
                    "stage", "--root", root, "--name", stage,
                    "--artifact", artifact,
                )
                self.assertEqual(recorded.returncode, 0, recorded.stderr)

            artifact.write_text("revised evidence", encoding="utf-8")
            replaced = self.run_cli(
                "stage", "--root", root, "--name", "fact_base",
                "--artifact", artifact,
            )
            self.assertEqual(replaced.returncode, 0, replaced.stderr)
            self.assertIn(
                "invalidated downstream stages: synthesis, qa", replaced.stdout
            )

            status = self.run_cli("status", "--root", root)
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(
                ["synthesis", "qa"], json.loads(status.stdout)["missing_stages"]
            )
            finalized = self.run_cli(
                "finalize", "--root", root, "--report", report
            )
            self.assertNotEqual(finalized.returncode, 0)
            self.assertIn("incomplete required stages", finalized.stderr)

    def test_status_rejects_input_redirected_outside_bundle(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            main.write_text("paper", encoding="utf-8")
            root = base / "bundle"
            initialized = self.run_cli("init", "--root", root, "--main", main)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            manifest = json.loads(
                (root / "review_run.json").read_text(encoding="utf-8")
            )
            bundled_input = root.joinpath(
                *manifest["inputs"][0]["path"].split("/")
            )
            bundled_input.unlink()
            try:
                bundled_input.symlink_to(main)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")

            status = self.run_cli("status", "--root", root)
            self.assertNotEqual(status.returncode, 0)
            payload = json.loads(status.stdout)
            self.assertEqual("failed", payload["integrity"])
            self.assertTrue(
                any("redirected path" in error for error in payload["errors"]),
                payload["errors"],
            )

    def test_verify_record_rejects_resolved_target_outside_bundle(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "bundle"
            target = root / "inputs" / "main.txt"
            target.parent.mkdir(parents=True)
            target.write_text("paper", encoding="utf-8")
            external = base / "external.txt"
            external.write_text("paper", encoding="utf-8")
            record = {
                "path": "inputs/main.txt",
                "size": target.stat().st_size,
                "sha256": module.sha256(target),
            }
            original_resolve = module.Path.resolve

            def redirected_resolve(path, strict=False):
                if path == target:
                    return external
                return original_resolve(path, strict=strict)

            with mock.patch.object(
                module.Path, "resolve", new=redirected_resolve
            ):
                errors = module.verify_record(root, record, "input main-001")

            self.assertEqual(
                [
                    "input main-001: redirected path leaves the review bundle: "
                    "inputs/main.txt"
                ],
                errors,
            )

    def test_malformed_manifest_is_rejected_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "review_run.json").write_text("[]\n", encoding="utf-8")
            result = self.run_cli("status", "--root", root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must contain a JSON object", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_nested_malformed_stage_artifacts_are_rejected_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            main = base / "main.txt"
            main.write_text("paper", encoding="utf-8")
            root = base / "bundle"
            initialized = self.run_cli("init", "--root", root, "--main", main)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            manifest_path = root / "review_run.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["stages"]["intake"]["artifacts"] = {"not": "a list"}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = self.run_cli("status", "--root", root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("artifacts must be a list of objects", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
