import typer

from anydev.configuration import Configuration
from anydev.core.command_alias_group import CommandAliasGroup
from anydev.core.docker_controls import DockerHelpers

# Get config object
config = Configuration()

# Initialize Typer for the project sub-commands
cmd = typer.Typer(
    help="Manage and interact with shared services.",
    no_args_is_help=True,
    cls=CommandAliasGroup
)

@cmd.command('r | restart')
@cmd.command('u | up', hidden=True)
def restart():
    """Start or restart services."""
    DockerHelpers.restart_composition(
        config.cli_root_dir,
        config.get_active_profiles()
    )

@cmd.command('s | stop')
@cmd.command('u | up', hidden=True)
def restart():
    """Stop the services."""
    DockerHelpers.stop_composition(config.cli_root_dir)

