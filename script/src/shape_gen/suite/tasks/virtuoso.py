from ..task import Task, Key
from ...config import RESULTS, SAMPLE_DATA, VIRTUOSO_DIR
from pathlib import Path

from ...virtuoso.cli import init, load, stop

from contextlib import redirect_stdout, redirect_stderr

CODE = 'virtuoso'

def done(key : Key) :
    return Path(f"{VIRTUOSO_DIR}/{key}-db/virtuoso.db").is_file()

def prep(key : Key) :
    try :
        stop() # just in case
    except :
        pass
    init(key)

def meat(key : Key) :
    input_file = Path(f'{SAMPLE_DATA}/{key}.ttl')
    log_file = Path(f"{RESULTS}/{CODE}/{key}.log")

    with open(log_file, "w") as f:
        with redirect_stdout(f), redirect_stderr(f):
            load(key, input_file)

def post(key : Key) :
    stop()

task = Task(
    description = "Shexer: generate SHACL from ttl ",
    code = CODE,
    done = done,
    meat = meat,
    prep = prep,
    post = post,
    )
