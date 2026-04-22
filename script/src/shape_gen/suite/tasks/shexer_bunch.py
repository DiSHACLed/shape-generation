from contextlib import redirect_stdout
from typing import Literal
from ..task import Task, Key
from ...config import RESULTS, SAMPLE_DATA, NAMESPACES
from pathlib import Path
import json
from . import shexer_profile

# import logging
from contextlib import redirect_stdout, redirect_stderr

from shexer.shaper import Shaper
from shexer.consts import TURTLE_ITER, SHACL_TURTLE, ALL_EXAMPLES, MIXED_INSTANCES, SHEXC
from shexer.utils.structures.dicts import ShapeExampleFeaturesDict

CODE = 'shexer-bunch'

def meat(key : Key) :
    private = True #
    # private = key.startswith('lblod')

    input_dir = f'{RESULTS}/{shexer_profile.CODE}/{key}'
    
    if not Path(input_dir).exists() :
        raise RuntimeError(f"{input_dir} does not exist")

    output_dir = f'{RESULTS}/{CODE}/{key}/'
    Path(output_dir).mkdir(parents=False, exist_ok=True)

    log_file = Path(f'{RESULTS}/{CODE}/{key}.log')

    with open(f"{input_dir}/profile.json", "r") as f:
        profile = json.load(f)

    with open(f"{input_dir}/class_counts.json", "r") as f:
        class_counts = json.load(f)

    with open(f"{input_dir}/shape_names.json", "r") as f:
        shape_names = json.load(f)

    if not private :
        with open(f"{input_dir}/class_min_iris.json", "r") as f:
            class_min_iris_data = json.load(f)

    def shex_graph(compliant : bool, format : Literal[SHEXC] | Literal[SHACL_TURTLE], threshold : float) :
        shaper = Shaper(
            examples_mode=(ALL_EXAMPLES if not private else None),
            instances_report_mode=MIXED_INSTANCES,
            graph_file_input="dummy.ttl",
            namespaces_dict={ abrev : url for (url, abrev) in NAMESPACES.items() },
            all_classes_mode=True,
            input_format=TURTLE_ITER,
            all_instances_are_compliant_mode=compliant,
        )
        # shaper._check_correct_output_params = (lambda x, y : True)

        if not private :
            class_min_iris = ShapeExampleFeaturesDict(track_inverse_features=False)
            class_min_iris._base_dict = class_min_iris_data
            shaper._class_min_iris = class_min_iris

        shaper._profile = profile
        shaper._target_classes_dict = {}
        shaper._class_counts = class_counts
        shaper._shape_names = shape_names

        shaper.shex_graph(
            output_file=f"{output_dir}/{'shex' if format == SHEXC else 'shacl'}-{threshold}-{"compl" if compliant else "non_compl"}.{"ttl" if format == SHACL_TURTLE else "shex" }",
            output_format=format,
            verbose=True,
            acceptance_threshold=threshold,
        )

    for threshold in (0, 0.5, 0.9, 1):
    # for threshold in (0, 0.25, 0.5, 0.75, 1):
       for compliant in (False, True) :
            for format in [SHEXC, SHACL_TURTLE] :
                shex_graph(compliant,format,threshold)               

from ..report import report_add
from ..statistics import statistics as _stats

def stats(key : Key) :
    output_dir = f'{RESULTS}/{CODE}/{key}/'

    for threshold in (0, 0.5, 0.9, 1):
       for compliant in (False, True) :
            path = Path(f"{output_dir}/shacl-{threshold}-{"compl" if compliant else "non_compl"}.ttl")
            if path.exists():
                (a, b) = _stats(path)
                report_add('info', f'shexer-{'sound' if compliant else 'unsound'}-{threshold}', key, f'{a} / {b}')

from ..validate import validate as _validate

def validate(key : Key, overwrite : bool) :
    input_file = Path(f'{SAMPLE_DATA}/{key}.ttl')

    output_dir = f'{RESULTS}/{CODE}/{key}/'

    for threshold in (0, 0.5, 0.9, 1):
       for compliant in (False, True) :
            shacl_path = Path(f"{output_dir}/shacl-{threshold}-{"compl" if compliant else "non_compl"}.ttl")
            if shacl_path.exists():
                (a , b) = (_validate(input_file, shacl_path, bl, overwrite) for bl in [False, True])
                report_add('violations', f'shexer-{'sound' if compliant else 'unsound'}-{threshold}', key, f'{a} / {b}')

task = Task(
    description = "generate SHACL from previously generated profile (depends on shexer-profile)",
    done = (lambda key : (RESULTS/Path(f"{CODE}/{key}/shacl-0-compl.ttl")).is_file()),
    # post = post,
    code = CODE,
    meat = meat,
    stats = stats,
    validate = validate
    )
