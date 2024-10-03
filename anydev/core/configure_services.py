import os
import questionary
import yaml

from anydev.configuration import Configuration
from anydev.core.cli_output import CliOutput
from anydev.core.docker_controls import DockerHelpers
from anydev.core.questionary_styles import anydev_qsty_styles


class ConfigureServices:
    """
    Helper functions for AnyDev projects.
    """

    def __init__(self):
        self.config = Configuration()

    def configure(self) -> None:
        """
        Runs the `anydev configure` command.
        Prompts users for their desired stacks/configurations.
        """

        CliOutput.info("Starting interactive configuration...")

        if self.config.get_configs():
            CliOutput.info("Using your existing configuration for defaults.")

        # Ask user which profiles they want to use
        self.prompt_profiles()

        # Ask for a default project directory
        self.prompt_projects_dir()

        # Save configs
        self.config.save()

        # Ask user if they want to restart services
        self.prompt_restart()

        CliOutput.success("Configuration complete!", True)

    def prompt_profiles(self) -> None:
        """
            Ask the user to select their desired profiles from available ones:
            - Profiles are obtained from docker-compose.yml under 'profiles' section.
            - Prompts user with a checkbox list to select/deselect profiles.
            - Updates the active profiles in the configuration based on user selection.
        """
        profiles = self.get_service_profiles()
        active_profiles = self.config.get_active_profiles()
        # Ask the user to select their desired profiles
        selected_profiles = questionary.checkbox(
            "Which profiles would you like to use?",
            choices=[
                questionary.Choice(
                    title=profile,
                    checked=(profile in active_profiles)
                ) for profile in profiles
            ],
            style=anydev_qsty_styles
        ).unsafe_ask()  # <-- keyboard interrupt exits
        # If no profiles are selected, return or handle accordingly
        if selected_profiles is None or len(selected_profiles) == 0:
            CliOutput.info("No profiles selected. Using minimal configuration.")
        else:
            CliOutput.info('Using your selected profiles: ' + ', '.join(selected_profiles))
            self.config.set_active_profiles(selected_profiles)

    def get_service_profiles(self) -> list:
        """
        Gets all service profiles from docker-compose.yml.

        Returns:
            list: A sorted list of unique profiles found in the docker-compose.yml file.
        """
        compose_file = os.path.join(self.config.cli_root_dir, 'docker-compose.yml')

        # Read the docker-compose.yml file
        with open(compose_file, 'r') as f:
            compose_data = yaml.safe_load(f)

        # Initialize a set to avoid duplication
        profiles = set()

        # Iterate over the services in the compose file
        services = compose_data.get('services', {})
        for service_name, service_data in services.items():
            # Get the profiles for the service, if they exist
            service_profiles = service_data.get('profiles', [])
            # Add them to the profiles set to ensure uniqueness
            profiles.update(service_profiles)

        # Return the profiles as a sorted list
        return sorted(profiles)

    def prompt_projects_dir(self) -> None:
        """
        Ask user where their default project directory is.
        """

        project_dir = questionary.text(
            "Where do you want to put your projects?",
            default=self.config.get_project_directory(),
            style=anydev_qsty_styles
        ).unsafe_ask()  # <-- keyboard interrupt exits

        if project_dir and os.path.isdir(project_dir.strip()):
            CliOutput.success(f"Projects will be created in: {project_dir}")
            self.config.set_project_directory(project_dir)
            return
        elif not project_dir or project_dir.strip() == "":
            CliOutput.warning("You need to specify a directory to keep your projects.")
            return self.prompt_projects_dir()
        else:
            create_dir = questionary.confirm(
                f"That directory doesn't exist. Should I try to create it? ( {project_dir} )",
                default=True,
                style=anydev_qsty_styles
            ).unsafe_ask()

            if create_dir:
                try:
                    os.makedirs(project_dir)
                    self.config.set_project_directory(project_dir)
                    CliOutput.success(f"Projects will be created in: {project_dir}")
                    return
                except Exception as e:
                    CliOutput.warning(f"Unable to create directory {project_dir}: {e}")
                    return self.prompt_projects_dir()
            CliOutput.warning("Please set a directory to continue configuration.")
            return self.prompt_projects_dir()

    def prompt_restart(self) -> None:
        # Ask the user if they want to (re)start the service containers
        restart_services = questionary.confirm(
            "Do you want to (re)start the service containers now?",
            default=True,
            style=anydev_qsty_styles
        ).unsafe_ask()

        # User accepted restart...
        if restart_services:
            DockerHelpers.restart_composition(
                self.config.cli_root_dir,
                self.config.get_active_profiles()
            )

