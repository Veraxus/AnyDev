import json
import os
import re
import subprocess
import typer

from anydev.configuration import Configuration
from anydev.core.cli_output import CliOutput
from dotenv import load_dotenv, dotenv_values
from functools import wraps
from rich.table import Table
from rich.console import Console

class ProjectHelpers:
    """Helper functions for AnyDev projects."""

    @staticmethod
    def is_running(path: str = '.') -> bool:
        """Are the project containers currently running?"""
        proc_command = ['docker', 'compose', 'ps', '--format', 'json']
        result = subprocess.run(proc_command, capture_output=True, text=True, cwd=path)
        try:
            # If running, we will get valid JSON, otherwise, empty string
            ps_output = json.loads(result.stdout)
            return len(ps_output) > 0
        except Exception:
            return False

    @staticmethod
    def is_project(path: str = '.') -> bool:
        """Check if the current directory is an AnyDev project."""

        # Check for .env files....
        env_file = None
        if os.path.isfile(path + '/.env.example'):
            env_file = path + '/.env.example'
        elif os.path.isfile(path + '/.env'):
            env_file = path + '/.env'

        # No env file means no flag. Not our project.
        if not env_file:
            CliOutput.warning("Current directory is not a valid AnyDev project.")
            return False

        try:
            # Load the environment file
            load_dotenv(env_file)
            env_vars = dotenv_values(env_file)
        except Exception as e:
            CliOutput.error(f"Could not parse environment file: {env_file}, {e}", True)

        # Check if the ANYDEV variable is present and "truthy"
        anydev_value = env_vars.get("ANYDEV")
        if anydev_value is None or str(anydev_value).lower() not in ["true", "1", "yes"]:
            CliOutput.warning(f"Could not verify project! ANYDEV variable is not present or enabled in env file(s).")
            return False

        return True

    @staticmethod
    def validate_project(f) -> callable:
        """Decorator to ensure certain commands check validity of project before running.."""

        @wraps(f)
        def wrapper(*args, **kwargs):
            # Execute is_project before the function
            if ProjectHelpers.is_project():
                return f(*args, **kwargs)
            else:
                CliOutput.error("Current directory is not a valid AnyDev project.", True)

        return wrapper

    @staticmethod
    def open_shell(shell_command: str) -> None:
        """Open shell for the current project container."""
        proc_command = ['docker', 'compose', 'exec', 'app', shell_command]
        result = subprocess.run(proc_command)
        if result.returncode != 0:
            CliOutput.error('Command failed: ' + ' '.join(proc_command), True)

    @staticmethod
    def restart_composition(path: str = '.') -> None:
        # Stop if already running
        ProjectHelpers.stop_project(path)
        # Start up
        CliOutput.info('Asking Docker to start project...')
        result = subprocess.run(['docker', 'compose', 'up', '-d'], cwd=path)
        if result.returncode != 0:
            CliOutput.error('Failed to start project!', True, result.returncode)
        else:
            CliOutput.success('Project containers successfully started!')

    @staticmethod
    def stop_project(path: str = '.') -> None:
        if ProjectHelpers.is_running(path):
            CliOutput.info('Asking Docker to stop project...')
            try:
                subprocess.run(['docker', 'compose', 'down'], check=True, cwd=path)
            except subprocess.CalledProcessError as e:
                CliOutput.error('Failed to stop project!', True, e.returncode)
        else:
            CliOutput.info('Project is not currently running.')

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
        if ProjectHelpers.is_running():
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

        for name, details in projects.items():
            path = details.get('path', 'Unknown')
            template = details.get('template', 'Unknown')
            table.add_row(name, template, path)

        console = Console()
        console.print(table)