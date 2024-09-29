import unittest

from anydev.core import project_helpers


class TestProjectHelpers(unittest.TestCase):
    def setUp(self):
        self.helper = project_helpers.ProjectHelpers

    def test_sanitize_folder_name(self):
        # Test all allowed character types
        name = "Valid_Folder-Name 123.4"
        self.assertEqual(self.helper.sanitize_folder_name(name), name,
                         "Folder name with valid characters should remain unchanged.")

        # Test unallowed character types
        # Hammer and sickle U+262D is not an allowed character and should be replaced with underscore
        name = "Inval*id:Fol*der|Name 123.4"
        expected = "Inval_id_Fol_der_Name 123.4"
        self.assertEqual(self.helper.sanitize_folder_name(name), expected,
                         "Folder name with invalid characters should be sanitized.")

        # Test leading/trailing spaces
        name = "  Valid Folder Name 123.4  "
        expected = "Valid Folder Name 123.4"
        self.assertEqual(self.helper.sanitize_folder_name(name), expected,
                         "Folder name with leading/trailing spaces should be stripped.")

        # Test length limit
        name = "a" * 256
        expected = "a" * 255
        self.assertEqual(self.helper.sanitize_folder_name(name), expected,
                         "Folder name should be cut to max length.")


if __name__ == '__main__':
    unittest.main()
