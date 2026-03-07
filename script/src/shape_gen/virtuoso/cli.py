from pathlib import Path
from typing import Optional

from ..prelude import Typer, graph_name, CLIENT

from . import virtuoso

virtuoso_typer = Typer()

@virtuoso_typer.command()
def init(key : str) :
    """initiate docker container..."""
    virtuoso.init(key)

@virtuoso_typer.command() 
def load(key : str, ttl_file : Path, target_graph : Optional[str] = None, check_empty : bool = False) -> None :
    """loads ttl_file given container"""
    container = CLIENT.containers.get(f'virtuoso-{key}')
    target_graph = graph_name(key) if not target_graph else target_graph
    virtuoso.load(container, ttl_file, target_graph, check_empty)

@virtuoso_typer.command() 
def stop() : # assuming only one running at a time (otherwise, dynamic ports)
    container = next ( 
        container for container in CLIENT.containers.list(filters={'status': 'running'}) 
            if container.name and container.name.startswith('virtuoso-')
        )
    container.stop()

# @virtuoso_typer.command() 
# def start(key : str) :
#     container = CLIENT.containers.get(f'virtuoso-{key}')
#     # container in CLIENT.containers.list(filters={'status': 'exited'}) 
#             # if container.name and container.name = ('virtuoso-')
#         # )
#     container.start()
