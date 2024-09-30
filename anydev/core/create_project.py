import os
import questionary
import re
import shutil
import typer
from anydev.configuration import Configuration
from anydev.core.project_helpers import ProjectHelpers
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
            if not typer.confirm(
                f"Current directory ({current_directory}) is not your configured projects directory. Should I create it there, instead ({projects_dir})?",
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
                typer.secho(
                    f"ERROR: Directory '{os.path.basename(self.project_path)}' already exists and is not empty. Please choose a different name.",
                    err=True, fg=typer.colors.RED, bold=True
                )
                raise typer.Exit(code=1)
            else:
                # Hey, the directory was empty! Use it?
                if not typer.confirm(
                        f"Directory '{self.project_path}' already exists but is empty. Would you like to use it?",
                        default=True
                ):
                    # User said no thanks :'(
                    typer.secho("Project creation cancelled.", fg=typer.colors.YELLOW, bold=True)
                    raise typer.Exit(code=1)
                else:
                    typer.secho(
                        f"Using existing directory at {self.project_path}.",
                        fg=typer.colors.GREEN, bold=True
                    )
                    return
        else:
            try:
                os.makedirs(self.project_path)
                typer.secho(
                    f"Directory created successfully at {self.project_path}.",
                    fg=typer.colors.GREEN, bold=True
                )
            except OSError as e:
                typer.secho(
                    f"ERROR: Failed to create directory at '{os.path.basename(self.project_path)}': {e}",
                    err=True, fg=typer.colors.RED, bold=True
                )
                raise typer.Exit(code=1)

    def prompt_template_select(self) -> None:
        """Handles interactive process of copying template files into project directory."""

        # Dynamically fetch templates from template directory
        template_dir = self.config.templates_dir_path
        try:
            template_dir_contents = os.listdir(template_dir)
            templates = [name for name in template_dir_contents if os.path.isdir(template_dir, name)]
        except FileNotFoundError:
            typer.secho(
                f"ERROR: Templates directory not found at '{template_dir}'.",
                err=True, fg=typer.colors.RED, bold=True
            )
        except PermissionError:
            typer.secho(
                f"ERROR: Permission denied for template directory '{template_dir}'.",
                err=True, fg=typer.colors.RED, bold=True
            )

        # Select prompt from available templates
        self.template_name = questionary.select(
            "Which template do you want to use?",
            choices=templates,
            use_indicator=True,
            style=self.config.questionary_style
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
            typer.secho(
                f"ERROR: Template directory '{source_template_path}' not found.",
                err=True, fg=typer.colors.RED, bold=True
            )
            raise typer.Exit(code=1)

        try:
            # Attempt to copy the template!
            shutil.copytree(source_template_path, self.project_path, dirs_exist_ok=True)
            typer.secho(
                f"Template files from '{template_dir}' copied to '{self.project_path}'",
                fg=typer.colors.GREEN, bold=True
            )
        except Exception as e:
            typer.secho(
                f"ERROR: Failed to copy template files: {e}",
                err=True, fg=typer.colors.RED, bold=True
            )
            raise typer.Exit(code=1)

        typer.secho("Template successfully copied!", fg=typer.colors.GREEN, bold=True)

    def prompt_project_setup(self) -> None:
        if typer.confirm("Would you like me to configure and start the project for you?", default=True):
            self._update_env()
            self._create_env_file()
            ProjectHelpers.restart_composition(self.project_path)
            typer.secho(
                f"All done!",
                fg=typer.colors.GREEN, bold=True
            )
            typer.secho(
                f"Browser URL: https://{self.entered_project_hostname}.site.test",
                fg=typer.colors.GREEN, bold=True
            )
            typer.secho(
                f"Project Location: {self.project_path}",
                fg=typer.colors.GREEN, bold=True
            )
        else:
            typer.secho("Project creation completed. It's in your hands now!", fg=typer.colors.GREEN, bold=True)
        raise typer.Exit(code=0)

    def _update_env(self, filename: str = '.env.example') -> None:
        """Set the values in the .env.example file."""
        dotenv_path = f"{self.project_path}/{filename}"

        # Change the value of the HOSTNAME variable
        set_key(dotenv_path, 'HOSTNAME', self.entered_project_hostname)

        # Confirm!
        confirm_value = get_key(dotenv_path, 'HOSTNAME')

        if confirm_value != self.entered_project_hostname:
            raise ValueError(f"Failed to set HOSTNAME. Expected '{self.entered_project_hostname}', but got '{confirm_value}'")

    def _create_env_file(self) -> None:
        """Copy .env.example to .env"""
        env_example_path = os.path.join(self.project_path, '.env.example')
        env_path = os.path.join(self.project_path, '.env')

        try:
            shutil.copy(env_example_path, env_path)
            typer.secho("Successfully created .env", fg=typer.colors.GREEN, bold=True)
        except PermissionError:
            typer.secho(
                f"ERROR: Permission denied. Unable to create .env",
                err=True, fg=typer.colors.RED, bold=True
            )
            raise typer.Exit(code=1)
        except Exception as e:
            typer.secho(
                f"ERROR: Failed to create .env: {e}",
                err=True, fg=typer.colors.RED, bold=True
            )
            raise typer.Exit(code=1)

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
