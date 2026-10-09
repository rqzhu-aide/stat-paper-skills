"""The legacy bundle CLI must not rebuild the promoted proof-check runtime."""

import contextlib
import io
import unittest
from unittest.mock import patch

import build_paper_core_bundles as builder


class BundleTargetTests(unittest.TestCase):
    def test_supported_cli_routes_only_target_graphify(self):
        expected = {"proof-graphify": builder.ROOT.parent / "proof-graphify"}
        self.assertEqual(builder.PACKAGES, expected)
        for arguments in ([], ["--package", "proof-graphify"], ["--check"],
                          ["--check", "--package", "proof-graphify"]):
            with self.subTest(arguments=arguments):
                with patch.object(builder, "build", return_value={"ok": True}) as build, \
                        patch.object(builder, "check", return_value={"ok": True}) as check, \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(builder.main(arguments), 0)
                selected, unused = (check, build) if "--check" in arguments else (build, check)
                selected.assert_called_once_with(expected)
                unused.assert_not_called()

    def test_proofcheck_is_rejected_before_build_or_check(self):
        for arguments in (["--package", "stat-proof-check"],
                          ["--check", "--package", "stat-proof-check"]):
            with self.subTest(arguments=arguments):
                with patch.object(builder, "build") as build, \
                        patch.object(builder, "check") as check, \
                        contextlib.redirect_stderr(io.StringIO()), \
                        self.assertRaises(SystemExit) as raised:
                    builder.main(arguments)
                self.assertEqual(raised.exception.code, 2)
                build.assert_not_called()
                check.assert_not_called()


if __name__ == "__main__":
    unittest.main()
