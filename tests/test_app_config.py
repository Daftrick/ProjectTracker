import os
from unittest import TestCase
from unittest.mock import patch

from tracker import _requires_configured_secret_key


class AppConfigTests(TestCase):
    def test_default_secret_is_allowed_for_local_startup(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_requires_configured_secret_key("project-tracker-v2-2026"))

    def test_default_secret_is_rejected_in_production(self):
        with patch.dict(os.environ, {"PROJECT_TRACKER_ENV": "production"}, clear=True):
            self.assertTrue(_requires_configured_secret_key("project-tracker-v2-2026"))

    def test_custom_secret_is_allowed_in_production(self):
        with patch.dict(os.environ, {"PROJECT_TRACKER_ENV": "production"}, clear=True):
            self.assertFalse(_requires_configured_secret_key("configured-secret"))
