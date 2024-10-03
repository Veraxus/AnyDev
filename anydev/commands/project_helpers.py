import os
import re
import subprocess

from anydev.configuration import Configuration
from anydev.core.cli_output import CliOutput
from anydev.core.docker_controls import DockerHelpers
from dotenv import load_dotenv, dotenv_values
from functools import wraps
from rich.console import Console
from rich.table import Table

class ProjectHelpers:
    """Helper functions for AnyDev projects."""

    @staticmethod
    def is_project(path: str = '.') -> bool:
        """Check if the current directory is an AnyDev project."""

        # Check for .env files (prefer example)....
        env_file = None
        if os.path.isfile(path + '/.env.example'):
            env_file = path + '/.env.example'
        elif os.path.isfile(path + '/.env'):
            env_file = path + '/.env'

        # No env file means no flag. Not our project.
        if not env_file:
            if path == os.getcwd():
                CliOutput.warning("Current directory is not an AnyDev project!")
            else:
                CliOutput.warning(f"Directory {path} is not an AnyDev project!")
            return False

        try:
            # Load the environment file
            load_dotenv(env_file)
            env_vars = dotenv_values(env_file)
        except Exception as e:
            CliOutput.error(f"Could not parse environment file: {env_file}, {e}", True)

        invalid_env_vars = 0

        # Check if the ANYDEV variable is present and "truthy"
        anydev_value = env_vars.get("ANYDEV")
        if anydev_value is None or str(anydev_value).lower() not in ["true", "1", "yes"]:
            CliOutput.warning(f"ANYDEV variable is not present or enabled in env file(s).")
            invalid_env_vars += 1

        anydev_template = env_vars.get("ANYDEV_TEMPLATE")
        if anydev_template is None:
            CliOutput.warning(f"ANYDEV_TEMPLATE variable is not present in env file(s).")
            invalid_env_vars += 1

        if invalid_env_vars > 0:
            CliOutput.error("Current directory is not a valid AnyDev project.", False)
            return False

        return True

    @staticmethod
    def validate_project(f) -> callable:
        """Decorator to ensure certain commands check validity of project before running.."""

        @wraps(f)
        def wrapper(*args, **kwargs):
            # Execute is_project before the function
            if ProjectHelpers.is_project():
                config = Configuration()
                project_details = ProjectHelpers.get_project_details()
                known_projects = config.get_registered_projects()
                if project_details["name"] not in known_projects:
                    # Project isn't registered yet. So remember it.
                    config.add_project(
                        project_details["name"],
                        project_details["path"],
                        project_details["template"]
                    )
                    config.save()
                    CliOutput.success(f"Project '{project_details['name']}' registered successfully.")

                return f(*args, **kwargs)
            else:
                CliOutput.error("Directory is not a valid AnyDev project.", True)

        return wrapper

    @staticmethod
    def get_project_details() -> dict:
        """
        Gets information about the current project.
        Always validate before calling!
        """

        env_file = dotenv_values(os.path.join(os.getcwd(), '.env.example'))

        project_details = {
            "name":     os.path.basename(os.getcwd()),
            "path":     os.path.abspath(os.getcwd()),
            "template": env_file.get("ANYDEV_TEMPLATE", "Invalid")
        }

        return project_details

    @staticmethod
    def open_shell(shell_command: str) -> None:
        """Open shell for the current project container."""
        proc_command = ['docker', 'compose', 'exec', 'app', shell_command]
        result = subprocess.run(proc_command)
        if result.returncode != 0:
            CliOutput.error('Command failed: ' + ' '.join(proc_command), True)

    @staticmethod
    def sanitize_folder_name(folder_name: str) -> str:
        """
        Sanitizes a folder name by replacing any risky (non-allow-listed) characters.
        Allowed characters: alphanumeric, underscores, dashes, spaces, and dots.

        Args:
            folder_name (str): The folder name to sanitize.

        Returns:
            str: The sanitized folder name.
        """

        # Define a regex pattern to match any character that is NOT alphanumeric, underscore, dash, space, or dot
        allowed_chars = r'[^\w\-\s\.]'

        # Replace any invalid characters with underscores
        sanitized_name = re.sub(allowed_chars, '_', folder_name)

        # Remove leading/trailing spaces
        sanitized_name = sanitized_name.strip()

        # Optionally limit the length to 255 characters (common max length)
        max_length = 255
        sanitized_name = sanitized_name[:max_length]

        return sanitized_name

    @staticmethod
    def tail_container_logs(service_name: str = "app", path: str = '.') -> None:
        """
        Tails the logs of a specified service within the current running Docker Compose project.

        This method runs the `docker compose logs` command with the `-f` flag to follow the logs
        of the given service in real-time. The logs are tailed in the specified directory.

        Args:
            service_name (str): The name of the Docker Compose service to tail logs for. Defaults to "app".
            path (str): The directory in which to run the command. Defaults to the current directory/context.

        Raises:
            typer.Exit: If the project is not running or the log tailing command fails.
        """
        if DockerHelpers.is_composition_running():
            proc_command = ['docker', 'compose', 'logs', service_name, '-f']
            result = subprocess.run(proc_command, cwd=path)
            if result.returncode != 0:
                CliOutput.error('Command failed: ' + ' '.join(proc_command), True, result.returncode)
            CliOutput.info('Logs tailed. Press Ctrl+C to exit.')
        else:
            CliOutput.error('The project is not currently running.', True)

    @staticmethod
    def list_projects() -> None:
        table = Table(title="AnyDev Projects")

        table.add_column("Project", justify="left", style="cyan", no_wrap=True)
        table.add_column("Template", justify="left", style="magenta")
        table.add_column("Path", justify="left", style="green")

        projects = Configuration().get_registered_projects()

        # Remove any project whose path doesn't validate
        projects_to_remove = []

        # Process and validate registered projects
        for name, details in projects.items():
            path = details.get('path', 'Unknown')
            template = details.get('template', 'Unknown')
            if ProjectHelpers.is_project(path):
                table.add_row(name, template, path)
            else:
                projects_to_remove.append(name)
                CliOutput.alert(f"Project {name} is no longer valid. Removing it from tracked projects.")

        # TODO: Make project validation optional?
        # Remove invalid projects from the configuration
        config = Configuration()
        for project_name in projects_to_remove:
            config.unregister_project(project_name)
        config.save()

        # Output the table
        console = Console()
        console.print(table)