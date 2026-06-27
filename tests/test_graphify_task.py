import unittest
from contextlib import redirect_stderr
from io import StringIO

from tools.graphify_task import main


class GraphifyTaskTest(unittest.TestCase):

    def test_missing_graphify_skips_successfully(self):
        calls = []

        def fake_run(*args, **kwargs):
            calls.append((args, kwargs))

        result = main(["update"], which=lambda _cmd: None, run=fake_run)

        self.assertEqual(result, 0)
        self.assertEqual(calls, [])

    def test_existing_graphify_propagates_return_code(self):
        class Result:
            returncode = 7

        calls = []

        def fake_run(args, check=False):
            calls.append((args, check))
            return Result()

        result = main(["check-update"], which=lambda _cmd: "/usr/local/bin/graphify", run=fake_run)

        self.assertEqual(result, 7)
        self.assertEqual(calls, [(["/usr/local/bin/graphify", "check-update", "."], False)])

    def test_unknown_action_returns_usage_error(self):
        stderr = StringIO()
        with redirect_stderr(stderr):
            result = main(["bad-action"], which=lambda _cmd: "/usr/local/bin/graphify")

        self.assertEqual(result, 2)
        self.assertIn("Uso:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
