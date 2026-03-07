from ..task import Task, Key
from ...config import RESULTS, PLAY_JAR
# from rdf_tools.prelude import docker_connect
from pathlib import Path
import subprocess
from ...config import RESULTS
from ...virtuoso.cli import init, stop
from ...virtuoso.virtuoso import ENDPOINT

JAVA_HEAP_SIZE = 32

CODE = 'play'

def prep(key : Key) :
    try :
        stop() # just in case
    except :
        pass
    init(key)

def post(key : Key) :
    stop()

def meat(key : Key) :
    if not PLAY_JAR.is_file() :
        raise RuntimeError(f"{PLAY_JAR} does not exist")

    output_file = Path(f"{RESULTS}/{CODE}/{key}.ttl")
    log_file = Path(f"{RESULTS}/{CODE}/{key}.log")

    # TODO namespaces are supported
    command = ["java", "-jar", f"-Xmx{JAVA_HEAP_SIZE}g", str(PLAY_JAR), "generate", "--endpoint", ENDPOINT, "-o", str(output_file) ]

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
            raise RuntimeError(f"Command {command} failed with exit code {e.returncode}. See {log_file} for details.") from e

task = Task(
    description = "PLAY: generate SHACL from endpoint ",
    code = CODE,
    done = (lambda key : (RESULTS/Path(f"{CODE}/{key}.ttl")).is_file()),
    meat = meat,
    prep = prep,
    post = post,
    )