from string import Template
import logging
from typing import Optional, Generator, Literal as Lit, cast
from pathlib import Path
from datetime import datetime

from ..virtuoso.virtuoso import ENDPOINT

from ..config import NAMESPACES

from .heuristics import minmax2constraints
from .interaction import prompt_y_n

from rdflib import Namespace, term, Literal, URIRef, Node, Graph, Dataset, IdentifiedNode
from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2

from importlib import resources

logging.getLogger().setLevel(logging.INFO)

def log(msg : str, channel : Lit["info"] | Lit["debug"] = "info"):
    msg = f"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} -- {msg}"
    match channel :
        case "info" :
            print(msg)
        case "debug" :
            pass
            # logging.debug(msg)

Templates = Lit["construct_node_shapes"] | Lit["property_shape"] | Lit["count_property"] | Lit["bare_shacl"]

# working with templates as f-strings are complicated with {}'s abundant in sparql
def load_template(template : Templates, subs : dict[str,str]) -> str :
    """Load sparql template with the required list of substitutions."""
    # with open(f"{SCRIPT_DIR}/templates/{template}.sparql", "r") as f:
    with resources.files("shape_gen.voicl.templates").joinpath(f"{template}.sparql").open("r") as f:
        content = f.read()
        query_template = Template(content)
        return query_template.substitute(subs)

def property_shape_query(node_shape : URIRef):
    """
    A query to select the different property shapes for a nodesshape and their properties
    """
    return load_template("property_shape", { 'node_shape' : node_shape })

# TODO technically; subject types could be blank nodes?
# TODO technically; objects could be blank nodes?
def count_property_query(data_graph : str, subject_type : URIRef, path : URIRef, object_type : Optional[URIRef], object_datatype : Optional[URIRef]):
    """
    for each subject type get every instance; for each instance; get the count... return min and max found
    """
    # TODO datatype 
    return load_template("count_property", 
        { 'data_graph': data_graph, 
          'path': path,
          'subject_type' : subject_type, 
          'object_type_snippet' : f"?o a <{object_type}> ." if object_type else "",
          'object_datatype_snippet' : f"FILTER(DATATYPE(?o) = {object_datatype})." if object_datatype else ""
        })

def bare_shacl_query(void_graph : str, shapes_prefix : str):
    """
    A construct query that creates nodeshapes and property-shapes for each void class
    """
    return load_template("bare_shacl",
            { 'void_graph': void_graph,
              'shapes_prefix': shapes_prefix }
            )


NODE_SHAPE_QUERY = """
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX sh: <http://www.w3.org/ns/shacl#>

SELECT DISTINCT ?nodeShape ?class
WHERE {
  ?nodeShape a sh:NodeShape ;
      sh:targetClass ?class .
}
"""

def node_shapes(graph : Graph) -> Generator[tuple[URIRef, URIRef]] :
    """Immediately start working with resutls"""
    ns = graph.query(NODE_SHAPE_QUERY)
    # TODO; technically classes could be blank nodes?
    ns = cast(Generator[tuple[URIRef,URIRef]], ns) # we are selecting subjects and objects

    for node_shape, target_class in ns:
        yield node_shape, target_class

# TODO technically; object types could be blank nodes?
def property_shapes(graph : Graph, node_shape : URIRef) -> Generator[tuple[URIRef,URIRef,Optional[URIRef],Optional[URIRef]]]: 
    qr = property_shape_query(node_shape)
    ps = graph.query(qr)
    for binding in ps.bindings:
        if term.Variable('objectClass') in binding:
            logging.debug(binding[term.Variable('objectClass')])
        elif term.Variable('objectDatatype') in binding:
            logging.debug(binding[term.Variable('objectDatatype')])
        if term.Variable('path') in binding:
            logging.debug(binding[term.Variable('path')])
        yield ( 
            binding[term.Variable('propertyShape')], 
            binding[term.Variable('path')], 
            binding[term.Variable('objectClass')] if term.Variable('objectClass') in binding else None,
            binding[term.Variable('objectDatatype')] if term.Variable('objectDataType') in binding else None 
            )

