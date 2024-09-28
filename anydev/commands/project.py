import typer
import subprocess

from anydev.core.command_alias_group import CommandAliasGroup

from anydev.core.project_helpers import is_running, validate_project

# Initialize Typer for the project sub-commands
cmd = typer.Typer(
    help="List, create, and manage your projects.",
    no_args_is_help=True,
    cls=CommandAliasGroup
)


@cmd.command('c | create')
def create():
    """Create a new project."""
    print('Not yet implemented.')


@cmd.command('l | list')
@cmd.command('ls', hidden=True)
@validate_project
def list():
    """List all projects."""
    print('Not yet implemented.')


@cmd.command('u | up')
@cmd.command('start', hidden=True)
@cmd.command('restart', hidden=True)
@validate_project
def start():
    """Start or restart an existing project."""

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


@cmd.command('d | down')
@cmd.command('stop', hidden=True)
@validate_project
def stop():
    """Stop a running project."""
    if is_running():
        typer.secho('Stopping project...', fg=typer.colors.YELLOW, bold=True)
        subprocess.run(['docker', 'compose', 'down'])
    else:
        typer.secho('Project is not running.', err=True, fg=typer.colors.YELLOW, bold=True)


@cmd.command('s | shell')
@cmd.command('sh', hidden=True)
@validate_project
def shell():
    """Open shell for the current project container."""
    proc_command = ['docker', 'compose', 'exec', 'app', '/bin/sh']
    result = subprocess.run(proc_command)
    if result.returncode != 0:
        typer.secho('ERROR: Command failed: ' + ' '.join(proc_command), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=result.returncode)


@cmd.command('g | logs')
@cmd.command('log', hidden=True)
@validate_project
def logs():
    """Tail the container logs."""
    if is_running():
        proc_command = ['docker', 'compose', 'logs', 'app', '-f']
        result = subprocess.run(proc_command)
        if result.returncode != 0:
            typer.secho('ERROR: Command failed: ' + ' '.join(proc_command), err=True, fg=typer.colors.RED,
                        bold=True)
            raise typer.Exit(code=result.returncode)
    else:
        typer.secho('The project is not currently running.', err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)
