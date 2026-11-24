import os
import subprocess
import sys
import textwrap
import unittest


class TestTestRunner(unittest.TestCase):
    def run_outcome(self, outcome):
        script = textwrap.dedent(
            """
            import runpy
            import sys
            import unittest

            outcome = sys.argv.pop()

            class Outcome(unittest.TestCase):
                def runTest(self):
                    if outcome == "failure":
                        self.fail("intentional runner failure")
                    if outcome == "error":
                        raise RuntimeError("intentional runner error")

            def load_outcome(self, test_case):
                return unittest.TestSuite([Outcome()])

            unittest.TestLoader.loadTestsFromTestCase = load_outcome
            runpy.run_module("i18n.tests.run_tests", run_name="__main__")
            """
        )
        return subprocess.run(
            [sys.executable, "-B", "-c", script, outcome],
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )

    def test_failed_assertions_produce_a_failing_exit_status(self):
        result = self.run_outcome("failure")
        self.assertIn("intentional runner failure", result.stderr)
        self.assertIn("FAILED (failures=", result.stderr)
        self.assertNotEqual(result.returncode, 0, result.stderr)

    def test_test_errors_produce_a_failing_exit_status(self):
        result = self.run_outcome("error")
        self.assertIn("intentional runner error", result.stderr)
        self.assertIn("FAILED (errors=", result.stderr)
        self.assertNotEqual(result.returncode, 0, result.stderr)

    def test_successful_tests_produce_a_successful_exit_status(self):
        result = self.run_outcome("success")
        self.assertIn("OK", result.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)
