# import os
import docker
from typing import Optional

import typer
from docker import DockerClient
# from rich.console import Console

from .config import ROOTLESS, SOCKET

from pathlib import Path

# INF_CONSOLE = Console(stderr=True)
# ERR_CONSOLE = Console(stderr=True)

def docker_connect(time_out : int =60) -> DockerClient :
    return DockerClient(base_url=SOCKET) if ROOTLESS else docker.from_env()

CLIENT = docker_connect()

def Typer():
    return typer.Typer(
        no_args_is_help=True,
        pretty_exceptions_show_locals=True)

def base(path : Path) -> str :
    """given input ttl file, get base key; base(../mandaten.ttl) = mandaten"""
    p = Path(path)
    assert p.suffix == '.ttl'
    return p.stem

def graph_name(key : str, suffix : Optional[str] = None) :
    return f"http://www.example.com/{key}{('-' + suffix) if suffix is not None else ""}"