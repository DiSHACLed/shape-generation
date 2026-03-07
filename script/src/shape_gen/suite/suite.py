from ..prelude import Typer
from typing import Annotated
from pathlib import Path
import typer

from ..config import SAMPLE_DATA, RESULTS

from .task import Task, execute

from .tasks import play, qse
from .tasks import qse, ntriples, shexer, virtuoso, void, play

tasks : list[Task] = [
    ntriples.task, 
    qse.task,
    shexer.task,
    virtuoso.task,
    void.task,
    play.task,
    ]

lookup : dict[str,Task] = { task.code : task for task in tasks  }

keys : list[str] = [ file.stem for file in SAMPLE_DATA.iterdir() if file.suffix == '.ttl' ]

for key in keys :
    assert (SAMPLE_DATA/Path(f"{key}.ttl")).exists()

def valid_keys(candidates : list[str]) :
    if all (candidate in keys for candidate in candidates) :
        return candidates
    else :
        raise typer.BadParameter(f"Keys must be in {keys}")

def valid_codes(candidates : list[str]) :
    valid_codes = lookup.keys()
    if all (candidate in valid_codes for candidate in candidates) :
        return candidates
    else :
        raise typer.BadParameter(f"{candidates} must all be in {valid_codes}")

suite_typer = Typer()


@suite_typer.command()
def run(sources : Annotated[list[str], typer.Argument(callback=valid_keys)] = keys,
            codes : list[str] = typer.Option([ task.code for task in tasks ], "--tasks", "-t", callback=valid_codes)) :

    for code in codes :
        (RESULTS/Path(code)).mkdir(parents=False, exist_ok=True)
        task = lookup[code]
        for key in sources :
            execute(task, key)

@suite_typer.command()
def info() :
    print(f"\nttl-files found in {SAMPLE_DATA}: (refer to them *without* the extension in the `run` command)")
    for key in keys :
        print(f"- {key}")
    print(f"\ncurrently implemented tasks (results to {RESULTS}):")
    for task in tasks :
        print(f"- {task.code}")
        print(f"  description: {task.description}")