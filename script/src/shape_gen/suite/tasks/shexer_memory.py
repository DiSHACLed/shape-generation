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

import memray
import subprocess

CODE = 'shexer-memory'

def _meat(key : Key) :
    input_file = Path(f'{SAMPLE_DATA}/{key}.ttl')
    output_file = Path(f'{RESULTS}/{CODE}/{key}.shex')
    log_file = Path(f'{RESULTS}/{CODE}/{key}.log')
    threshold = 0

    private = True
    # private = key.startswith('lblod')

    shaper = Shaper(
        all_classes_mode = True,
        graph_file_input = str(input_file),
        # graph_list_of_files_input= input,
        input_format=TURTLE_ITER,
        examples_mode=(ALL_EXAMPLES if not private else None),
        # remove_empty_shapes=False,
        inverse_paths=True,
        namespaces_dict={ abrev : url for (url, abrev) in NAMESPACES.items() },
        instances_report_mode=MIXED_INSTANCES,
    )

    with open(log_file, "w") as f:
        with redirect_stdout(f), redirect_stderr(f):
            # raise Error("asdf")
            # print('hmmmm')
            shaper.shex_graph(
                output_file=str(output_file),
                output_format=SHEXC,
                # output_format=SHACL_TURTLE,
                acceptance_threshold=threshold,
                verbose=True,
                # rdfconfig_directory = f'{RESULTS}/{CODE}/{key}/'
                )

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