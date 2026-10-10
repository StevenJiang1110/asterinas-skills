#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_regression_tests.py")
SPEC = importlib.util.spec_from_file_location("checker", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class CheckerTests(unittest.TestCase):
    def scan_c(self, source: str):
        return CHECKER.scan_c(Path("sample.c"), source)

    def test_accepts_calls_in_expected_contexts(self):
        findings = self.scan_c(
            """
FN_SETUP(open_file) { CHECK(open(path, O_RDONLY)); } END_SETUP()
FN_TEST(read_file) { TEST_RES(read(fd, buf, sizeof(buf)), _ret == 1); } END_TEST()
"""
        )
        self.assertEqual(findings, [])

    def test_flags_bare_value_and_wrong_contexts(self):
        findings = self.scan_c(
            """
FN_SETUP(open_file) { TEST_SUCC(open(path, O_RDONLY)); } END_SETUP()
FN_TEST(read_file) { CHECK(read(fd, buf, 1)); TEST_RES(nread, _ret == 1); } END_TEST()
TEST_SUCC(close(fd));
"""
        )
        pairs = {(finding.rule, finding.severity) for finding in findings}
        self.assertIn(("RT-01", "violation"), pairs)
        self.assertIn(("RT-03", "violation"), pairs)
        self.assertIn(("RT-03", "candidate"), pairs)

    def test_flags_unexplained_whole_test_guard(self):
        findings = self.scan_c(
            """
#ifdef __asterinas__
FN_TEST(platform_only) { TEST_SUCC(do_work()); } END_TEST()
#endif
"""
        )
        messages = [finding.message for finding in findings if finding.rule == "RT-06"]
        self.assertEqual(len(messages), 2)

    def test_shell_groups_are_checked_separately(self):
        source = "./beta\n./alpha\n\n./delta\n./echo\n"
        findings = CHECKER.scan_shell_list(Path("run_test.sh"), source)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 1)

    def test_makefile_test_list_order(self):
        source = "\n".join(("SUBDIRS := \\", "    beta \\", "    alpha \\", ""))
        findings = CHECKER.scan_makefile_list(Path("Makefile"), source)
        self.assertEqual(len(findings), 1)


if __name__ == "__main__":
    unittest.main()
