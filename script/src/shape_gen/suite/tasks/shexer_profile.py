from contextlib import redirect_stdout
from ..task import Task, Key
from ...config import RESULTS, SAMPLE_DATA, NAMESPACES
from pathlib import Path
import json

# import logging
from contextlib import redirect_stdout, redirect_stderr

from shexer.shaper import Shaper
from shexer.consts import TURTLE_ITER, SHACL_TURTLE, ALL_EXAMPLES, MIXED_INSTANCES, SHEXC

CODE = 'shexer-profile'

def meat(key : Key) :
    input_file = f'{SAMPLE_DATA}/{key}.ttl'
    
    output_path = f'{RESULTS}/{CODE}/{key}/'
    Path(output_path).mkdir(parents=False, exist_ok=True)

    log_file = Path(f'{RESULTS}/{CODE}/{key}.log')

    private = key.startswith('lblod')

    shaper = Shaper(
        all_classes_mode=True,
        examples_mode=(ALL_EXAMPLES if not private else None),
        instances_report_mode=MIXED_INSTANCES,
        graph_file_input=input_file,
        namespaces_dict={ abrev : url for (url, abrev) in NAMESPACES.items() },
        input_format=TURTLE_ITER,
    )

    shaper._check_correct_output_params = (lambda x, y : True)

    with open(log_file, "w") as f:
        with redirect_stdout(f), redirect_stderr(f):
            shaper.profile_graph(string_output=None, output_file=f"{output_path}/profile.json", verbose=True)

    with open(f"{output_path}/class_counts.json", "w") as out_stream:
        json.dump(shaper._class_counts, out_stream, indent=2)

    with open(f"{output_path}/shape_names.json", "w") as out_stream:
        json.dump(shaper._shape_names, out_stream, indent=2)

    if not private :
        with open(f"{output_path}/class_min_iris.json", "w") as out_stream:
            json.dump(shaper._class_min_iris._base_dict, out_stream, indent=2)

task = Task(
    description = "instance tracker+class profile shexer; all saved in json files",
    done = (lambda key : (RESULTS/Path(f"{CODE}/{key}/profile.json")).is_file()),
    code = CODE,
    meat = meat
    )
