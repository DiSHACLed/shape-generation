from contextlib import redirect_stdout
from ..task import Task, Key
from ...config import RESULTS, SAMPLE_DATA, NAMESPACES
from pathlib import Path

# import logging
from contextlib import redirect_stdout, redirect_stderr

from shexer.shaper import Shaper
from shexer.consts import TURTLE_ITER, SHACL_TURTLE, ALL_EXAMPLES, MIXED_INSTANCES, SHEXC

CODE = 'shexer'

def meat(key : Key) :
    input_file = Path(f'{SAMPLE_DATA}/{key}.ttl')
    output_file = Path(f'{RESULTS}/{CODE}/{key}.ttl')
    log_file = Path(f'{RESULTS}/{CODE}/{key}.log')
    threshold = 0

    shaper = Shaper(
        all_classes_mode = True,
        graph_file_input = str(input_file),
        # graph_list_of_files_input= input,
        input_format=TURTLE_ITER,
        examples_mode=ALL_EXAMPLES,
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
                # to_uml_path=uml_output
                )

task = Task(
    description = "generate SHACL from ttl",
    done = (lambda key : (RESULTS/Path(f"{CODE}/{key}.ttl")).is_file()),
    code = CODE,
    meat = meat
    )
