import unittest
import json
from unittest.mock import patch, MagicMock
from anydev.core import project_helpers


class TestProjectHelpers(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.project_helpers = project_helpers.ProjectHelpers

    def tearDown(self):
        super().tearDown()

    def test_sanitize_folder_name(self):
        # Test all allowed character types
        name = "Valid_Folder-Name 123.4"
        self.assertEqual(self.project_helpers.sanitize_folder_name(name), name,
                         "Folder name with valid characters should remain unchanged.")

        # Test unallowed character types
        # Hammer and sickle U+262D is not an allowed character and should be replaced with underscore
        name = "Inval*id:Fol*der|Name 123.4"
        expected = "Inval_id_Fol_der_Name 123.4"
        self.assertEqual(self.project_helpers.sanitize_folder_name(name), expected,
                         "Folder name with invalid characters should be sanitized.")

        # Test leading/trailing spaces
        name = "  Valid Folder Name 123.4  "
        expected = "Valid Folder Name 123.4"
        self.assertEqual(self.project_helpers.sanitize_folder_name(name), expected,
                         "Folder name with leading/trailing spaces should be stripped.")

        # Test length limit
        name = "a" * 256
        expected = "a" * 255
        self.assertEqual(self.project_helpers.sanitize_folder_name(name), expected,
                         "Folder name should be cut to max length.")

    @patch('subprocess.run')
    def test_is_running(self, mock_subprocess):
        # Test with project running
        mock_run_return = MagicMock()
        mock_run_return.stdout = json.dumps(["running"])
        mock_subprocess.return_value = mock_run_return
        self.assertTrue(self.project_helpers.is_running())
        mock_subprocess.assert_called_once_with([
            'docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True, text=True
        )
        mock_subprocess.reset_mock()

        # Test with project not running
        mock_run_return.stdout = json.dumps([])
        self.assertFalse(self.project_helpers.is_running())
        mock_subprocess.assert_called_once_with(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True, text=True
        )
        mock_subprocess.reset_mock()

        # Test with subprocess exception
        mock_run_return.stdout = "not json"
        self.assertFalse(self.project_helpers.is_running())
        mock_subprocess.assert_called_once_with(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True, text=True
        )


if __name__ == '__main__':
    unittest.main()
