import typer
from anydev.commands import project
from anydev.core.command_alias_group import CommandAliasGroup
from anydev.core.configure_services import ConfigureServices

# Initialize CLI
main = typer.Typer(
    help="AnyDev CLI - Easily create and manage development environments.",
    no_args_is_help=True,
    cls=CommandAliasGroup
)


@main.command("i | install")
def install():
    """Check your system for prerequisites and optionally install them."""
    print('Not yet implemented.')


@main.command("c | configure")
@main.command("config", hidden=True)
def configure():
    """Add or remove services from your environments."""
    services = ConfigureServices()
    services.configure()


# Sub-commands
main.add_typer(project.cmd, name="p | project")
main.add_typer(project.cmd, name="proj", hidden=True)

if __name__ == '__main__':
    main()
