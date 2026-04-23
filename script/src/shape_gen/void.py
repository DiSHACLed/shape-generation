from .prelude import CLIENT, Typer
from .config import VIRTUOSO_DIR
import re
import shutil
from pathlib import Path

void_typer = Typer()

@void_typer.command()
# TODO cli with --iri-of-void
def generate(endpoint : str, graph : str, key : str, output : Path) -> None :
    """generates data/{key}-void.tll of graph in sparql endpoint"""
    container_void = CLIENT.containers.run(
        image = 'redpencil/void-generator-docker',
        name = 'void-gen',
        volumes={
            f"{VIRTUOSO_DIR}/.voids": {"bind": "/output/", "mode": "rw"}
            },
        network='host',
        command = [
            "java", "-jar", "void-generator.jar",
            "-r", endpoint,
            "--void-file", f"/output/{key}-void.ttl",
            "--iri-of-void", f"http://example.com/void-description/{key}",
            "-g", graph
        ],
        remove=True,
        detach=True,
    )
    # TODO iri-of-void argument

    READY_PATTERN = re.compile(r"swiss.sib.swissprot.servicedescription.Generate - Ran", re.IGNORECASE)

    for raw in container_void.logs(stream=True, follow=True):
        line = raw.decode("utf-8", errors="replace")
        print(f'void-docker $ {line}')

        if READY_PATTERN.search(line):
            # print(f"\npython $ void file has been generated and copied to data/")

            shutil.copy(f"{VIRTUOSO_DIR}/.voids/{key}-void.ttl", 
                        output)
            print(f'Void file generated and stored in {output}')
            return # f"{DATA_DIR}/{key}-void.ttl"

    raise AssertionError("This branch will only be reached of container stops")

@void_typer.command()
def validate() :
    pass