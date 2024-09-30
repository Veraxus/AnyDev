import os
import typer
import yaml


class Configuration:
    """Configuration settings for the application.

    This class implements a singleton pattern to ensure that there is only
    one instance of the configuration settings. The configuration settings
    are stored in the user's home directory, under the `.anydev` directory.

    Attributes:
        __instance (Configuration): The singleton instance of the Configuration class.
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

        # Path to user's home directory
        self.user_dir = os.path.expanduser('~')
        # Default project path if none is specified
        self.default_projects_dir = os.path.join(self.user_dir, 'AnyDev Projects')
        # Path to users anydev configurations
        self.config_dir = os.path.join(self.user_dir, '.anydev')
        # Path certificates directory in anydev configurations
        self.certs_dir = os.path.join(self.config_dir, 'certs')
        # Persistent configuration data
        self.config_file = os.path.join(self.config_dir, 'config.yaml')

        # Path to anydev's .env.example file
        self.cli_env_example = os.path.join(self.cli_root_dir, '.env.example')
        # Path to anydev's active .env file
        self.cli_env_active = os.path.join(self.cli_root_dir, '.env')

        self._configs = self.load_configuration()

    def load_configuration(self) -> dict:
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            typer.secho(
                f"AnyDev has not been configured.",
                fg=typer.colors.YELLOW, bold=True
            )
        except yaml.YAMLError as error:
            typer.secho(
                f"ERROR: Unable to parse config file at {self.config_file}: {error}!",
                err=True, fg=typer.colors.RED, bold=True
            )
        return {}

    def get_configs(self) -> dict:
        return self._configs

    def get_active_profiles(self) -> list:
        """Gets all currently enabled profiles."""
        return self._configs.get('active_profiles', []) if self._configs \
            else []

    def set_active_profiles(self, active_profiles=None) -> None or list:
        if active_profiles is None:
            active_profiles = []
        self._configs['active_profiles'] = active_profiles
        # self.save_configuration()

    def get_project_directory(self) -> None or str:
        """Gets the configured project directory."""
        return self._configs.get('projects_path', self.default_projects_dir) if self._configs \
            else self.default_projects_dir

    def set_project_directory(self, project_directory: str = '') -> None:
        self._configs['projects_path'] = project_directory
        if project_directory.strip() == '':
            self._configs['organize_projects'] = False
        # self.save_configuration()

    def get_projects_organized(self) -> bool:
        return self._configs.get('organize_projects', True) if self._configs \
            else True

    def add_project(self, name, path, template) -> None:
        if 'projects' not in self._configs:
            self._configs['projects'] = {}
        self._configs['projects'][name] = {}
        self._configs['projects'][name]['path'] = path
        self._configs['projects'][name]['template'] = template
        self.save()

    def save(self) -> None:
        """Saves the current configuration to the config file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w') as file:
                yaml.safe_dump(self._configs, file)
            typer.secho(
                f"Successfully saved configuration!",
                fg=typer.colors.GREEN, bold=True
            )
        except Exception as error:
            typer.secho(
                f"ERROR: Unable to save config file at {self.config_file}: {error}!",
                err=True, fg=typer.colors.RED, bold=True
            )
