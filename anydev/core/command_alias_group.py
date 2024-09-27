import re
import typer
import typer.core


class CommandAliasGroup(typer.core.TyperGroup):
    """Typer Group subclass that enables command aliases.
    1. Add to typer instance with cls=CommandAliasGroup
    2. specify names like @main.command(name="i | install")
    """

    _CMD_SPLIT_P = re.compile(r"\s*\|\s*")

    def get_command(self, ctx, cmd_name):
        """Find the command OBJECT matching the given name."""
        cmd_name = self._group_cmd_name(self.commands.values(), cmd_name)
        return super().get_command(ctx, cmd_name)

    def _group_cmd_name(self, group_command_names, default_name):
        """Find the command NAME matching the given default name."""
        for cmd in group_command_names:
            names = self._CMD_SPLIT_P.split(cmd.name)
            if cmd.name and default_name in names:
                return cmd.name
        return default_name
