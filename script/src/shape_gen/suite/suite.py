from os import mkdir
from ..prelude import Typer
from typing import Annotated
from pathlib import Path
import typer
import json
from rdflib import Graph

from ..config import JAVA_HEAP_SIZE, SAMPLE_DATA, RESULTS

from .task import Task, execute

from .tasks import play, qse
from .tasks import qse, ntriples, shexer, shexer_profile, shexer_bunch, virtuoso, void, play, voicl

tasks : list[Task] = [
    ntriples.task, 
    qse.task,
    shexer.task,
    shexer_profile.task,
    shexer_bunch.task,
    # shexer_memory.task,
    virtuoso.task,
    void.task,
    play.task,
    voicl.task,
    ]

lookup : dict[str,Task] = { task.code : task for task in tasks  }

keys : list[str] = [ file.stem for file in SAMPLE_DATA.iterdir() if file.suffix == '.ttl' ]

for key in keys :
    assert (SAMPLE_DATA/Path(f"{key}.ttl")).exists()

def valid(all : list[str]) :
    def _valid(candidates : list[str]) :
        for candidate in candidates :
            if candidate not in all :
                raise typer.BadParameter(f"{candidate} not in {keys}")
        return candidates
    return _valid

suite_typer = Typer()

@suite_typer.command()
def run(sources : Annotated[list[str], typer.Argument(callback=valid(keys))] = keys,
            codes : list[str] = typer.Option([ task.code for task in tasks ], "--tasks", "-t", callback=valid(list(lookup.keys()))),
            exclude_codes : list[str] = typer.Option([], "--exclude-tasks", "-e", callback=valid(list(lookup.keys()))),
            overwrite : bool = False
            ) :

    for code in (code for code in codes if code not in exclude_codes ) :
        (RESULTS/Path(code)).mkdir(parents=False, exist_ok=True)
        task = lookup[code]
        for key in sources :
            execute(task, key, overwrite)

@suite_typer.command()
def info() :
    print(f"\nttl-files found in {SAMPLE_DATA}: (refer to them *without* the extension in the `run` command)")
    for key in keys :
        print(f"- {key}")
    print(f"\ncurrently implemented tasks (results to {RESULTS}):")
    for task in tasks :
        print(f"- {task.code}")
        print(f"  description: {task.description}")

shape_tasks : list[Task] = [
    qse.task,
    # shexer.task,
    shexer_bunch.task,
    play.task,
    voicl.task,
    ]

from .validate import generic_vals, validate
from .statistics import statistics as stats

def _get_shacls(code : str, key : str) -> list[Path] :
    candidate_dir = Path(f"{RESULTS}/{code}/{key}")
    candidate_file = Path(f"{RESULTS}/{code}/{key}.ttl")
    if candidate_dir.exists() :
        shacl_files = list(Path(f"{RESULTS}/{code}/{key}").glob('**/*.ttl'))
    elif candidate_file.exists() :
        shacl_files = [ candidate_file ]
    else :
        shacl_files = []
    return shacl_files

@suite_typer.command()
def validation(sources : Annotated[list[str], typer.Argument(callback=valid(keys))] = keys,
               codes : list[str] = typer.Option([ task.code for task in shape_tasks ], "--tasks", "-t", callback=valid([shape_task.code for shape_task in shape_tasks])),
               exclude_codes : list[str] = typer.Option([], "--exclude-tasks", "-e", callback=valid([shape_task.code for shape_task in shape_tasks])),
               overwrite : bool = False
            ) :
    for code in (code for code in codes if code not in exclude_codes ) :
        task = lookup[code]
        for key in sources :
            print(f"validation for {task.code} / {key}")
            if task.validate == None :
                generic_vals(code, key, overwrite)
            else :
                task.validate(key,overwrite)

from .statistics import generic_stats

@suite_typer.command()
def stats(sources : Annotated[list[str], typer.Argument(callback=valid(keys))] = keys,
               codes : list[str] = typer.Option([ task.code for task in shape_tasks ], "--tasks", "-t", callback=valid([shape_task.code for shape_task in shape_tasks])),
               exclude_codes : list[str] = typer.Option([], "--exclude-tasks", "-e", callback=valid([shape_task.code for shape_task in shape_tasks])),
               overwrite : bool = False,
               both : bool = True
            ) :
    for code in (code for code in codes if code not in exclude_codes ) :
        task = lookup[code]
        for key in sources :
            print(f"stats for {task.code} / {key}")
            if task.stats == None :
                generic_stats(code, key)
            else :
                task.stats(key)

from .report import excel as excel_gen, REPORT_JSON, REPORT_EXCEL

@suite_typer.command()
def excel():
    f"""make excel from push results of {REPORT_JSON} into {REPORT_EXCEL}"""
    excel_gen()

from .java_memory import derive_min_ram
from . import java_memory
from ..virtuoso.cli import init, stop
from .report import report_add

INITIAL_MB = 1024*JAVA_HEAP_SIZE

@suite_typer.command()
def java_mem(sources : Annotated[list[str], typer.Argument(callback=valid(keys))] = keys):
    Path('/tmp/java-memory').mkdir(exist_ok=True)
    for key in sources :
        # init(key) # for things that need sparql endpoint
        for func , code in [ (java_memory.qse, 'qse') ] :
            mn_mb = derive_min_ram(func, key, INITIAL_MB, granularity=100)
            report_add('memory', code, key, str(mn_mb))
        # stop(key) # for things that need sparql endpoint

from .tasks import shexer_memory

python_tasks : list[Task] = [ shexer_memory.task ]

@suite_typer.command()
def python_mem(sources : Annotated[list[str], typer.Argument(callback=valid(keys))] = keys):
    for task in python_tasks :
        for key in sources :
            execute(task, key, True)