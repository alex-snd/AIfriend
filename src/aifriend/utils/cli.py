import os
import platform
import time
from pathlib import Path
from subprocess import Popen, STDOUT
from typing import Optional, List, Tuple, Generator, Union

import psutil

from aifriend.config import var, log


def start_service(argv: List[str], name: str, logfile: Path, pidfile: Path) -> None:
    """
    Start service as a new process with given pid and log files.

    Parameters
    ----------
    argv : List[str]
        New process command.
    name : str
        Service name.
    logfile : Path
        Service logfile path.
    pidfile : Path
        Service pidfile path.

    """

    if platform.system() == 'Windows':
        from subprocess import CREATE_NO_WINDOW

        process = Popen(argv, creationflags=CREATE_NO_WINDOW, stdout=logfile.open(mode='w+'), stderr=STDOUT,
                        universal_newlines=True, start_new_session=True)
    else:
        process = Popen(argv, stdout=logfile.open(mode='w+'), stderr=STDOUT, universal_newlines=True,
                        start_new_session=True)

    with pidfile.open('w') as f:
        f.write(str(process.pid))

    log.project_console.print(f'The {name} service is started', style='bright_blue')


def stop_service(name: str, pidfile: Path, logfile: Path) -> None:
    """
    Send an interrupt signal to the process with given pid.

    Parameters
    ----------
    name : str
        Service name.
    pidfile : Path
        Service pidfile path.
    logfile : Path
        Service logfile path.

    """

    try:
        with pidfile.open() as f:
            pid = int(f.read())

        service = psutil.Process(pid=pid)

        for child_proc in service.children(recursive=True):
            child_proc.kill()

        if platform.system() != 'Windows':
            service.kill()

        service.wait()

        if logfile.exists():
            os.remove(logfile)

    except ValueError:
        log.project_console.print(f'The {name} service could not be stopped correctly'
                                  ' because its PID file is corrupted', style='red')
    except (OSError, psutil.NoSuchProcess):
        log.project_console.print(f'The {name} service could not be stopped correctly'
                                  ' because it probably failed earlier', style='red')
    else:
        log.project_console.print(f'The {name} service is stopped', style='bright_blue')

    finally:
        if pidfile.exists():
            os.remove(pidfile)


def check_service(name: str, pidfile: Path) -> None:
    """
    Display status of the process with given pid.

    Parameters
    ----------
    name : str
        Service name.
    pidfile : Path
        Service pidfile path.

    """

    try:
        with pidfile.open() as f:
            pid = int(f.read())

        if psutil.pid_exists(pid):
            log.project_console.print(f':rocket: The {name} status: running', style='bright_blue')
        else:
            log.project_console.print(f'The {name} status: dead', style='red')

    except FileNotFoundError:
        log.project_console.print(f'The {name} service is not started', style='yellow')

    except ValueError:
        log.project_console.print(f'The {name} service could not be checked correctly'
                                  ' because its PID file is corrupted', style='red')


def stream(*services: Union[Tuple[str, Path], Tuple[Tuple[str, Path]]],
           live: bool = False,
           period: float = 0.1
           ) -> Optional[Generator[str, None, None]]:
    """
    Get a generator that yields the services' stdout streams.

    Parameters
    ----------
    *services : Union[Tuple[str, Path], Tuple[Tuple[str, Path]]]
        Sequence of services' names and logfile's paths.
    live : bool, default=False
        Yield only new services' logs.
    period : float, default=0.1
        Generator's delay.

    Returns
    -------
    Optional[Generator[str, None, None]]:
        Generator that yields the services' stdout streams or None if services are stopped.

    """

    names = list()
    streams = list()
    alignment = 0

    try:
        for (name, log_file) in services:
            if not log_file.exists():
                continue

            names.append(name)

            service_stream = log_file.open()

            if live:
                service_stream.seek(0, 2)

            streams.append(service_stream)

            if len(name) > alignment:
                alignment = len(name)

        if not (n_services := len(names)):
            return None

        while True:
            for i in range(n_services):
                if record := streams[i].read().strip():
                    color = var.COLORS[i % len(var.COLORS)]

                    for record_line in record.split('\n'):
                        yield f'[{color}]{names[i]: <{alignment}} |[/{color}] {record_line}'

            time.sleep(period)

    finally:
        for service_stream in streams:
            service_stream.close()
