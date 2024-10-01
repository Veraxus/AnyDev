import os
import questionary
import subprocess
import typer
import yaml
from anydev.configuration import Configuration
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

        typer.secho(
            "Starting interactive configuration...",
            fg=typer.colors.YELLOW, bold=True
        )

        if self.config.get_configs():
            typer.secho(
                "Existing configuration found. Using it for default values.",
                fg=typer.colors.YELLOW, bold=True
            )

        # Ask user which profiles they want to use
        self.prompt_profiles()

        # Ask for a default project directory
        self.prompt_projects_dir()

        # Save configs
        self.config.save()

        # Ask user if they want to restart services
        self.prompt_restart()

        typer.secho(
            "Configuration complete!",
            fg=typer.colors.GREEN, bold=True
        )
        typer.secho(
            "Create projects with `anydev project create`.",
            fg=typer.colors.GREEN
        )
        raise typer.Exit(code=0)

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
            typer.secho(
                "No profiles selected. Using minimal configuration.",
                fg=typer.colors.YELLOW, bold=True
            )
        else:
            typer.secho(
                'Selected profiles: ' + ', '.join(selected_profiles),
                fg=typer.colors.GREEN, bold=True
            )
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
            typer.secho(
                f"Projects directory set to: {project_dir}",
                fg=typer.colors.GREEN, bold=True
            )
            self.config.set_project_directory(project_dir)
            return
        elif not project_dir or project_dir.strip() == "":
            typer.secho(
                "You need to specify somewhere to keep your projects.",
                fg=typer.colors.RED
            )
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
                    return typer.secho(
                        f"Directory created at: {project_dir}",
                        fg=typer.colors.GREEN, bold=True
                    )
                except Exception as e:
                    typer.secho(
                        f"ERROR: Unable to create directory {project_dir}: {e}",
                        err=True, fg=typer.colors.RED, bold=True
                    )
                    return self.prompt_projects_dir()
            typer.secho(
                "Please set a directory to continue.",
                fg=typer.colors.RED, bold=True
            )
            return self.prompt_projects_dir()

    def prompt_restart(self) -> None:
        # Ask the user if they want to (re)start the service containers
        restart_services = questionary.confirm(
            "Do you want to (re)start the service containers now?",
            default=True,
            style=anydev_qsty_styles
        ).unsafe_ask()

        if restart_services:
            typer.secho("Stopping any running service containers...", fg=typer.colors.YELLOW, bold=True)
            subprocess.run(['docker', 'compose', '--profile', '*', 'down'], cwd=self.config.cli_root_dir)

            typer.secho(
                "Starting your service containers...",
                        fg=typer.colors.YELLOW, bold=True
            )
            profiles = self.config.get_active_profiles()
            profile_args = []
            for profile in profiles:
                profile_args.extend(["--profile", profile])
            subprocess.run(["docker-compose"] + profile_args + ["up", "-d"], cwd=self.config.cli_root_dir)

            # TODO: Exception handling
