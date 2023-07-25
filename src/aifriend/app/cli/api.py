from typer import Typer, Option, Argument, Context

from aifriend.config import var, log

cli = Typer(name='API-cli', add_completion=False, help='Manage API service')


@cli.callback(invoke_without_command=True)
def api_state_verification(ctx: Context) -> None:
    """
    Perform cli commands verification (state checking).

    Parameters
    ----------
    ctx : Context
        Typer (Click like) special internal object that holds state relevant
        for the script execution at every single level.

    """

    if var.API_PID.exists():
        if ctx.invoked_subcommand in ('start', None):
            log.project_console.print(':rocket: The API service is already started', style='bright_blue')
            ctx.exit(0)

    elif ctx.invoked_subcommand is None:
        api_start(host=var.FASTAPI_HOST, port=var.FASTAPI_PORT, loglevel=var.LogLevel.info,
                  concurrency=var.FASTAPI_WORKERS, attach=False, no_daemon=False)

    elif ctx.invoked_subcommand not in ('start', 'talk'):
        log.project_console.print('The API service is not started', style='yellow')
        ctx.exit(1)


@cli.command(name='talk', help='Send talk API request')
def api_talk(message: str = Argument(..., help='New message for AI friend'),
             url: str = Option(var.FASTAPI_URL, help='API url')
             ) -> None:
    """
    Send talk API request.

    Parameters
    ----------
    message : str
        New message for AI friend.
    url : str
        API url.
    """

    import requests
    from time import time
    from aifriend.config import log

    payload = {
        'message': message,
        'history': [],
    }

    start_time = time()
    response = requests.post(url=f'{url}/talk', json=payload)
    response = response.json()

    log.project_console.print(f'Elapsed: {time() - start_time:>7.3f} s\n', style='bright_blue')
    log.project_console.print(f'Human: {message} ', style='yellow')
    log.project_console.print(f'AI: {response["response_message"]} ', style='green')


@cli.command(name='start', help='Start service')
def api_start(host: str = Option(var.FASTAPI_HOST, '--host', '-h', help='Bind socket to this host.'),
              port: int = Option(var.FASTAPI_PORT, '--port', '-p', help='Bind socket to this port.'),
              loglevel: var.LogLevel = Option(var.LogLevel.info, '--loglevel', '-l', help='Logging level.'),
              concurrency: int = Option(var.FASTAPI_WORKERS, '-c', help='The number of worker processes.'),
              attach: bool = Option(False, '--attach', '-a', is_flag=True,
                                    help='Attach output and error streams'),
              no_daemon: bool = Option(False, '--no-daemon', is_flag=True, help='Do not run as a daemon process')
              ) -> None:
    """
    Start API service.

    Parameters
    ----------
    host : str, default=ENV(FASTAPI_HOST) or 'localhost'
        Bind socket to this host.
    port : int, default=ENV(FASTAPI_PORT) or 8001
        Bind socket to this port.
    loglevel : {'debug', 'info', 'warning', 'error', 'critical'}, default='info'
        Level of logging.
    concurrency : int, default=ENV(FASTAPI_WORKERS) or 1
        The number of worker processes.
    attach : bool, default=False
        Attach output and error streams.
    no_daemon : bool, default=False
        Do not run as a daemon process.

    """

    from subprocess import run

    from aifriend.config import log
    from aifriend.utils.cli import start_service

    argv = [
        'uvicorn', 'aifriend.app.api.aifriendapi:api',
        '--host', host,
        '--port', str(port),
        '--workers', str(concurrency),
        '--log-level', loglevel
    ]

    if no_daemon:
        run(argv)
    else:
        start_service(argv, name='API', logfile=log.API_LOG, pidfile=var.API_PID)

        if attach:
            api_attach(live=False)


@cli.command(name='stop', help='Stop service')
def api_stop() -> None:
    """ Stop API service. """

    from aifriend.config import log
    from aifriend.utils.cli import stop_service

    stop_service(name='API', pidfile=var.API_PID, logfile=log.API_LOG)


@cli.command(name='status', help='Display service status')
def api_status() -> None:
    """ Display API service status. """

    from aifriend.utils.cli import check_service

    check_service(name='API', pidfile=var.API_PID)


@cli.command(name='attach', help='Attach local output stream to a service')
def api_attach(live: bool = Option(False, '--live', '-l', is_flag=True,
                                   help='Stream only fresh log records')
               ) -> None:
    """
    Attach local output stream to a running API service.

    Parameters
    ----------
    live : bool, Default=False
        Stream only fresh log records

    """

    from aifriend.utils.cli import stream

    with log.project_console.screen():
        for record in stream(('API', log.API_LOG), live=live):
            log.project_console.print(record)

    log.project_console.clear()


if __name__ == '__main__':
    cli()
