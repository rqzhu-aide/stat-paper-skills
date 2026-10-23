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

    def init_bundle(self, base, *, profile="focused", required=()):
        main = base / "main.txt"
        artifact = base / "stage.md"
        report = base / "report.md"
        main.write_text("paper", encoding="utf-8")
        artifact.write_text("durable stage evidence", encoding="utf-8")
        report.write_text("bounded review", encoding="utf-8")
        root = base / "bundle"
        extra = [argument for stage in required for argument in ("--require-stage", stage)]
        result = self.run_cli(
            "init", "--root", root, "--profile", profile, "--main", main, *extra
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return root, artifact, report

    def record_stage(self, root, artifact, stage):
        result = self.run_cli(
            "stage", "--root", root, "--name", stage, "--artifact", artifact
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_focused_required_analyses_need_fact_base_without_first_reader(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, artifact, report = self.init_bundle(
                Path(temporary), required=("literature", "patterned_prose")
            )
            self.record_stage(root, artifact, "source_map")
            for stage in ("literature", "patterned_prose"):
                rejected = self.run_cli(
                    "stage", "--root", root, "--name", stage, "--artifact", artifact
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("incomplete dependencies: fact_base", rejected.stderr)
            self.record_stage(root, artifact, "fact_base")
            for stage in ("literature", "patterned_prose", "synthesis", "qa"):
                self.record_stage(root, artifact, stage)
            manifest = load_module().load_manifest(root)
            self.assertNotIn("first_reader", manifest["stages"])
            result = self.run_cli("finalize", "--root", root, "--report", report)
            self.assertEqual(result.returncode, 0, result.stderr)
            status = self.run_cli("status", "--root", root)
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(json.loads(status.stdout)["status"], "finalized")

    def test_focused_declared_first_reader_blocks_both_analyses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, artifact, _ = self.init_bundle(
                Path(temporary), required=("first_reader", "literature", "patterned_prose")
            )
            for stage in ("source_map", "fact_base"):
                self.record_stage(root, artifact, stage)
            for stage in ("literature", "patterned_prose"):
                rejected = self.run_cli(
                    "stage", "--root", root, "--name", stage, "--artifact", artifact
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("incomplete dependencies: first_reader", rejected.stderr)
            self.record_stage(root, artifact, "first_reader")
            for stage in ("literature", "patterned_prose"):
                self.record_stage(root, artifact, stage)

    def test_focused_replacement_invalidates_dependent_evidence(self):
        cases = {
            "fact_base": {"claim_chain", "literature", "patterned_prose", "synthesis", "qa"},
            "first_reader": {"literature", "patterned_prose", "synthesis", "qa"},
        }
        for changed, expected in cases.items():
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as temporary:
                root, artifact, report = self.init_bundle(Path(temporary))
                for stage in (
                    "source_map", "fact_base", "first_reader", "claim_chain",
                    "literature", "patterned_prose", "synthesis", "qa",
                ):
                    self.record_stage(root, artifact, stage)
                before = load_module().load_manifest(root)["stages"]
                artifact.write_text("revised evidence", encoding="utf-8")
                self.record_stage(root, artifact, changed)
                after = load_module().load_manifest(root)["stages"]
                self.assertEqual(set(before) - set(after), expected)
                self.assertNotEqual(before[changed]["artifacts"], after[changed]["artifacts"])
                self.assertEqual(after[changed]["outcome"], "complete")
                for preserved in set(before) - expected - {changed}:
                    self.assertEqual(before[preserved], after[preserved])
                rejected = self.run_cli("finalize", "--root", root, "--report", report)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("incomplete required stages", rejected.stderr)

    def test_new_optional_evidence_invalidates_existing_synthesis_and_qa(self):
        cases = {
            "first_reader": {"literature", "patterned_prose", "synthesis", "qa"},
            "claim_chain": {"synthesis", "qa"},
        }
        for added, expected in cases.items():
            with self.subTest(added=added), tempfile.TemporaryDirectory() as temporary:
                root, artifact, report = self.init_bundle(Path(temporary))
                for stage in (
                    "source_map", "fact_base", "literature", "patterned_prose", "synthesis", "qa",
                ):
                    self.record_stage(root, artifact, stage)
                before = load_module().load_manifest(root)["stages"]
                self.assertNotIn(added, before)
                self.record_stage(root, artifact, added)
                after = load_module().load_manifest(root)["stages"]
                self.assertEqual(set(before) - set(after), expected)
                self.assertEqual(after[added]["outcome"], "complete")
                for preserved in set(before) - expected:
                    self.assertEqual(before[preserved], after[preserved])
                rejected = self.run_cli("finalize", "--root", root, "--report", report)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("incomplete required stages", rejected.stderr)

    def test_full_first_reader_prerequisites_and_invalidation_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, artifact, _ = self.init_bundle(Path(temporary), profile="full")
            self.record_stage(root, artifact, "source_map")
            for stage in ("literature", "patterned_prose"):
                rejected = self.run_cli(
                    "stage", "--root", root, "--name", stage, "--artifact", artifact
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("incomplete dependencies: first_reader", rejected.stderr)
            # Full analysis still needs only first-reader evidence, not a fact-base record.
            for stage in (
                "first_reader", "literature", "patterned_prose", "fact_base",
                "claim_chain", "synthesis", "qa",
            ):
                self.record_stage(root, artifact, stage)
            before = load_module().load_manifest(root)["stages"]
            self.record_stage(root, artifact, "first_reader")
            after = load_module().load_manifest(root)["stages"]
            self.assertEqual(
                set(before) - set(after),
                {"fact_base", "claim_chain", "literature", "patterned_prose", "synthesis", "qa"},
            )
            self.assertEqual(set(after), {"intake", "source_map", "first_reader"})

    def test_old_schema_two_manifests_load_without_rewriting_or_stage_closure(self):
        module = load_module()
        for required in ((), ("literature", "patterned_prose", "first_reader")):
            with self.subTest(required=required), tempfile.TemporaryDirectory() as temporary:
                root, _, _ = self.init_bundle(Path(temporary), required=required)
                manifest_path = root / "review_run.json"
                manifest = module.load_manifest(root)
                manifest["workflow_version"] = "1.2"
                manifest["protocol"]["skill_version"] = "1.2.1"
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                before = manifest_path.read_bytes()
                loaded = module.load_manifest(root)
                self.assertEqual(loaded["workflow_version"], "1.2")
                self.assertEqual(loaded["protocol"]["skill_version"], "1.2.1")
                self.assertEqual(loaded["required_stages"], manifest["required_stages"])
                self.assertEqual(manifest_path.read_bytes(), before)

    def test_snapshotted_helper_runs_from_unrelated_cwd(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root, _, _ = self.init_bundle(base)
            unrelated = base / "unrelated"
            unrelated.mkdir()
            snapshot = root / "protocol" / "scripts" / "review_run.py"
            result = subprocess.run(
                [sys.executable, str(snapshot), "status", "--root", str(root)],
                cwd=unrelated, capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["integrity"], "ok")

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
                payload["protocol"]["skill_name"], "stat-paper-review"
            )
            self.assertEqual(payload["protocol"]["skill_version"], "1.2.9")
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
            self.assertEqual(manifest["workflow_version"], "1.3")
            self.assertIn("literature", manifest["required_stages"])
            self.assertEqual(
                manifest["protocol"]["skill_name"], "stat-paper-review"
            )
            self.assertEqual(manifest["protocol"]["skill_version"], "1.2.9")
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
                    "name": "stat-paper-review",
                    "version": "1.2.9",
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

    def test_verify_record_reports_root_and_target_resolution_access_errors(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            target = root / "inputs" / "main.txt"
            record = {"path": "inputs/main.txt", "size": 5, "sha256": "unused"}
            for denied_path in (root, target):
                with self.subTest(denied_path=denied_path):
                    detail = f"access denied at {denied_path.name}"

                    def denied_resolve(path, strict=False):
                        if path == denied_path:
                            if path == target:
                                self.assertTrue(strict)
                            raise PermissionError(detail)
                        return path

                    with (
                        mock.patch.object(module.Path, "is_file", return_value=True),
                        mock.patch.object(module.Path, "resolve", new=denied_resolve),
                        mock.patch.object(module.Path, "stat") as file_stat,
                        mock.patch.object(module.os, "lstat") as component_stat,
                        mock.patch.object(module, "sha256") as digest,
                    ):
                        errors = module.verify_record(root, record, "input main-001")
                    self.assertEqual(
                        errors,
                        [f"input main-001: cannot verify physical containment for inputs/main.txt: {detail}"],
                    )
                    self.assertNotIn("leaves the review bundle", errors[0])
                    file_stat.assert_not_called()
                    component_stat.assert_not_called()
                    digest.assert_not_called()

    def test_verify_record_rejects_unreadable_path_components_before_hashing(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            record = {"path": "inputs/main.txt", "size": 5, "sha256": "unused"}
            with (
                mock.patch.object(module.Path, "is_file", return_value=True),
                mock.patch.object(module.Path, "resolve", new=lambda path, strict=False: path),
                mock.patch.object(module.os, "lstat", side_effect=PermissionError("component denied")),
                mock.patch.object(module.Path, "stat") as file_stat,
                mock.patch.object(module, "sha256") as digest,
            ):
                errors = module.verify_record(root, record, "input main-001")
            self.assertEqual(
                errors,
                ["input main-001: unreadable path component inputs/main.txt: component denied"],
            )
            file_stat.assert_not_called()
            digest.assert_not_called()

    def test_verify_record_detects_size_and_hash_changes(self):
        module = load_module()
        for replacement, expected in (
            ("other", ["hash changed"]),
            ("longer content", ["size changed", "hash changed"]),
        ):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / "main.txt"
                target.write_text("paper", encoding="utf-8")
                record = {
                    "path": "main.txt", "size": target.stat().st_size,
                    "sha256": module.sha256(target),
                }
                target.write_text(replacement, encoding="utf-8")
                self.assertEqual(
                    module.verify_record(root, record, "input main-001"),
                    [f"input main-001: {reason}: main.txt" for reason in expected],
                )

    def test_finalization_rejects_changed_input_even_with_all_stages_complete(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, artifact, report = self.init_bundle(Path(temporary))
            for stage in ("source_map", "fact_base", "synthesis", "qa"):
                self.record_stage(root, artifact, stage)
            manifest = load_module().load_manifest(root)
            target = root.joinpath(*manifest["inputs"][0]["path"].split("/"))
            target.write_text("other", encoding="utf-8")
            rejected = self.run_cli("finalize", "--root", root, "--report", report)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("run integrity check failed", rejected.stderr)
            self.assertIn("hash changed", rejected.stderr)
            self.assertEqual(load_module().load_manifest(root)["status"], "in_progress")

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
