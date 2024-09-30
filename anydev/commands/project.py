import typer

from anydev.core.command_alias_group import CommandAliasGroup
from anydev.core.project_helpers import ProjectHelpers

# Initialize Typer for the project sub-commands
cmd = typer.Typer(
    help="List, create, and manage your projects.",
    no_args_is_help=True,
    cls=CommandAliasGroup
)


@cmd.command('c | create')
def create():
    """Create a new project."""
    from anydev.core.create_project import CreateProject
    project_creator = CreateProject()
    project_creator.prompt()


@cmd.command('a | add')
def add():
    """Add an existing project directory to AnyDev's memory."""
    print('Not yet implemented.')


@cmd.command('l | list')
@cmd.command('ls', hidden=True)
@ProjectHelpers.validate_project
def list_all():
    """List all projects."""
    print('Not yet implemented.')


@cmd.command('u | up')
@cmd.command('start', hidden=True)
@cmd.command('r | restart', hidden=True)
@ProjectHelpers.validate_project
def start():
    """Start or restart an existing project."""
    ProjectHelpers.restart_composition()


@cmd.command('d | down')
@cmd.command('stop', hidden=True)
@ProjectHelpers.validate_project
def stop():
    """Stop a running project."""
    ProjectHelpers.stop_project()


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
    typer.secho(f"Opening interactive shell with {shell_command}", err=True, fg=typer.colors.YELLOW, bold=True)
    ProjectHelpers.open_shell(shell_command)
