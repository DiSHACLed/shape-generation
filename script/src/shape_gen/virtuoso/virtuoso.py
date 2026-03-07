from ..prelude import CLIENT
from ..config import VIRTUOSO_DIR

from pathlib import Path
import re
import shutil
import os

from docker.models.containers import Container

ENDPOINT = "http://localhost:8890/sparql"

from importlib import resources

def init(key : str, verbose : bool = False) -> Container :
    """initiate docker container with name virtuoso-{key} under folder ...; returns container"""
    # TODO check if port is free and contianer name...

    container : Container = CLIENT.containers.run(
        image="redpencil/virtuoso:1.3.0",
        name=f"virtuoso-{key}",
        environment={
        'SPARQL_UPDATE': "true",
        # 'DEFAULT_GRAPH': graph
        },
        volumes={
            # f"{DATA_DIR}/{key}.ttl": {"bind": f"/data/toLoad/{key}.ttl", "mode": "rw"},
            str(resources.files("rdf_tools.other").joinpath('virtuoso.ini')): {"bind": "/data/virtuoso.ini", "mode": "ro"},
            f"{VIRTUOSO_DIR}/{key}-db": {"bind": "/data", "mode": "rw"},
            },
        ports={"8890/tcp": 8890},
        labels={'loging': 'true'},
        remove=True,
        detach=True,
    )

    READY_PATTERN = re.compile(r"server online at", re.IGNORECASE)

    print(f"\npython $ waiting for sparql endpoint to be online")

    for raw in container.logs(stream=True, follow=True):
        line = raw.decode("utf-8", errors="replace")
        if verbose :
            print(f'docker $ {line}')

        if READY_PATTERN.search(line):
            break

    print('python $ sparql endpoint online ')
    return container

def load(container : Container, ttl_file : Path, target_graph : str, check_empty : bool = True) -> None :
    """loads ttl_file given container"""
    
    # TODO check whether has been loaded
    # TODO check amount of triples afterwards

    if not container.name:
        raise ValueError

    name_container : str = container.name

    assert name_container.startswith('virtuoso-')
    _, key = name_container.split('-', maxsplit=1)

    if check_empty :
        pass

    sql_commands = f"""
    ld_dir('manual', '*.ttl', '{target_graph}');
    rdf_loader_run();
    select * from DB.DBA.load_list;
    checkpoint;
    """
    # TODO instead of wildcard..

    os.makedirs(f'{VIRTUOSO_DIR}/{key}-db/manual', exist_ok=True) 

    with open(f'{VIRTUOSO_DIR}/{key}-db/manual/load-void.sql', "w") as f:
        f.write(sql_commands)

    # TODO just mount the thing?
    # TODO check not existing already
    shutil.copy(ttl_file, 
                f'{VIRTUOSO_DIR}/{key}-db/manual/')

    exit_code , result = container.exec_run(
        cmd=["isql-v", "1111", "dba", "dba", "/data/manual/load-void.sql"],
    )

    # TODO print to logfile
    # <<EOF   
    # SELECT ll_file, ll_state, ll_started, ll_done, ll_error
    # FROM DB.DBA.load_list
    # WHERE ll_file = 'manual/graph-dump-big.ttl';
    # EOF

    if exit_code == 0 :
        print(f"python $ triples loaded :)\n" )
        print(result)
        os.remove(f'{VIRTUOSO_DIR}/{key}-db/manual/load-void.sql')
        os.remove(f'{VIRTUOSO_DIR}/{key}-db/manual/{key}.ttl')
    else :
        raise RuntimeError('something went wrong :(')
