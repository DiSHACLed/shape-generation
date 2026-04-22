from ..task import Task, Key
from ...config import SAMPLE_DATA, RESULTS, INTERMEDIATE
from ...prelude import docker_connect
from . import qse

from pathlib import Path

CODE = 'ntriples'

def meat(key : Key) :
    client = docker_connect(time_out=60*60)

    result_path = Path(f"{INTERMEDIATE}/{CODE}/")
    result_path.mkdir(parents=False, exist_ok=True)

    log_path = Path(f"{RESULTS}/{CODE}/")
    log_path.mkdir(parents=False, exist_ok=True)
    print(log_path)

    try :
        container = client.containers.run(
                        image = 'stain/jena',
                        name = f'jena-{key}-to-nt',
                        volumes={
                            str(SAMPLE_DATA) : {"bind": "/rdf/", "mode": "ro"}
                            },
                        command = [
                            "riot", "--output=ntriples", "--strict", f"{key}.ttl"
                            ],
                        remove=True,
                        detach=True,
                        stdout=True,
                        stderr=True, # TODO false? to raise error in python
                    )
        with open(f"{INTERMEDIATE}/{CODE}/{key}.nt", 'wb') as f :
            for chunk in container.logs(stream=True):
                f.write(chunk)
    except Exception as e :
        with open(f"{RESULTS}/{CODE}/{key}.error", 'w') as f :
            f.write(str(e))

task = Task(
    description = f"generate nt file from ttl (needed for qse)",
    done = (lambda key : (INTERMEDIATE/Path(f"{CODE}/{key}.nt")).exists()),
    code = CODE,
    meat = meat
    )