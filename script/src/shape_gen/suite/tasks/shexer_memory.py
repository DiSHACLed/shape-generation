from contextlib import redirect_stdout
from ..task import Task, Key
from ...config import RESULTS, SAMPLE_DATA, NAMESPACES
from pathlib import Path
import json

# import logging
from contextlib import redirect_stdout, redirect_stderr

from shexer.shaper import Shaper
from shexer.consts import TURTLE_ITER, SHACL_TURTLE, ALL_EXAMPLES, MIXED_INSTANCES, SHEXC

CODE = 'shexer-memory'

from .shexer import meat as _meat

import memray
import subprocess

def meat(key : Key) :
    memory_graph = f'{RESULTS}/{CODE}/{key}.bin'
    with memray.Tracker(memory_graph) :
        _meat(key)

from memray import FileReader

from ..report import report_add

def post(key : Key) :
    memory_graph = f'{RESULTS}/{CODE}/{key}.bin'
    memory_graph_html = f'{RESULTS}/{CODE}/{key}.html'

    subprocess.run(["memray", "flamegraph", memory_graph, "-o", memory_graph_html])

    reader = FileReader(memory_graph)
    peak_bytes = max((s.heap for s in reader.get_memory_snapshots()), default=0)
    peak_mb = peak_bytes / (1024 * 1024)

    report_add('memory', 'shexer', key, str(peak_mb))

task = Task(
    description = "instance tracker+class profile shexer; all saved in json files",
    done = (lambda key : (RESULTS/Path(f"{CODE}/{key}.html")).is_file()),
    code = CODE,
    meat = meat,
    post = post
    )