SH = Namespace("http://www.w3.org/ns/shacl#")

def add_prefixes(graph : Graph) :
    for (prefix, full) in NAMESPACES.items() :
        graph.bind(prefix, full)

from ..prelude import Typer

from pathlib import Path
voicl_typer = Typer()


@voicl_typer.command(name='generate')
def generator(
        data_graph : str, 
        data_endpoint : str,
        output : Path,
        shapes_prefix : str = "http://example.com/shapes/",
        void_graph : Optional[str] = None, 
        void_endpoint : Optional[str] = None,
        void_file : Optional[Path] = None, 
        interactive : bool = False
        ):
    """
    Generates output.ttl with shacl shape given a sparql endpoint with graph and void graph.
    """
    log("Generating bare shacl structure")
    if void_file is not None and void_endpoint is None and void_graph is None :
        dummy_void = URIRef('http://dummy.com/void')
        void = Dataset()
        void.graph(dummy_void).parse(void_file, format="turtle")
        shacl_graph = void.query(bare_shacl_query(dummy_void, shapes_prefix)).graph
        if shacl_graph is None :
            raise RuntimeError("could not generate bare shacl graph")
    elif void_graph is not None and void_endpoint is not None and void_file is None :
        void = SPARQLWrapper(void_endpoint)
        void.setQuery(bare_shacl_query(void_graph, shapes_prefix))
        shacl_graph = void.queryAndConvert()
        shacl_graph = cast(Graph, shacl_graph)
    else :
        raise RuntimeError('either --void-file or --void-endpoint and --void-graph')
    log("Bare shacl structure done")

    # TODO replace with sparqlstore
    data_sparql = SPARQLWrapper2(data_endpoint)

    log("Adding counts")
    log("-------------")
    for node_shape, target_class in node_shapes(shacl_graph):
        log(f"{node_shape} ~ {target_class}")

        for property_shape, path, object_class, object_datatype in property_shapes(shacl_graph, node_shape):
            # TODO if a path ranges over multiple types/datatypes, they must be stored in different void partitions (otherwise below won't make sense)
            log(f"\t{property_shape} | {path} > {object_class if object_class is not None else 
                                                    (object_datatype if object_datatype is not None else "[no object/datatype]")}")

            q = count_property_query(data_graph,
                                     target_class,
                                     path,
                                     object_class,
                                     object_datatype,
                                     )
            log(q,"debug")
            data_sparql.setQuery(q)
            res = data_sparql.query()

            mincount = int(res.bindings[0]['minCount'].value)
            log(f"\t\t min: {mincount} (min found at subject)")
            maxcount = int(res.bindings[0]['maxCount'].value)
            log(f"\t\t max: {maxcount} (max found at subject)")

            shacl_min_count, shacl_max_count = minmax2constraints(mincount, maxcount)

            if shacl_min_count:
                triple = property_shape, SH['minCount'], Literal(mincount)
                log(f"\t\t shacl-min: {shacl_min_count}")
                if not interactive or prompt_y_n(f"Add sh:minCount {shacl_min_count} for <{path}>?"):
                    shacl_graph.add(triple)
            if shacl_max_count:
                triple = property_shape, SH['maxCount'], Literal(maxcount)
                log(f"\t\t shacl-max: {shacl_max_count}")
                if not interactive or prompt_y_n(f"Add sh:maxCount {shacl_max_count} for <{path}>?"):
                    shacl_graph.add(triple)
    
    add_prefixes(shacl_graph)

    shacl_graph.serialize(destination=output, format='turtle')

from ..prelude import graph_name

@voicl_typer.command()
def validate():
    generator(graph_name('mandaten-fix'),
        ENDPOINT,
        Path('/home/koen/shacl.ttl'),
        void_file = Path('/home/koen/shape-generation-clean/generated-output/void/mandaten-fix.ttl'), 
        interactive = False
        )
