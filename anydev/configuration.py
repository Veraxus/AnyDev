import os
import platform
import shutil
import typer
import yaml

from core.cli_output import CliOutput


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

    PKG_MAN_MAP = [
        'apt',  # Debian, Ubuntu
        'dnf',  # Fedora
        'yum',  # CentOS, older Fedora
        'pacman',  # Arch Linux
        'apk',  # Alpine Linux
        'zypper',  # openSUSE
        # 'emerge',      # Gentoo
        # 'snap',        # Universal Linux package manager
        # 'flatpak',     # Universal Linux package manager
        # 'pkg',         # BSD systems
    ]

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Configuration, cls).__new__(cls, *args, **kwargs)
            cls.__instance._initialize()
        return cls.__instance

    def _initialize(self):
        """
        Sets class properties when instantiated.
        """

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

        self._os = None
        self._arch = None

        self.get_os()
        self.get_architecture()
        self._configs = self.load_configuration()

    def load_configuration(self) -> dict:
        """Loads the configuration from the config file.

        This method tries to open the configuration file specified in the
        `self.config_file` attribute and loads its content using the YAML parser.

        If the configuration file does not exist, it informs the user that AnyDev
        has not been configured yet. If there is a YAML parsing error, it informs
        the user about the error.

        Returns:
            dict: A dictionary containing the configuration settings, or an empty
            dictionary if the file does not exist or cannot be parsed.
        """
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            CliOutput.warning("AnyDev has not been configured yet.")
        except yaml.YAMLError as error:
            CliOutput.warning(f"Unable to parse config file at {self.config_file}: {error}!")
        return {}

    def get_configs(self) -> dict:
        """Returns raw config data."""
        return self._configs

    def get_active_profiles(self) -> list:
        """Gets all currently enabled profiles."""
        return self._configs.get('active_profiles', []) if self._configs \
            else []

    def set_active_profiles(self, active_profiles=None) -> None or list:
        """
        Sets the active profiles in the configuration.
        Args:
            active_profiles (list, optional): A list of active profiles. If None, an empty list will be set. Defaults to None.
        """
        if active_profiles is None:
            active_profiles = []
        self._configs['active_profiles'] = active_profiles
        # self.save_configuration()

    def get_project_directory(self) -> None or str:
        """Gets the configured project directory."""
        return self._configs.get('projects_path', self.default_projects_dir) if self._configs \
            else self.default_projects_dir

    def set_project_directory(self, project_directory: str = '') -> None:
        """
        Sets the project directory in the configuration.

        Args:
            project_directory (str): The path to the project directory. If an empty string is provided, the 'organize_projects'
            configuration will be set to False.
        """
        self._configs['projects_path'] = project_directory
        if project_directory.strip() == '':
            self._configs['organize_projects'] = False
        # self.save_configuration()

    def get_projects_organized(self) -> bool:
        """Checks if projects are organized as per the configuration.

        Returns:
            bool: True if the projects are set to be organized, False otherwise.
        """
        return self._configs.get('organize_projects', True) if self._configs \
            else True

    def add_project(self, name, path, template) -> None:
        """
        Adds a new project to the configuration.

        Args:
            name (str): The name of the project.
            path (str): The path to the project's directory.
            template (str): The template used for the project.

        """
        if 'projects' not in self._configs:
            self._configs['projects'] = {}
        self._configs['projects'][name] = {}
        self._configs['projects'][name]['path'] = path
        self._configs['projects'][name]['template'] = template
        self.save()

    def get_architecture(self) -> None or str:
        # Already set, return
        if self._arch:
            return self._arch

        arch_dict = {
            'x86_64':  'amd64',
            'amd64':   'amd64',
            'arm64':   'arm64',
            'aarch64': 'arm64',
        }

        arch = platform.machine()
        sanitized_arch = arch_dict.get(arch, None)

        if not sanitized_arch:
            CliOutput.warning("Unsupported architecture.")

        self._arch = sanitized_arch
        return self._arch

    def get_os(self) -> None or str:

        # Already looked up. Return it.
        if self._os:
            return self._os

        os_system = platform.system()
        if os_system == 'Darwin':
            self._os = self.make_os_dict(
                'macos',
                None,
                platform.mac_ver()[0],
                'brew',
                shutil.which('brew') is not None
            )
        elif os_system == 'Windows':
            CliOutput.warning("Windows is not fully supported yet.")
            self._os = self.make_os_dict(
                'windows',
                platform.version(),
                None,
                'choco',
                shutil.which('choco') is not None
            )
        elif os_system == 'Linux':
            CliOutput.warning("Linux is not fully supported yet.")
            self._os = self.make_os_dict('linux')
        else:
            CliOutput.error(f"Unsupported OS: {os_system}", True)

        return self._os

    def make_linux_dict(self) -> dict:
        """
        Constructs a dictionary containing detailed information about the Linux distribution.
        
        Returns:
            dict: A dictionary containing details about the OS such as name, version, 
                  package manager information, etc.
        
        Raises:
            FileNotFoundError: If the /etc/os-release file is not found.
            Exception: If any other error occurs while fetching the Linux distribution information.
        """

        # FIRST - Get Distro info
        try:
            # Try to get from /etc/os-release
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
            os_info = {}
            for line in lines:
                key_value = line.strip().split('=')
                if len(key_value) == 2:
                    key = key_value[0]
                    value = key_value[1].strip('"')
                    os_info[key] = value
            found_distro = os_info.get('ID', None)
            found_version = os_info.get('VERSION_ID', None)
        except FileNotFoundError:
            CliOutput.warning("Could not read distro information from /etc/os-release")
        except Exception:
            CliOutput.warning("Could not find information about your distro.")

        # FINALLY, check package managers...
        found_pkg_man = None
        for package_manager in self.PKG_MAN_MAP:
            if shutil.which(package_manager) is not None:
                found_pkg_man = package_manager
                break

        # Return what we found
        return self.make_os_dict(
            'linux',
            found_distro,
            found_version,
            found_pkg_man,
            shutil.which(found_pkg_man) is not None
        )

    def make_os_dict(self, os=None, distro=None, version=None, pkg_man=None, pkg_man_present=None):
        return {
            'os':      os,  # Name of the OS
            'distro':  distro,  # The distro (for Linux systems
            'version': version,  # The OS version
            'pkg_man': {  # Dict for package manager info
                'name':    pkg_man,  # The default package manager for this system (brew or macos, choco for windows)
                'present': pkg_man_present  # Whether the package manager is installed (only check for mac or win
            }
        }

    def save(self) -> None:
        """
        Saves the current configuration to the config file.
        """
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w') as file:
                yaml.safe_dump(self._configs, file)
            CliOutput.success("Configuration saved!")
        except Exception as error:
            CliOutput.error(f"Unable to save config file to {self.config_file}: {error}!", True)
