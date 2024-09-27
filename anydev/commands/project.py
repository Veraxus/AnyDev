import typer
import subprocess
from anydev.core.command_alias_group import CommandAliasGroup

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
def list():
    """List all projects."""
    print('Not yet implemented.')


@cmd.command('u | up')
@cmd.command('start', hidden=True)
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


@cmd.command('d | down')
@cmd.command('stop', hidden=True)
def stop():
    """Stop a running project."""
    is_running = subprocess.run(['docker', 'compose', 'ps', '--format', 'json'], capture_output=True, text=True)
    if len(is_running.stdout.strip()) > 0:
        typer.secho('Stopping project...', fg=typer.colors.YELLOW, bold=True)
        subprocess.run(['docker', 'compose', 'down'])
    else:
        typer.secho('Project is not running.', err=True, fg=typer.colors.YELLOW, bold=True)


@cmd.command('s | shell')
@cmd.command('sh', hidden=True)
def shell():
    """Open shell for the current project container."""
    result = subprocess.run(['docker', 'compose', 'exec', 'web', '/bin/sh'])
    if result.returncode != 0:
        typer.secho('', err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=result.returncode)
