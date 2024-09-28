import os
import subprocess
import typer

from functools import wraps
from dotenv import load_dotenv, dotenv_values

from commands.project import stop


class ProjectHelpers:
    """Helper functions for AnyDev projects."""

    @staticmethod
    def is_running():
        """Are the project containers currently running?"""
        proc_command = ['docker', 'compose', 'ps', '--format', 'json']
        result = subprocess.run(proc_command, capture_output=True, text=True)
        return len(result.stdout.strip()) > 0

    @staticmethod
    def is_project():
        """Check if the current directory is an AnyDev project."""

        # Check for .env files....
        env_file = None
        if os.path.isfile('.env.example'):
            env_file = '.env.example'
        elif os.path.isfile('.env'):
            env_file = '.env'

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
    def validate_project(f):
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
    def open_shell(shell_command: str):
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
    def restart_composition():
        # Stop if already running
        stop()
        # Start up
        typer.secho('Starting project...', fg=typer.colors.YELLOW, bold=True)
        result = subprocess.run(['docker', 'compose', 'up', '-d'])
        if result.returncode != 0:
            typer.secho('Failed to start project!', err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=result.returncode)
        else:
            typer.secho('Projected started!', err=False, fg=typer.colors.GREEN, bold=True)

    @staticmethod
    def stop_project():
        if ProjectHelpers.is_running():
            typer.secho('Stopping project...', fg=typer.colors.YELLOW, bold=True)
            try:
                subprocess.run(['docker', 'compose', 'down'], check=True)
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
