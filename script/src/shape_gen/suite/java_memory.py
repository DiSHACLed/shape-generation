import bisect
from os import mkdir
from typing import Callable
from ..config import PLAY_JAR
# import shutil
# from ..virtuoso.cli import init, stop
from ..virtuoso.virtuoso import ENDPOINT
# from ..suite.report import report_add
from pathlib import Path
import subprocess

TEMP_DIR = '/tmp/java-memory'

def play(key : str, mem : int) :
    output_dir = Path(f"{TEMP_DIR}/play-{key}-{mem}mb")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / Path(f"{key}.ttl")

    # log_file = Path(f"{TEMP_DIR}/play-{mem}mb/{key}.log")

    command = ["java", "-jar", f"-Xmx{mem}m", str(PLAY_JAR), "generate", "--endpoint", ENDPOINT, "-o", str(output_file) ]

    try:
        # run the command, redirect stdout and stderr to log file
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            # stdout=log_file,
            # stderr=subprocess.STDOUT,  # merge stderr into stdout
            check=True,                 # raises CalledProcessError on failure
            text=True
        )
        output_file.unlink()
        succeeded = True
    except subprocess.CalledProcessError as e:
        succeeded = False
    
    # log_file.unlink()

    # shutil.rmtree(Path(f"{TEMP_DIR}/play-{mem}mb)")
    return succeeded

from ..config import QSE_DIR, INTERMEDIATE, JAVA_BIN
# QSE_JAR = QSE_DIR/Path('jar')/Path('qse.jar')
from .tasks import ntriples
import shutil

QSE_JAR : Path = QSE_DIR/Path('jar') / Path('qse.jar')

def qse(key : str, mem : int) :
    output_path = Path(f"{TEMP_DIR}/qse-{key}-{mem}mb")
    output_path.mkdir(parents=False, exist_ok=True)
    # log_file = Path(f"{TEMP_DIR}/play-{key}-{mem}mb/log")

    nt_file = Path(f'{INTERMEDIATE}/{ntriples.CODE}/{key}.nt')

    private = True # examples inflate..
    # private = key.startswith('lblod')

    config = f"""\
        # ---------------------------------- QSE Config -----------------------------
        qse_exact_file=true
        qse_exact_query_based=false
        qse_approximate_file=false
        qse_approximate_query_based=false
        qse_approximate_parallel_query_based=false
        qse_approximate_parallel_qb_threads=1

        # Please specify the list of classes in file available at //app/qse/config/pruning/classes.txt
        qse_specific_classes=falsemax_cardinality=true
        min_cardinality=true

        # ---------------------------------- Dataset Config -----------------------------
        dataset_name=DATASET
        expected_number_classes=15
        expected_number_of_lines=1000000
        is_wikidata=false
        # set true to add examples to shapes
        add_examples={'true' if not private else 'false'}
        # predicates used for labels (separated by ",")
        label_properties=<http://www.w3.org/2000/01/rdf-schema#label>,<http://www.w3.org/2004/02/skos/core#prefLabel>
        # IRI used for examples in shapes
        example_IRI=http://example.org/example

        # ---------------------------------- GraphDB Endpoint Config - For QSE (Query-based) -----------------------------
        graphdb_url=http://graphdb.srver.com:7200
        graphdb_repository=REPOSITORY


        # ---------------------------------- Sampling Parameters - For QSE Approximate -----------------------------
        entity_sampling_threshold=100
        entity_sampling_target_percentage=75


        # ---------------------------------- Validation -----------------------------
        qse_validation=false
        # extract shapes using shacl not for validation purpose
        qse_validation_with_shNot=false


        # ---------------------------------- Paths Config -----------------------------
        dataset_path={nt_file}
        # I think below does not matter
        resources_path={QSE_DIR}/src/main/resources
        # I think below does not matter
        config_dir_path={QSE_DIR}/config/
        output_file_path={str(output_path)}/
        default_directory={QSE_DIR}/Output/lubm/default/
        validation_input_dir={QSE_DIR}/validation/

        # annotate shapes with support and confidence
        annotateSupportConfidence=true

        # ---------------------------------- Pruning Thresholds (Support and Confidence) -----------------------------

        # 1st parameter is confidence and 2nd is support. So for more parameters, you can append the list with more pairs lie (0.25,150) etc. Please do not use spaces in this list.
        pruning_thresholds={{(0,0),(0.5,0),(0.9,0),(1,0)}}
        # pruning_thresholds={{(0,0),(0.1,20),(0.2,20),(0.3,20),(0.4,20),(0.5,20),(0.6,20),(0.7,20),(0.8,20),(0.9,20),(0.9,50),(0.95,50),(0.95,100),(0.95,200)}}
    """

    config_file = output_path / Path("config.properties")
    with open(config_file, "w") as f:
        f.write(config)   

    command = [JAVA_BIN, "-jar", f"-Xmx{mem}m", str(QSE_JAR), str(config_file)] # 

    try:
        # run the command, redirect stdout and stderr to log file
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            # stdout=log_file,
            # stderr=subprocess.STDOUT,  # merge stderr into stdout
            check=True,                 # raises CalledProcessError on failure
            text=True
        )
        succeeded = (output_path / Path('DATASET_QSE_0.0_0_SHACL.ttl')).exists()
        # shutil.rmtree(output_path)
        output_path.mkdir(exist_ok=True)
    except subprocess.CalledProcessError as e:
        succeeded = False
    
    # log_file.unlink()

    # shutil.rmtree(Path(f"{TEMP_DIR}/play-{mem}mb)")
    return succeeded

def derive_min_ram(
    execute: Callable[[str, int], bool],
    key : str,
    upper: int,
    granularity: int = 128,
) -> int:
    """
    Find the minimum RAM (in MB) for which `execute` returns True,
    using binary search over [0, upper] in steps of `granularity`.

    `execute` must be monotonic: False for values below the minimum,
    True for values at or above it.

    Args:
        execute:     Function that takes RAM in MB and returns bool.
        upper:       Upper bound (inclusive) in MB.
        granularity: Step size in MB. Use larger values for coarser
                     searches, e.g. granularity=100 to find the minimum
                     in ~0.1 GB increments (100 MB steps).

    Returns:
        The minimum value in [0, upper] (aligned to granularity)
        for which execute returns True.

    Raises:
        ValueError: If execute returns False for all values in range.
    """
    seq = range(0, upper + 1, granularity)

    def keyfunc(mem : int) -> bool:
        print(f"Trying {mem} MB")
        bl = execute(key, mem)
        if bl :
            print(f"Succeeded with {mem} MB")
        else : 
            print(f"Failed with {mem} MB")
        return bl

    idx = bisect.bisect_left(seq, True, key=keyfunc)

    if idx >= len(seq):
        raise ValueError(
            f"execute returned False for all values in [0, {upper}] "
            f"with granularity={granularity}"
        )

    result = seq[idx]
    print(f"Minimum RAM found: {result} MB")
    return result

