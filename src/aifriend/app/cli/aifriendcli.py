from pathlib import Path

import typer
from typer import Typer, Option, Context

from aifriend.app.cli import dashboard, api, worker, broker, backend
from aifriend.config import var, log

cli = Typer(name='AIfriend-cli', add_completion=False)

cli.add_typer(dashboard.cli, name='dashboard')
cli.add_typer(api.cli, name='api')
cli.add_typer(worker.cli, name='worker')
cli.add_typer(broker.cli, name='broker')
cli.add_typer(backend.cli, name='backend')


@cli.command(help="Initialize project's environment")
def init(base: Path = Option(Path().absolute(), '--base', '-b', help="Path to the project's base directory")) -> None:
    """
    Initialize project's environment.

    Parameters
    ----------
    base : Path, default='./'
        Path to the project's base directory.
    """

    base.mkdir(parents=True, exist_ok=True)

    with var.BASE_INIT.open(mode='w') as f:
        f.write(base.as_posix())

    typer.echo(typer.style("Project's environment is initialized.", fg=typer.colors.BRIGHT_BLUE))


@cli.command(name='download-artifacts', help='Download model artifacts')
def download_artifacts() -> None:
    """ Download model artifacts. """

    from transformers import AutoModelForCausalLM, AutoTokenizer

    AutoModelForCausalLM.from_pretrained(var.MODEL_ID, trust_remote_code=True, cache_dir=var.CHECKPOINTS_DIR)
    AutoTokenizer.from_pretrained(var.TOKENIZER_ID, cache_dir=var.CHECKPOINTS_DIR)

    log.project_console.print(f"The model artifacts are downloaded to the {var.CHECKPOINTS_DIR} folder",
                              style='bright_blue')


@cli.callback(invoke_without_command=True, help='')
def cli_state_verification(ctx: Context) -> None:
    """
    Perform cli commands verification (state checking) and config file parsing.

    Parameters
    ----------
    ctx : Context
        Typer (Click like) special internal object that holds state relevant
        for the script execution at every single level.
    """

    if ctx.invoked_subcommand == 'init':
        return
    elif not var.BASE_INIT.exists():
        typer.echo(typer.style('You need to initialize the project environment.\n'
                               'For more information use: trecover init --help',
                               fg=typer.colors.RED))
        ctx.exit(1)

    from aifriend.config import log

    if ctx.invoked_subcommand is None:
        log.project_console.print(ctx.get_help(), markup=False)
        ctx.exit(0)


if __name__ == '__main__':
    cli()
