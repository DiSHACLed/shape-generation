from string import Template
import logging
from typing import Optional, Generator, Literal as Lit, cast
from pathlib import Path

from .heuristics import minmax2constraints
from .interaction import prompt_y_n

from rdflib import Namespace, term, Literal, URIRef, Node, Graph

from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2

from importlib import resources

logging.getLogger().setLevel(logging.INFO)

Templates = Lit["construct_node_shapes"] | Lit["property_shape"] | Lit["count_property"] | Lit["bare_shacl"]

# working with templates as f-strings are complicated with {}'s abundant in sparql
def load_template(template : Templates, subs : dict[str,str]) -> str :
    """Load sparql template with the required list of substitutions."""
    # with open(f"{SCRIPT_DIR}/templates/{template}.sparql", "r") as f:
    with resources.files("rdf_tools.templates").joinpath(f"{template}.sparql").open("r") as f:
        content = f.read()
        query_template = Template(content)
        return query_template.substitute(subs)

def property_shape_query(node_shape : str):
    """
    A query to select the different property shapes for a nodesshape and their properties
    """
    return load_template("property_shape", { 'node_shape' : node_shape })

# TODO property argument?
def count_property_query(data_graph : str, subject_type : str, path : str, object_type : Optional[str] = None , property : Optional[str] = None):
    """
    """
    return load_template("count_property", 
        { 'data_graph': data_graph, 
          'path': path,
          'subject_type' : subject_type, 
          'object_type_snippet' : f"?o a <{object_type}> ." if object_type else "" })

# def construct_node_shapes_query(void_graph : str, class_partition_uri_prefix : str):
#     """
#     A construct query that creates nodeshapes and property-shapes for each void class
#     """
#     return load_template("construct_node_shapes",
#             { 'void_graph': void_graph, 
#               'class_partition_uri_prefix': class_partition_uri_prefix })

def bare_shacl_query(void_graph : str, class_partition_uri_prefix : str):
    """
    A construct query that creates nodeshapes and property-shapes for each void class
    """
    return load_template("bare_shacl",
            { 'void_graph': void_graph })


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

    ns = cast(Generator[tuple[URIRef,URIRef]], ns) # we are selecting subjects and objects

    for node_shape, target_class in ns:
        yield node_shape, target_class

def property_shapes(graph : Graph, node_shape) -> Generator[tuple[Node,Node,Node]]: 
    qr = property_shape_query(node_shape)
    ps = graph.query(qr)
    for binding in ps.bindings:
        if term.Variable('objectClass') in binding:
            logging.debug(binding[term.Variable('objectClass')])
        elif term.Variable('objectDatatype') in binding:
            logging.debug(binding[term.Variable('objectDatatype')])
        if term.Variable('path') in binding:
            logging.debug(binding[term.Variable('path')])
        yield ( binding[term.Variable('propertyShape')], 
                binding[term.Variable('path')], 
                binding[term.Variable('objectClass')] if term.Variable('objectClass') in binding else None )

SH = Namespace("http://www.w3.org/ns/shacl#")

# TODO in separate file ...
namespaces = ( 
    ('sh', 'http://www.w3.org/ns/shacl#'),
    ('vl_besl', 'http://data.vlaanderen.be/ns/besluit#'),
    ('vl_mand', 'http://data.vlaanderen.be/ns/mandaat#'),
    ('vl_pers', 'http://data.vlaanderen.be/ns/persoon#'),

    ('example', 'http://example.com/'),
    ('mu_core', 'http://mu.semte.ch/vocabularies/core/'),

    ('mu_ext', 'http://mu.semte.ch/vocabularies/ext/'),
    ('lblod_org', 'http://lblod.data.gift/vocabularies/organisatie/'),
    ('lblod_ere', 'http://data.lblod.info/vocabularies/erediensten/'),
    )

def add_prefixes(graph : Graph) :
    for (prefix, full) in namespaces :
        graph.bind(prefix, full)

from ..prelude import Typer

from pathlib import Path
voicl_typer = Typer()

# TODO have void be a graph or just a file
# TODO same for data-graph

@voicl_typer.command(name='generate')
def generator(
        data_graph : str, 
        void_graph : str, 
        output : Path,
        data_endpoint : str,
        void_endpoint : str,
        class_partition_prefix : str = "http://example.com/class-partition/",
        interactive : bool = False
        ):
    """
    Generates output.ttl with shacl shape given a sparql endpoint with graph and void graph.
    """

    # TODO replace with sparqlstore
    void_sparql = SPARQLWrapper(void_endpoint)
    data_sparql = SPARQLWrapper2(data_endpoint)
    
    # init shacl graph; node shapes and property shapes for each void class
    void_sparql.setQuery(bare_shacl_query(void_graph, class_partition_prefix))
    # void_sparql.setQuery(construct_node_shapes_query(void_graph, class_partition_prefix))
    shacl_graph = void_sparql.queryAndConvert()

    shacl_graph = cast(Graph, shacl_graph)

    for node_shape, target_class in node_shapes(shacl_graph):
        logging.info(f"Node shape {node_shape} with target class {target_class}")

        for property_shape, path, object_class in property_shapes(shacl_graph, node_shape):
            # data_sparql.setQuery( )
            q = count_property_query(data_graph,
                                     str(target_class),
                                     str(path),
                                     object_type=str(object_class))
            logging.debug(q)
            data_sparql.setQuery(q)
            res = data_sparql.query()

            mincount = int(res.bindings[0]['minCount'].value)
            maxcount = int(res.bindings[0]['maxCount'].value)
            logging.info(f"<{path}>: min {mincount}, max {maxcount} occurences per subject.")

            shacl_min_count, shacl_max_count = minmax2constraints(mincount, maxcount)

            if shacl_min_count:
                triple = property_shape, SH['minCount'], Literal(mincount)
                logging.info(f"suggesting sh:minCount {shacl_min_count}")
                if not interactive or prompt_y_n(f"Add sh:minCount {shacl_min_count} for <{path}>?"):
                    shacl_graph.add(triple)
            if shacl_max_count:
                triple = property_shape, SH['maxCount'], Literal(maxcount)
                logging.info(f"suggesting sh:maxCount {shacl_max_count}")
                if not interactive or prompt_y_n(f"Add sh:maxCount {shacl_max_count} for <{path}>?"):
                    shacl_graph.add(triple)
    
    add_prefixes(shacl_graph)

    shacl_graph.serialize(destination=output, format='turtle')

    # print(bare_shacl_query(void_graph, class_partition_prefix))

@voicl_typer.command()
def validate():
    pass

