import unittest

from tracker.domain import project_semaphore

TODAY = "2026-06-19"


class SemaphoreTest(unittest.TestCase):

    def test_no_fields_returns_gris(self):
        self.assertEqual(project_semaphore({}, TODAY), "gris")

    def test_deadline_in_2_days_returns_rojo(self):
        p = {"deadline": "2026-06-21", "updated_at": TODAY}
        self.assertEqual(project_semaphore(p, TODAY), "rojo")

    def test_deadline_exactly_3_days_returns_rojo(self):
        p = {"deadline": "2026-06-22", "updated_at": TODAY}
        self.assertEqual(project_semaphore(p, TODAY), "rojo")

    def test_deadline_in_5_days_returns_amarillo(self):
        p = {"deadline": "2026-06-24", "updated_at": TODAY}
        self.assertEqual(project_semaphore(p, TODAY), "amarillo")

    def test_inactive_7_days_returns_rojo(self):
        p = {"updated_at": "2026-06-12"}
        self.assertEqual(project_semaphore(p, TODAY), "rojo")

    def test_inactive_3_days_returns_amarillo(self):
        p = {"updated_at": "2026-06-16"}
        self.assertEqual(project_semaphore(p, TODAY), "amarillo")

    def test_active_with_future_deadline_returns_verde(self):
        p = {"deadline": "2026-06-29", "updated_at": TODAY}
        self.assertEqual(project_semaphore(p, TODAY), "verde")

    def test_inactive_overrides_far_deadline(self):
        # 7 days inactive trumps a deadline in 30 days
        p = {"deadline": "2026-07-19", "updated_at": "2026-06-12"}
        self.assertEqual(project_semaphore(p, TODAY), "rojo")

    def test_invalid_today_str_returns_gris(self):
        p = {"deadline": "2026-06-22", "updated_at": TODAY}
        self.assertEqual(project_semaphore(p, "not-a-date"), "gris")

    def test_invalid_deadline_falls_back_to_inactivity(self):
        p = {"deadline": "invalid", "updated_at": "2026-06-12"}
        self.assertEqual(project_semaphore(p, TODAY), "rojo")

    def test_only_updated_at_no_deadline_active_returns_gris(self):
        # updated today, no deadline → gris (no enough info for verde)
        p = {"updated_at": TODAY}
        self.assertEqual(project_semaphore(p, TODAY), "gris")


if __name__ == "__main__":
    unittest.main()
