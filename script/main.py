from string import Template
import os
import logging
import sys
import uuid

from rdflib import Namespace, RDF, term, Literal
from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2, JSON

logging.getLogger().setLevel(logging.INFO)
SH = Namespace("http://www.w3.org/ns/shacl#")


def generate_propertyshape_query(node_shape):
    """
    A query to select the different property shapes for a nodesshape and their properties
    """
    query_template = Template("""
PREFIX sh: <http://www.w3.org/ns/shacl#>

SELECT DISTINCT ?propertyShape ?path ?objectDatatype ?objectClass
WHERE {
  <$node_shape> a sh:NodeShape ;
    sh:property ?propertyShape .
  ?propertyShape sh:path ?path .
  OPTIONAL {
    ?propertyShape sh:datatype ?objectDatatype .
  }
  OPTIONAL {
    ?propertyShape sh:class ?objectClass .
  }
}
""")
    query_string = query_template.substitute(
        node_shape=node_shape
    )
    return query_string

def generate_count_property_query(data_graph, subject_class, path, object_class=None, property=None):
    """
    """
    query_template = Template("""
SELECT (MAX(?count) AS ?maxCount) (MIN(?count) AS ?minCount)
WHERE {
    {
        SELECT ?s (COUNT(?o) AS ?count)
        WHERE {
            GRAPH <$data_graph> {
                ?s a <$subject_class> .
    OPTIONAL {
                ?s <$path> ?o .
                $object_class_snippet }
            }
        }
        GROUP BY ?s
    }
}
""")
    query_string = query_template.substitute(
        data_graph=data_graph,
        subject_class=subject_class,
        object_class_snippet=f"?o a <{object_class}> ." if object_class else "",
        path=path
    )
    return query_string

def generate_nodeshape_query(void_description_graph, class_partition_uri_prefix):
    """
    A construct query that creates nodeshapes and property-shapes for each void class
    """
    query_template = Template("""
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX void-ext: <http://ldf.fi/void-ext#>
PREFIX sh: <http://www.w3.org/ns/shacl#>

CONSTRUCT {
  ?nodeShape a sh:NodeShape ;
  sh:targetClass ?subjectClass ;
  sh:property [
                sh:path ?prop ;
                sh:datatype ?objectDatatype ;
                sh:class ?objectClass ;
              ]
}
WHERE {
  GRAPH <$void_description_graph> {
    {
      {
        SELECT DISTINCT (?classPartition AS ?cp) ?nodeShape
        WHERE {
          GRAPH <$void_description_graph> {
            ?classPartition void:class ?subjectClass .
            BIND (URI(CONCAT("$class_partition_uri_prefix", STRUUID())) AS ?nodeShape)
          }
        }
      }
      ?cp void:class ?subjectClass ;
      void:entities ?subjectsCount ;
      void:propertyPartition ?pp .
      ?pp void:property ?prop .
      OPTIONAL {
        {
          ?pp  void:classPartition [ void:class ?objectClass ] .
        } UNION {
          ?pp void-ext:datatypePartition [ void-ext:datatype ?objectDatatype ] .
        }
      }
    } UNION {
      ?linkset void:subjectsTarget [ void:class ?subjectClass ] ;
      void:linkPredicate ?prop ;
      void:objectsTarget [ void:class ?objectClass ] .
    }
  }
}
""")
    query_string = query_template.substitute(
        void_description_graph=void_description_graph,
        class_partition_uri_prefix=class_partition_uri_prefix
    )
    return query_string

NODE_SHAPE_QUERY = """
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX sh: <http://www.w3.org/ns/shacl#>

SELECT DISTINCT ?nodeShape ?class
WHERE {
  ?nodeShape a sh:NodeShape ;
      sh:targetClass ?class .
}
"""

def minmax2constraints(mincount, maxcount):
    """
    Determine sh:minCount and sh:maxCount based on dataset min and max count,
    based on a few assumptions.
    """
    if mincount > 0:
        if mincount == maxcount:
            shacl_min_count = mincount
        else:
            shacl_min_count = 1
    else:
        shacl_min_count = None

    if maxcount == 1:
        shacl_max_count = 1
    else:
        shacl_max_count = None

    return shacl_min_count, shacl_max_count

def yield_node_shapes(graph):
    ns = graph.query(NODE_SHAPE_QUERY)
    for node_shape, target_class in ns:
        yield node_shape, target_class

def yield_property_shapes(graph, node_shape):
    q = generate_propertyshape_query(node_shape)
    ps = graph.query(q)
    for binding in ps.bindings:
        if term.Variable('objectClass') in binding:
            logging.debug(binding[term.Variable('objectClass')])
        elif term.Variable('objectDatatype') in binding:
            logging.debug(binding[term.Variable('objectDatatype')])
        if term.Variable('path') in binding:
            logging.debug(binding[term.Variable('path')])
        yield binding[term.Variable('propertyShape')], binding[term.Variable('path')], binding[term.Variable('objectClass')] if term.Variable('objectClass') in binding else None

if __name__ == '__main__':
    SPARQL_ENDPOINT = "http://localhost:8890/sparql" #  os.environ.get("SPARQL_ENDPOINT")
    DATASET_GRAPH = "http://example.com/graphs/rijksmuseum"
    DATASET_VOID_GRAPH = "http://example.com/graphs/void/rijksmuseum"
    CLASS_PARTITION_PREFIX = "http://example.com/class-partition/"

    sparql_query = SPARQLWrapper2(SPARQL_ENDPOINT)
    sparql_construct = SPARQLWrapper(SPARQL_ENDPOINT)

    nodeshape_qs = generate_nodeshape_query(DATASET_VOID_GRAPH, CLASS_PARTITION_PREFIX)
    sparql_construct.setQuery(nodeshape_qs)
    shacl_graph = sparql_construct.queryAndConvert()

    for node_shape, target_class in yield_node_shapes(shacl_graph):
        logging.info(f"Node shape {node_shape} with target class {target_class}")
        for property_shape, path, object_class in yield_property_shapes(shacl_graph, node_shape):
            q = generate_count_property_query(DATASET_GRAPH,
                                              target_class,
                                              path,
                                              object_class=object_class)
            sparql_query.setQuery(q)
            res = sparql_query.query()

            mincount = int(res.bindings[0]['minCount'].value)
            maxcount = int(res.bindings[0]['maxCount'].value)

            shacl_min_count, shacl_max_count = minmax2constraints(mincount, maxcount)

            if shacl_min_count:
                triple = property_shape, SH['minCount'], Literal(mincount)
                shacl_graph.add(triple)
            if shacl_max_count:
                triple = property_shape, SH['maxCount'], Literal(maxcount)
                shacl_graph.add(triple)

    shacl_graph.serialize(destination='shacl_description.ttl', format='turtle')
