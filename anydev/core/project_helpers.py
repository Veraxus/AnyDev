import json
import os
import re
import subprocess
import typer

from functools import wraps
from dotenv import load_dotenv, dotenv_values
from typer.testing import CliRunner


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
        except json.JSONDecodeError as e:
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
            typer.secho(
                "ERROR: This is not an AnyDev project (no env file found)",
                err=True, fg=typer.colors.RED, bold=True
            )
            return False

        try:
            # Load the environment file
            load_dotenv(env_file)
            env_vars = dotenv_values(env_file)
        except Exception as e:
            typer.secho(
                f"ERROR: Failed to parse the environment file: {e}",
                err=True, fg=typer.colors.RED, bold=True
            )
            raise typer.Exit(code=1)

        # Check if the ANYDEV variable is present and "truthy"
        anydev_value = env_vars.get("ANYDEV")
        if anydev_value is None or str(anydev_value).lower() not in ["true", "1", "yes"]:
            typer.secho(
                f"ERROR: ANYDEV variable not present or enabled in {env_file}",
                err=True, fg=typer.colors.RED, bold=True
            )
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
                typer.secho(
                    'Current directory is not a valid AnyDev project.',
                    err=True, fg=typer.colors.RED, bold=True
                )
                raise typer.Exit(code=1)

        return wrapper

    @staticmethod
    def open_shell(shell_command: str) -> None:
        """Open shell for the current project container."""
        proc_command = ['docker', 'compose', 'exec', 'app', shell_command]
        result = subprocess.run(proc_command)
        if result.returncode != 0:
            typer.secho(
                'ERROR: Command failed: ' + ' '.join(proc_command),
                err=True, fg=typer.colors.RED, bold=True
            )
            raise typer.Exit(code=result.returncode)

    @staticmethod
    def restart_composition(path: str = '.') -> None:
        # Stop if already running
        ProjectHelpers.stop_project(path)
        # Start up
        typer.secho('Starting project...', fg=typer.colors.YELLOW, bold=True)
        result = subprocess.run(['docker', 'compose', 'up', '-d'], cwd=path)
        if result.returncode != 0:
            typer.secho('Failed to start project!', err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=result.returncode)
        else:
            typer.secho('Projected started!', err=False, fg=typer.colors.GREEN, bold=True)

    @staticmethod
    def stop_project(path: str = '.') -> None:
        # TODO: Ensure other projects don't get stopped
        if ProjectHelpers.is_running(path):
            typer.secho('Stopping project...', fg=typer.colors.YELLOW, bold=True)
            try:
                subprocess.run(['docker', 'compose', 'down'], check=True, cwd=path)
            except subprocess.CalledProcessError as e:
                typer.secho(
                    f"ERROR: Failed to stop the project: {e}",
                    err=True, fg=typer.colors.RED, bold=True
                )
                raise typer.Exit(code=e.returncode)
        else:
            typer.secho(
                'Project is not running.',
                err=True, fg=typer.colors.YELLOW, bold=True
            )

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
                typer.secho(
                    'ERROR: Command failed: ' + ' '.join(proc_command),
                    err=True, fg=typer.colors.RED, bold=True
                )
                raise typer.Exit(code=result.returncode)
            typer.secho('Tailing logs. Press Ctrl+C to exit.', fg=typer.colors.YELLOW, bold=True)
        else:
            typer.secho('The project is not currently running.', err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)
