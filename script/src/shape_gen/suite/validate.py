from ..config import RESULTS, PLAY_JAR, SAMPLE_DATA
from pathlib import Path
import subprocess
from rdflib import Graph

JAVA_HEAP_SIZE = 32

CODE = 'play'

CLOSE_SHAPES_QUERY = """
PREFIX sh:   <http://www.w3.org/ns/shacl#>
PREFIX rdf:	<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

CONSTRUCT {
	?nodeShape sh:closed true .
	?nodeShape sh:ignoredProperties (rdf:type) .	
} WHERE {
	{
	SELECT DISTINCT ?nodeShape
	WHERE
	{
		{
			{
				?nodeShape a sh:NodeShape .
			}
			UNION
			{
				?nodeShape sh:targetClass|sh:targetNode|sh:targetObjectsOf|sh:targetSubjectsOf ?anything .
			}
		}
		FILTER NOT EXISTS {
			?nodeShape sh:closed true . 
		}
	}
	}
}
"""

import tempfile

def validate(input_file : Path, shacl_path : Path, closed : bool, overwrite : bool = False) -> int :

    report_html_path = shacl_path.parent / Path(f"{shacl_path.stem}.report.{"closed" if closed else "open"}.html")
    report_csv_path = shacl_path.parent / Path(f"{shacl_path.stem}.report.{"closed" if closed else "open"}.csv")
    log_report_path = shacl_path.parent / Path(f"{shacl_path.stem}.report.{"closed" if closed else "open"}.log")

    old_log = shacl_path.parent / Path(f"{shacl_path.stem}.report.log")
    if old_log.exists() :
        old_log.unlink()
    old_html = shacl_path.parent / Path(f"{shacl_path.stem}.report.html")
    if old_html.exists() :
        old_html.unlink()

    if closed :
        shapes = Graph()
        shapes.parse(shacl_path)
        closing_triples = shapes.query(CLOSE_SHAPES_QUERY).graph
        shapes += closing_triples
        with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False, mode="wb") as f:
            tmp_path = Path(f.name)

        shapes.serialize(destination=tmp_path, format="turtle")
        print(tmp_path)
        shacl_path = tmp_path

    command = ["java", "-jar", f"-Xmx{JAVA_HEAP_SIZE}g", str(PLAY_JAR), "validate", "-i", str(input_file), "-o", str(report_html_path), "-o", str(report_csv_path), "-s", str(shacl_path) ]

    # docker run --volume ./:/rdf stain/jena shacl validate --shapes shacl-for-shacl.ttl --data shacl.ttl --text

    if not report_html_path.exists() or overwrite :
        with open(log_report_path, "w") as log_file:
            try:
                subprocess.run(
                    command,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,  # merge stderr into stdout
                    check=True,                 # raises CalledProcessError on failure
                    text=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Command {command} failed with exit code {e.returncode}. See {log_file} for details.") from e

    with open(report_csv_path, "r") as f:
        line_count = sum(1 for _ in f)

    return (line_count - 1)

from .report import report_add

def generic_vals(CODE : str, key : str, overwrite : bool) :
    input_file = Path(f'{SAMPLE_DATA}/{key}.ttl')
    shacl_path = Path(f"{RESULTS}/{CODE}/{key}.ttl")

    if shacl_path.exists():
        (a , b) = (validate(input_file, shacl_path, bl, overwrite) for bl in [False, True])
        report_add('violations', CODE, key, f'{a} / {b}')
