from ..task import Task, Key
from pathlib import Path

from ...virtuoso.cli import init, stop
from ...virtuoso.virtuoso import ENDPOINT
from ... import void
from ...prelude import graph_name
from . import virtuoso

from contextlib import redirect_stdout, redirect_stderr

from ...config import RESULTS

CODE = 'void'

def done(key : Key) :
    return Path(f"{RESULTS}/{CODE}/{key}.ttl").is_file()

def prep(key : Key) :
    try :
        stop()
    except :
        pass
    init(key)

def meat(key : Key) :
    log_file = Path(f"{RESULTS}/{CODE}/{key}.log")
    output_file = Path(f"{RESULTS}/{CODE}/{key}.ttl")

    with open(log_file, "w") as f:
        with redirect_stdout(f), redirect_stderr(f):
            void.generate(ENDPOINT, graph_name(key), key, output_file)

def post(key : Key) :
    stop()

task = Task(
    description = f"generate void from endpoint (depends on {virtuoso.CODE})",
    code = CODE,
    done = done,
    meat = meat,
    prep = prep,
    post = post,
    )