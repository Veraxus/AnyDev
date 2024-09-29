import os
from pathlib import Path


class Configuration:
    """Configuration settings for the application.

    This class implements a singleton pattern to ensure that there is only
    one instance of the configuration settings. The configuration settings
    are stored in the user's home directory, under the `.anydev` directory.

    Attributes:
        _instance (Configuration): The singleton instance of the Configuration class.
        config_dir (str): The path to the configuration directory.
        certs_dir (str): The path to the directory containing SSL certificates.
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Configuration, cls).__new__(cls, *args, **kwargs)
            cls.__instance._initialize()
        return cls.__instance

    def _initialize(self):
        # == Important AnyDev Core Locations ==

        # Path to the directory of the anydev package
        self.cli_package_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to anydev's top-level directory
        self.cli_root_dir = os.path.dirname(self.cli_package_dir)
        # Path to the templates directory
        self.templates_dir = os.path.join(self.cli_root_dir, 'templates')

        # == Important AnyDev Config Locations ==

        # Path to users anydev configurations
        self.config_dir = os.path.expanduser('~/.anydev')
        # Path certificates directory in anydev configurations
        self.certs_dir = os.path.join(self.config_dir, 'certs')

        # Path to anydev's .env.example file
        self.cli_env_example = os.path.join(self.cli_root_dir, '.env.example')
        # Path to anydev's active .env file
        self.cli_env_active = os.path.join(self.cli_root_dir, '.env')
