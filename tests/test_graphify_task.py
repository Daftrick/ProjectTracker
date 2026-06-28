import unittest

from tools.graphify_task import main


class Completed:
    returncode = 0


class GraphifyTaskTest(unittest.TestCase):

    def test_update_returns_success(self):
        calls = []

        result = main(
            ["update"],
            runner=lambda args, cwd: calls.append((args, cwd)) or Completed(),
            which=lambda name: "/tmp/graphify",
        )

        self.assertEqual(result, 0)
        self.assertEqual(calls[0][0], ["/tmp/graphify", "update", "."])

    def test_check_update_returns_success(self):
        calls = []

        result = main(
            ["check-update"],
            runner=lambda args, cwd: calls.append((args, cwd)) or Completed(),
            which=lambda name: "/tmp/graphify",
        )

        self.assertEqual(result, 0)
        self.assertEqual(calls[0][0], ["/tmp/graphify", "info"])

    def test_missing_graphify_returns_success(self):
        result = main(["update"], runner=None, which=lambda name: None)

        self.assertEqual(result, 0)

    def test_unknown_action_returns_success(self):
        result = main(["bad-action"])

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
