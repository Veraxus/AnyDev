import os
import unittest

from anydev import configuration


class TestConfiguration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = configuration.Configuration()

    def test_singleton_pattern(self):
        another_config = configuration.Configuration()
        self.assertEqual(self.config, another_config)

    def test_initialize(self):
        # Test cli_package_dir
        expected_cli_package_dir = os.path.dirname(os.path.abspath(configuration.__file__))
        self.assertEqual(self.config.cli_package_dir, expected_cli_package_dir)

        # Test cli_root_dir
        expected_cli_root_dir = os.path.dirname(expected_cli_package_dir)
        self.assertTrue(self.config.cli_root_dir, expected_cli_root_dir)

        # Test templates_dir
        expected_templates_dir = os.path.join(expected_cli_root_dir, 'templates')
        self.assertEqual(self.config.templates_dir, expected_templates_dir)

        # Test config_dir
        expected_config_dir = os.path.expanduser('~/.anydev')
        self.assertEqual(self.config.config_dir, expected_config_dir)

        # Test certs_dir
        expected_certs_dir = os.path.join(expected_config_dir, 'certs')
        self.assertEqual(self.config.certs_dir, expected_certs_dir)

        # Test cli_env_example
        expected_cli_env_example = os.path.join(expected_cli_root_dir, '.env.example')
        self.assertEqual(self.config.cli_env_example, expected_cli_env_example)

        # Test cli_env_active
        expected_cli_env_active = os.path.join(expected_cli_root_dir, '.env')
        self.assertEqual(self.config.cli_env_active, expected_cli_env_active)


if __name__ == '__main__':
    unittest.main()
