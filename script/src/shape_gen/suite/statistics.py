from pathlib import Path
from rdflib import Graph
import json
from typing import Tuple
from ..config import RESULTS
# from .report import report_add

def statistics(shacl_path : Path) -> Tuple[int,int] :
    """opens shacl file with rdflib and write some base statistics to a json file; 1. amount of nodeshapes, 2. amount of propertyshapes """

    stats_file = shacl_path.parent / Path(f"{shacl_path.stem}.json")

    # if not stats_file.exists() or overwrite :
    g = Graph()
    g.parse(shacl_path, format="turtle")

    node_shapes = g.query("""
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        SELECT (COUNT(?s) AS ?count) WHERE { ?s a sh:NodeShape }
    """)
    property_shapes = g.query("""
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        SELECT (COUNT(?s) AS ?count) WHERE { ?s sh:path ?p }
    """)
        # SELECT (COUNT(?s) AS ?count) WHERE { ?s a sh:PropertyShape }

    node_shapes = int(next(iter(node_shapes))[0])
    property_shapes = int(next(iter(property_shapes))[0])

    stats = {
        "node_shapes": node_shapes,
        "property_shapes": property_shapes
    }
   
    with open(stats_file, "w") as log_file:
        json.dump(stats, log_file, indent=2)
    
    return(node_shapes, property_shapes)
    
from .report import report_add

def generic_stats(CODE : str, key : str) :
    output_file = Path(f"{RESULTS}/{CODE}/{key}.ttl")
    if output_file.exists():
        (a, b) = statistics(output_file)
        report_add('info', CODE, key, f'{a} / {b}')
