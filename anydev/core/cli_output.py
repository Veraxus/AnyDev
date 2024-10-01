import typer


class CliOutput:

    @staticmethod
    def success(message, auto_exit: bool = False):
        typer.secho(message, fg=typer.colors.GREEN, bold=True)
        if auto_exit:
            raise typer.Exit(code=0)

    @staticmethod
    def error(message, auto_exit: bool = True, exit_code: int = 1):
        typer.secho(f"ERROR: {message}", err=True, fg=typer.colors.RED, bold=True)
        if auto_exit:
            raise typer.Exit(code=exit_code)

    @staticmethod
    def warning(message):
        typer.secho(f"WARNING: {message}", fg=typer.colors.RED, bold=True)

    @staticmethod
    def alert(message, auto_exit: bool = False):
        typer.secho(f"{message}", fg=typer.colors.RED, bold=True)
        if auto_exit:
            raise typer.Exit(code=1)

    @staticmethod
    def info(message):
        typer.secho(message, fg=(120, 120, 120), bold=False)
