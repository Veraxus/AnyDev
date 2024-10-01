import os
import questionary
import re
import shutil
import typer
import webbrowser
from anydev.configuration import Configuration
from anydev.core.cli_output import CliOutput
from anydev.core.project_helpers import ProjectHelpers
from anydev.core.questionary_styles import anydev_qsty_styles
from dotenv import set_key, get_key


class CreateProject:
    """
    Class to handle creation of new projects (including state during the process).
    """

    def __init__(self):
        self.config = Configuration()
        self.entered_project_hostname = None
        self.entered_project_title = None
        self.sanitized_project_title = None
        self.project_path = None
        self.template_name = None

    def prompt(self) -> None:
        # TODO: Halt if AnyDev is not configured

        # 1. Prompt user for directory
        self.create_project_directory()
        # 2. Prompt user for template
        self.prompt_template_select()
        # 3. Save project information to configs
        self.config.add_project(f"{self.entered_project_hostname}.site.test", self.project_path, self.template_name)
        # 4. Prompt for project configuration
        self.prompt_project_setup()

    def create_project_directory(self) -> None:
        """ Runs the interactive process for creating a new project directory.
            1. Prompts the user to enter and confirm the name for the project.
            2. Sanitizes the name.
            3. Checks for the existence of a directory with the same name.
            4. Creates the project directory if confirmed by the user.

        Raises:
            typer.Exit: If the directory already exists or the user aborts directory creation.
        """

        # Initial questions!
        self.entered_project_hostname = typer.prompt('Enter a simple hostname for your project (e.g. "foo", "bar", "foo-bar")')
        if not typer.confirm(
                f"Do you want to use the default folder name ({self.entered_project_hostname}.site.test)?",
                default=True
        ):
            self.entered_project_title = typer.prompt(
                "Enter the folder name to use for this project",
                default=f"{self.entered_project_hostname}.site.test"
            )
        else:
            self.entered_project_title = f"{self.entered_project_hostname}.site.test"
        self.sanitized_project_title = self.sanitize_folder_name(self.entered_project_title)

        # Check if current directory is AnyDev default projects directory
        projects_dir = self.config.get_project_directory()
        current_directory = os.getcwd()
        if current_directory != projects_dir:
            CliOutput.alert("Current directory is not your configured projects directory!")
            if not typer.confirm(
                f"Use your project directory instead? (N will create here)",
                default=True
            ):
                # Use the current directory
                self.project_path = os.path.join(current_directory, self.sanitized_project_title)
            else:
                # Use the project directory
                self.project_path = os.path.join(projects_dir, self.sanitized_project_title)
        else:
            # Use the project directry
            self.project_path = os.path.join(projects_dir, self.sanitized_project_title)

        # Starting validating...
        if os.path.exists(self.project_path):
            # The directory already exists!!!
            if os.listdir(self.project_path):
                # The directory is NOT empty. Abort.
                CliOutput.error(f"Directory '{os.path.basename(self.project_path)}' already exists and is not empty. Please choose a different name.")
                raise typer.Exit(code=1)
            else:
                # Hey, the directory was empty! Use it?
                if not typer.confirm(
                        f"Directory '{self.project_path}' already exists but is empty. Would you like to use it?",
                        default=True
                ):
                    # User said no thanks :'(
                    CliOutput.alert("Project creation cancelled.", True)
                else:
                    CliOutput.success(f"Using existing directory at {self.project_path}.")
                    return
        else:
            try:
                os.makedirs(self.project_path)
                CliOutput.success(f"Created directory at {self.project_path}.")
            except OSError as e:
                CliOutput.error(f"Failed to create directory at '{os.path.basename(self.project_path)}': {e}")

    def prompt_template_select(self) -> None:
        """Handles interactive process of copying template files into project directory."""

        # Dynamically fetch templates from template directory
        template_dir = self.config.templates_dir
        try:
            template_dir_contents = os.listdir(template_dir)
            templates = [name for name in template_dir_contents if os.path.isdir(template_dir + "/" + name)]
        except FileNotFoundError:
            CliOutput.error(f"Templates directory not found at '{template_dir}'.", False)
        except PermissionError:
            CliOutput.error(f"Permission denied for template directory '{template_dir}'.", False)

        # Select prompt from available templates
        self.template_name = questionary.select(
            "Which template do you want to use?",
            choices=templates,
            use_indicator=True,
            style=anydev_qsty_styles
        ).unsafe_ask()

        # Copy template to target directory
        self.copy_template_files(self.template_name)

    def copy_template_files(self, template_dir: str) -> None:
        """
        Copies the files from the selected template directory to the created project directory.
        """

        # Get the path to the template directory
        source_template_path = self.config.templates_dir + '/' + template_dir

        # Is something wrong with template path?
        if not os.path.exists(source_template_path):

            CliOutput.error(f"Template directory '{source_template_path}' not found.", True)

        try:
            # Attempt to copy the template!
            shutil.copytree(source_template_path, self.project_path, dirs_exist_ok=True)
            CliOutput.success(f"Template files copied to '{self.project_path}'")
        except Exception as e:
            CliOutput.error(f"Failed to copy template files: {e}", True)

    def prompt_project_setup(self) -> None:
        """
        Prompts the user to configure and start the project if desired.

        This method asks the user if they want to configure and start the project.
        If the user confirms, it updates environment files, creates an environment
        file from a template, and restarts the project composition. Finally, it
        provides success messages with the project URL and location.

        Raises:
            typer.Exit: Exits the application after the configuration process.
        """
        if typer.confirm("Would you like me to configure and start the project for you?", default=True):
            self._update_env()
            self._create_env_file()
            ProjectHelpers.restart_composition(self.project_path)
            CliOutput.success("Project configured and started!")
            CliOutput.success(f"URL: https://{self.entered_project_hostname}.site.test")
            CliOutput.success(f"Project Location: {self.project_path}")

            # TODO: Make optional?
            webbrowser.open(f"https://{self.entered_project_hostname}.site.test")
        else:
            CliOutput.alert("Project configuration completed.")
        raise typer.Exit(code=0)

    def _update_env(self, filename: str = '.env.example') -> None:
        """Set the values in the .env.example file."""

        # Location of env file for current project
        dotenv_path = f"{self.project_path}/{filename}"

        # Change the value of the HOSTNAME variable
        set_key(dotenv_path, 'HOSTNAME', self.entered_project_hostname)
        set_key(dotenv_path, 'COMPOSE_PROJECT_NAME', f"{self.sanitized_project_title}.site.test")

    def _create_env_file(self) -> None:
        """Copy .env.example to .env"""
        env_example_path = os.path.join(self.project_path, '.env.example')
        env_path = os.path.join(self.project_path, '.env')

        try:
            shutil.copy(env_example_path, env_path)
            CliOutput.success("Successfully created .env file.")
        except PermissionError:
            CliOutput.error(f"Permission denied. Unable to create .env", True)
        except Exception as e:
            CliOutput.error(f"Failed to create .env: {e}", True)

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
        allowed_chars = r'[^\w\-\s\.]'
        sanitized_name = re.sub(allowed_chars, '_', folder_name).strip()
        return sanitized_name[:255]  # Truncate to max length of 255
