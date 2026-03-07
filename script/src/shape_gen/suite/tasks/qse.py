from ..task import Task, Key
from ...config import RESULTS, QSE_DIR
from pathlib import Path
import subprocess

from . import ntriples

CODE = 'qse'

QSE_JAR = QSE_DIR/Path('jar')/Path('qse.jar')

def meat(key : Key) :
    if not QSE_DIR.exists() :
        raise RuntimeError(f"{QSE_DIR} does not exist")

    if not QSE_JAR.is_file() :
        raise RuntimeError(f"{QSE_JAR} does not exist")

    nt_file = Path(f'{RESULTS}/{ntriples.CODE}/{key}.nt')
    if not nt_file.is_file() :
        raise RuntimeError(f"{RESULTS}/{ntriples.CODE}/{key}.nt does not exist")

    output_path = Path(f"{RESULTS}/{CODE}/{key}/")
    output_path.mkdir(parents=False, exist_ok=True)

    log_file = Path(f"{RESULTS}/{CODE}/{key}.log")

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
        add_examples=true
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
        pruning_thresholds={{(0,0),(0.1,100),(0.9,100)}}
    """

    config_file = Path(f"{RESULTS}/{CODE}/{key}/config.properties")
    with open(config_file, "w") as f:
        f.write(config)   

    command = ["java", "-jar", "-Xmx50g", str(QSE_JAR), str(config_file)] # 

    with open(log_file, "w") as log_file:
        try:
            # run the command, redirect stdout and stderr to log file
            subprocess.run(
                command,
                stdout=log_file,
                stderr=subprocess.STDOUT,  # merge stderr into stdout
                check=True,                 # raises CalledProcessError on failure
                text=True
            )
            print("Command succeeded, output written to log.")
        except subprocess.CalledProcessError as e:
            # You can add more info if you want
            raise RuntimeError(f"Command {command} failed with exit code {e.returncode}. See {log_file} for details.") from e

task = Task(
    description = f"generate SHACL from nt (depends on {ntriples.CODE})",
    done = (lambda key : (RESULTS/Path(f"{CODE}/{key}/DATASET_QSE_FULL_SHACL.ttl")).is_file()),
    code = CODE,
    meat = meat
    )


