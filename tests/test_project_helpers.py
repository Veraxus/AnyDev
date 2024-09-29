import unittest
import json
from unittest.mock import patch, MagicMock
from anydev.core.project_helpers import ProjectHelpers


class TestProjectHelpers(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.project_helpers = ProjectHelpers

    def tearDown(self):
        super().tearDown()

    def test_sanitize_folder_name(self):
        # Test all allowed character types
        name = "Valid_Folder-Name 123.4"
        self.assertEqual(
            self.project_helpers.sanitize_folder_name(name), name,
            "Folder name with valid characters should remain unchanged."
        )

        # Test unallowed character types
        # Hammer and sickle U+262D is not an allowed character and should be replaced with underscore
        name = "Inval*id:Fol*der|Name 123.4"
        expected = "Inval_id_Fol_der_Name 123.4"
        self.assertEqual(
            self.project_helpers.sanitize_folder_name(name), expected,
            "Folder name with invalid characters should be sanitized."
        )

        # Test leading/trailing spaces
        name = "  Valid Folder Name 123.4  "
        expected = "Valid Folder Name 123.4"
        self.assertEqual(
            self.project_helpers.sanitize_folder_name(name), expected,
            "Folder name with leading/trailing spaces should be stripped."
        )

        # Test length limit
        name = "a" * 256
        expected = "a" * 255
        self.assertEqual(
            self.project_helpers.sanitize_folder_name(name), expected,
            "Folder name should be cut to max length."
        )

    @patch("subprocess.run")
    @patch("json.loads")
    def test_is_running_true(self, mock_json_loads, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = '[{"name": "app"}]'
        mock_json_loads.return_value = [{"name": "app"}]
        self.assertTrue(
            self.project_helpers.is_running("my_project_path")
        )
        mock_subprocess_run.assert_called_once_with(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True,
            text=True,
            cwd="my_project_path"
        )

    @patch("subprocess.run")
    @patch("json.loads")
    def test_is_running_false(self, mock_json_loads, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = '[]'
        mock_json_loads.return_value = []
        self.assertFalse(
            self.project_helpers.is_running("my_project_path")
        )
        mock_subprocess_run.assert_called_once_with(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True,
            text=True,
            cwd="my_project_path"
        )

    @patch("subprocess.run")
    @patch("json.loads")
    def test_is_running_exception(self, mock_json_loads, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = 'this is invalid json'
        mock_json_loads.side_effect = Exception("Invalid JSON")
        self.assertFalse(
            self.project_helpers.is_running("my_project_path")
        )
        mock_subprocess_run.assert_called_once_with(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True,
            text=True,
            cwd="my_project_path"
        )


if __name__ == '__main__':
    unittest.main()
