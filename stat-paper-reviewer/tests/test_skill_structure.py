from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
SKILL = ROOT / "SKILL.md"
REFERENCES = ROOT / "references"


def markdown_files() -> list[Path]:
    return [SKILL, *sorted(REFERENCES.glob("*.md"))]


def heading_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = re.sub(r"[`*_]", "", match.group(1))
        slug = re.sub(r"[^\w\s-]", "", heading.casefold())
        slug = re.sub(r"[\s-]+", "-", slug).strip("-")
        if not slug:
            continue
        duplicate = counts.get(slug, 0)
        counts[slug] = duplicate + 1
        anchors.add(slug if duplicate == 0 else f"{slug}-{duplicate}")
    return anchors


class SkillStructureTests(unittest.TestCase):
    def test_frontmatter_description_is_a_quoted_scalar(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        parts = skill.split("---", 2)
        self.assertEqual(len(parts), 3)
        match = re.search(r"(?m)^description:\s*(.+?)\s*$", parts[1])
        self.assertIsNotNone(match)
        assert match is not None
        description = json.loads(match.group(1))
        self.assertIsInstance(description, str)
        self.assertLessEqual(len(description), 800)

    def test_local_markdown_links_and_anchors_resolve(self) -> None:
        failures: list[str] = []
        for path in markdown_files():
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
                raw = match.group(1)
                if "://" in raw or raw.startswith("mailto:"):
                    continue
                file_part, _, anchor = raw.partition("#")
                target = path if not file_part else (path.parent / file_part).resolve()
                if not target.is_file():
                    failures.append(
                        f"{path.relative_to(ROOT)}: missing target {raw}"
                    )
                    continue
                if anchor and anchor not in heading_anchors(target):
                    failures.append(
                        f"{path.relative_to(ROOT)}: missing anchor {raw}"
                    )
        self.assertEqual(failures, [])

    def test_release_version_matches_readme(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        skill_version = re.search(r'(?m)^  version: "([^"]+)"$', skill)
        readme_version = re.search(
            r"(?m)^\| `stat-paper-reviewer` \| v([^ |]+) \|$",
            readme,
        )
        self.assertIsNotNone(skill_version)
        self.assertIsNotNone(readme_version)
        assert skill_version is not None and readme_version is not None
        self.assertEqual(skill_version.group(1), readme_version.group(1))

    def test_runtime_metadata_covers_reviewer_tests(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "The reviewer helper and tests also require Python 3.10 or later.",
            readme,
        )
        self.assertIn(
            "python -m unittest discover -s stat-paper-reviewer/tests",
            readme,
        )

    def test_eval_definitions_are_unique_and_fixtures_exist(self) -> None:
        eval_path = ROOT / "evals" / "evals.json"
        payload = json.loads(eval_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["skill_name"], "stat-paper-reviewer")
        evals = payload["evals"]
        ids = [item["id"] for item in evals]
        names = [item["eval_name"] for item in evals]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))
        failures: list[str] = []
        for item in evals:
            if len(item.get("assertions", [])) < 3:
                failures.append(f"{item['eval_name']}: fewer than three assertions")
            for raw in item.get("files", []):
                if not (eval_path.parent / raw).is_file():
                    failures.append(f"{item['eval_name']}: missing fixture {raw}")
        self.assertEqual(failures, [])

    def test_evaluation_artifacts_are_scoped_to_reviewer_package(self) -> None:
        results = ROOT / "evals" / "results"
        expected = {
            "stat-paper-reviewer-eval-review.html",
            "stat-paper-reviewer-evaluation.md",
        }
        self.assertTrue(
            expected.issubset(
                {path.name for path in results.iterdir() if path.is_file()}
            )
        )
        for name in expected:
            self.assertFalse((REPO_ROOT / name).exists())


if __name__ == "__main__":
    unittest.main()
