import json
import subprocess

from anydev.core.cli_output import CliOutput


class DockerHelpers:
    """Helper functions for AnyDev projects."""

    @staticmethod
    def restart_composition(path: str = '.', profiles: list = []) -> None:

        # Stop if already running
        DockerHelpers.stop_composition(path)

        # Friendly CLI output
        if len(profiles) > 0:
            CliOutput.info("Asking Docker to start chosen services...")
        else:
            CliOutput.info('Asking Docker to start composition...')

        # Turn profile list into command args
        profile_args = []
        for profile in profiles:
            profile_args.extend(["--profile", profile])

        # Create the up command using profile args
        up_cmd = ['docker-compose'] + profile_args + ['up', '-d']

        # Run the up command with any profiles
        result = subprocess.run(up_cmd, cwd=path)

        # Friendly CLI output
        if result.returncode != 0:
            CliOutput.error('Failed to start composition!', True, result.returncode)
        else:
            CliOutput.success('Composition containers successfully started!')

    @staticmethod
    def stop_composition(path: str = '.') -> None:
        """
        Stops the project's Docker composition if it is currently running.
        Stop command always stops ALL profiles.

        Args:
            path (str): The path to the Docker composition directory. Defaults to the current directory.

        """

        is_running = DockerHelpers.is_composition_running(path)

        if is_running:
            CliOutput.info('Asking Docker to stop composition...')
            try:
                subprocess.run(['docker', 'compose', '--profile', '*', 'down'], check=True, cwd=path)
            except subprocess.CalledProcessError as e:
                CliOutput.error('Failed to stop project!', True, e.returncode)
        else:
            CliOutput.info(f"Composition at is not currently running.")

    @staticmethod
    def is_composition_running(path: str = '.') -> bool:
        """
        Is there a composition running for the specified path?
        """
        proc_command = ['docker', 'compose', 'ps', '--format', 'json']
        result = subprocess.run(
            proc_command,
            capture_output=True, text=True, cwd=path
        )

        if result.stdout.strip():
            try:
                ps_results = []
                # Split the output into lines and parse each as a JSON object
                lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
                for line in lines:
                    # Add line to the output
                    json_line = json.loads(line)
                    ps_results.append(json_line)
                return len(ps_results) > 0
            except Exception as e:
                CliOutput.error(f"Failed to parse Docker ps output: {e}")
                return False

        return False

    @staticmethod
    def is_docker_running() -> bool:
        """
        Check if Docker daemon is running on the host machine.

        Returns:
            bool: True if Docker daemon is running, False otherwise.
        """
        try:
            # Check Docker version as a proxy for checking if Docker daemon is running
            result = subprocess.run(
                ['docker', 'version'],
                capture_output=True, text=True
            )
            # docker version exits with 1 if docker daemon isnt running
            return result.returncode == 0
        except Exception:
            return False
