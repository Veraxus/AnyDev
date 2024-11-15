import os.path
import tomllib
import typer

from anydev.commands import project as project_commands
from anydev.commands import services as services_commands
from anydev.configuration import Configuration
from anydev.core.cli_output import CliOutput
from anydev.core.command_alias_group import CommandAliasGroup
from anydev.core.configure_services import ConfigureServices

# Initialize CLI
main = typer.Typer(
    help="AnyDev CLI - Easily create and manage development environments.",
    no_args_is_help=True,
    cls=CommandAliasGroup
)

# Initialize configuration
config = Configuration()


# ==================
# Top-level commands
# ==================

@main.command("i | install")
def install():
    """Check your system for prerequisites and optionally install them."""
    CliOutput.warning('Not yet implemented.')


@main.command("c | configure")
@main.command("config", hidden=True)
def configure():
    """Add or remove services from your environments."""
    services = ConfigureServices()
    services.configure()


@main.command("v | version")
def version():
    """View current AnyDev version."""
    with open(os.path.join(config.cli_root_dir, 'pyproject.toml'), "rb") as f:
        data = tomllib.load(f)
        CliOutput.info(data['tool']['poetry']['version'])


# ==================
# Sub-commands
# ==================

# TODO: Pass-through p commands when current dir is a recognized project

# Project commands
main.add_typer(project_commands.cmd, name="p | project")
main.add_typer(project_commands.cmd, name="pr | proj", hidden=True)

# Shared services commands
main.add_typer(services_commands.cmd, name="s | services")
main.add_typer(services_commands.cmd, name="srv | svc | serv | service", hidden=True)

if __name__ == '__main__':
    main()
