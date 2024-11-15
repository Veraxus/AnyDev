import typer
import webbrowser

from anydev.core.cli_output import CliOutput
from anydev.core.command_alias_group import CommandAliasGroup
from anydev.core.create_project import CreateProject
from anydev.core.docker_controls import DockerHelpers
from anydev.commands.project_helpers import ProjectHelpers

# Initialize Typer for the project sub-commands
cmd = typer.Typer(
    help="List, create, and manage your projects.",
    no_args_is_help=True,
    cls=CommandAliasGroup
)


@cmd.command('c | create')
def create():
    """Create a new project."""
    project_creator = CreateProject()
    project_creator.prompt()


@cmd.command('a | add')
def add():
    """WIP. Add an existing project directory to AnyDev's memory."""
    CliOutput.error('Not yet implemented.')


@cmd.command('l | list')
@cmd.command('ls', hidden=True)
def list_all():
    """List all projects."""
    ProjectHelpers.list_projects()


@cmd.command('u | up')
@cmd.command('start', hidden=True)
@cmd.command('r | restart', hidden=True)
@ProjectHelpers.validate_project
def start():
    """Start or restart an existing project."""
    DockerHelpers.restart_composition()


@cmd.command('d | down')
@cmd.command('stop', hidden=True)
@ProjectHelpers.validate_project
def stop():
    """Stop a running project."""
    DockerHelpers.stop_composition()


@cmd.command('g | logs')
@cmd.command('log', hidden=True)
@ProjectHelpers.validate_project
def logs():
    """Tail the container logs."""
    ProjectHelpers.tail_container_logs()


@cmd.command('t | terminal')
@ProjectHelpers.validate_project
def terminal(
        shell_command: str = typer.Argument(
            "/bin/sh",
            help="Type of terminal/shell to open (e.g., sh, bash, zsh, etc.)"
        )
):
    """Open command for the current project container."""
    CliOutput.info(f"Opening terminal with {shell_command}")
    ProjectHelpers.open_shell(shell_command)


@cmd.command('b | bash', hidden=True)
def bash():
    terminal(shell_command="/bin/bash")


@cmd.command('v | view')
@cmd.command('browser', hidden=True)
@ProjectHelpers.validate_project
def browser():
    """Open default browser to current project's .site.test URL."""
    project_details = ProjectHelpers.get_project_details()
    if 'name' in project_details:
        project_name = project_details['name']
        url = f"https://{project_name}"
        CliOutput.info(f"Opening {url} in your default browser.")
        webbrowser.open(url)
    else:
        CliOutput.error("Project name not found. Cannot open the browser.")

