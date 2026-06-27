import unittest

from tools.graphify_task import main


class GraphifyTaskTest(unittest.TestCase):

    def test_update_returns_success(self):
        result = main(["update"])

        self.assertEqual(result, 0)

    def test_check_update_returns_success(self):
        result = main(["check-update"])

        self.assertEqual(result, 0)

    def test_unknown_action_returns_success(self):
        result = main(["bad-action"])

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
