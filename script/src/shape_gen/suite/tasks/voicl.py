from ..task import Task, Key
from pathlib import Path
from ...config import RESULTS
from ...virtuoso.cli import init, stop
from ...virtuoso.virtuoso import ENDPOINT
from . import void
from ...voicl.generator import generator
from ...prelude import graph_name

from contextlib import redirect_stdout, redirect_stderr

CODE = 'voicl'

def prep(key : Key) :
    try :
        stop() # just in case
    except :
        pass
    init(key)

def post(key : Key) :
    stop()

def meat(key : Key) :
    output_shacl_file = Path(f'{RESULTS}/{CODE}/{key}.ttl')
    log_file = Path(f'{RESULTS}/{CODE}/{key}.log')
    void_input_file = Path(f'{RESULTS}/{void.CODE}/{key}.ttl')

    if not void_input_file.is_file() :
        raise RuntimeError(f"{void_input_file} does not exist")

    with open(log_file, "w") as f:
        with redirect_stdout(f), redirect_stderr(f):
            generator(
                data_graph = graph_name(key),
                data_endpoint = ENDPOINT,
                output = output_shacl_file,
                void_file=void_input_file,
                interactive=False
            )

task = Task(
    description = f"generate SHACL from endpoint and void file (depends on {void.CODE})",
    code = CODE,
    done = (lambda key : (RESULTS/Path(f"{CODE}/{key}.ttl")).is_file()),
    meat = meat,
    prep = prep,
    post = post,
    )