This repository contains the work in progress for *WP 1 Data Discovery - assisted shape construction*, as part of the DiSHACLed project.

# Prelude

Broadly speaking, we can classify two main strategies to the automatic generation of SHACL shapes [1];
- A-BOX based: looking at the "raw data" of your KG, i.e. the actual triples of your data
- T-BOX based: exploiting any other type meta-data that is available; ontologies, RML mapping... [2]

Due to performance concerns, some research advices against A-BOX based approaches, giving preference to T-BOX based strategies. [2]
Unfortunately, these strategies do not always apply as practically, we'll work with a bunch of databases where said resources (ontologies, RML setup,...) simply do not exist.
Fortunately, research on the T-BOX approach does exist, some of it with an explicit focus on performance. [1,3]
Moreover, a bunch of concrete tools have been published; 
in this repo, we'll document our understanding and practical experience with said tooling.

Tools we are looking at:
- [shexer](https://github.com/weso/shexer)
- [QSE](https://github.com/dkw-aau/qse/) / [shactor](https://github.com/dkw-aau/demo-shactor)
- [SHACL play](https://github.com/sparna-git/shacl-play)
- [voicl](scripts/...) (home-grown); starting from [void generator]((https://github.com/sib-swiss/void-generator))
- [SHACLgen](https://github.com/AKSW/shaclgen)
- [shape designer](https://gitlab.inria.fr/jdusart/shexjapp)

# Test suite

This repo contains of bunch python wrappers (see [here](./script/README.md)) to easily work with these different tools.
It also contains a [test suite](), that makes it easy to run a bunch of tools on new sample inputs.
The [generated-output](./generated-output/) directory hosts the output of these.

# Datasets in scope

- Flanders' Mandatendatabank, available at https://mandaten.lokaalbestuur.vlaanderen.be/
- Rijksmuseum Amsterdam's heritage collection, available at https://data.rijksmuseum.nl/docs/data-dumps/ as suggested in https://github.com/DiSHACLed/shape-generation/issues/1
- VLIZ' MarineRegions dataset, obtained by syncing their LDES feed at https://www.marineregions.org/feed
- TODO: Riooloverstorten Aquafin, not in production just yet. Snippet available at https://informatievlaanderen.github.io/OSLO-mapping/water/Aquafin%20-%20Overstort%20In%20Vlaanderen/0_4_examples_overstort
- ...

[TODO](./samples-input/summary.md)

# Practical considerations according to different approaches within A-BOX

We can divide A-BOX approaches into two distinct ways [3]:

## Query based

Information from graph is extracted through SPARQL queries
Some practical considerations according to the different contexts:

### remote/local endpoint 

Examples: 
- shexer with `url_endpoint`
- QSE with query mode (NOTE: as is, only supports GraphDB)
- SHACL-play generate with `-e` flag
- void-generator

Practical considerations;
- Strain on remote endpoint
- Config of endpoint; e.g. virtuoso: (void-generator)
  + Queries can time out; `MaxQueryExecutionTime`
    Kind of unavoidable really with large graphs.
  + Queries can be limit results (silently); `ResultSetMaxRows`
    Though (all?) tools handle this with multiple queries with increasing offsets
- Loading files in local endpoint can be time-intensive

  On virtuoso, check out `NumberOfBuffers` and `MaxDirtyBuffers`

### local file

Some tools can a file and try to load it completely in memory (with e.g. rdflib in python, or ... in java)

Examples:
- [[shacl-gen]] 
- [[SHACL-play]] with file input
- [[void-generator]] with file input

Practical consideration: Obviously, large graphs can eat up your memory.

## Non-query based:
Only two tools here
+ [[shexer]] (with file)
+ [[QSL]] (with file)

Both go over graph two times; collecting instances and classes in first pass, and constraints in second.

# Sampling

While [[shexer]] and [[QSL]] (in non-query mode) do not load graphs into memory, the intermediate structures to keep track of instances/classes/constraints are;
On very large graphs, this could still eat up your memory.
The [[QSL]] authors propose to solve this with a sampling version of there algorithm (seems pretty advanced). [3]
Similarly, [[shexer]] provides an `instances_cap`, though their authors propose an alternative solution to sampling by kind-off 'chop-them-up' approach [1] (not supported as is though).

- NOTE QSE (non-sampling) actually runs out of memory on LBLOD-large; but could just be a bug?

# Erroneous data / relevant structures

TODO; discuss relevance wrt dishacled

When automatically trying to extract shapes from an existing knowledge graph (that did not previously have a shape-s), there might be 'erroneous' data in there, deviating from the 'intended' structure of the graph.
E.g. 10 million instances of 'person' all of which have a birthdate of `xsd:date` but two who have `xsd:string`, it's clear that the latter two are faulty (and should be discarded when considering the property shape)
In [3] the refer to this as "spuriousness".

As such, instead of generating a shape graph for which the target graph is automatically valid (a "faithful" graph, say), we might want to generate a shape graph reflecting the "intended structure", invalidating exactly the erroneous triples in our (imperfect) data graph.

Moreover, there might be lots of instance classes/properties with only a handful of instances each, polluting the shapes file and distracting from the "important" shape files (e.g. marine-regions).

We can try deal with the above completely automatically:
- shexer provides `acceptance threshold` (between [0,1]) for relative cutoff for constraints (or constraint votes) (with acceptance threshold `t`, constraint evidenced less than `t x #instances` are ignored)
TODO `all_instances_are_compliant_mode`
- QSE provides `pruning_thresholds`; a relative and absolute cutoff (referred to as "confidence" and "support" in their paper)
This assumes that erroneous (and irrelevant) data is small when compared to valid data.
This is not always the case though; considering e.g. blood types, you would not want to discard AB negative as invalid.

Alternatively, we can sift through a collection of candidate shapes, inspecting the absolute and relative count of each constraint and making (semi)-manual decisions case by case.
- QSE `annotateSupportConfidence` annotates constraints with support and confidence; allows a list of different values as well (multiple files be created)
- shactor provides a UI to play with different values of constraint/confidence; and inspect what would be cutoff etc.. (even generates sparql queries to look at particular instances..)
- shexer does the same with `instances_report_mode`;generates such comments about all constraint votes (on SHEX files); most readible to find e.g. bugs in value
- shape designer has GUI but did not try; project seems quite abandoned

# Validity of generated shapes

We can readily test validity of a generated shape;
If shape was generated without pruning thresholds, validating data graph with shapes graph should validate all triples.
With thresholds, the invalid triples are (very informally) "within the scope of the thresholds set".

# Ouput

notes about output [notes about output](./notes_output.md)

# Completeness

In general, it is not clear to the "amount of detail" we want our shapes to reflect any given concrete knowledge graph; it will depend case by case.

# Scope of SHACL

Up for debate. Scope will probably depend on the data-base at hand.
In general, the bare minimum probably does include `sh:NodeShape`'s each with `sh:targetClass` and `sh:property`'s (each of which with a `sh:path`).
Current example result snippet (from voicl):
```ttl
ns1:Place
	rdf:type	ns2:NodeShape ;
	ns2:targetClass	ns3:Place ;
	ns2:property	[
                        ns2:path	skos:prefLabel ;
                        ns2:maxCount	6
                    ] , [
                        ns2:path	geo:long ;
                        ns2:maxCount	1 ;
                        ns2:datatype	xsd:string
                    ] , [
                        ns2:path	geo:lat ;
                        ns2:maxCount	1 ;
                        ns2:datatype	xsd:string
                    ] .
```

# Extensibility of tooling

How easy is it to extend X tool?
- Shexer: seems easy to add extra features (just add votes to)
- QSE: to investigate
- ...

# Maintained

Is tool X still maintained?

# Assumptions on input format

All approaches consider a file or SPARQL endpoint.

LDES-streams can be ingested into a triplestore by existing components such as the [RDF-connect LDES-client](https://github.com/rdf-connect/ldes-client), or simply sampled to a ttl file.

For streams, it most often makes sense to sample them anyway (probably).

# Assumptions on graph

All tools do rely on `rdf:type` predicate (or similar) being present in graph.

# References

[1]: Extracting shapes from large RDF data collections - Fernández-Álvarez ...

[2]: Link; https://drive.google.com/file/d/1xQwWoM1ktWHWts4-k4_li1JCr8SPgpGe/view?usp=drive_link

[3]: Extraction of Validating Shapes from very large Knowledge Graphs - Rabbani...

[4]: Automatic Extraction of Shapes Using sheXer - Fernández-Álvarez ...