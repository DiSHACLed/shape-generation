# Shape generation

This repository contains the work in progress for *WP 1 Data Discovery - assisted shape construction*, as part of the DiSHACLed project.


## Process 

For now we assume a triplestore & SPARQL-based setup. LDES-streams can be ingested into a triplestore by existing components such as the [RDF-connect LDES-client](https://github.com/rdf-connect/ldes-client).

### VoID intermediary approach

The literature on automated SHACL shape generation we studied[[1]](https://drive.google.com/file/d/1xQwWoM1ktWHWts4-k4_li1JCr8SPgpGe/view?usp=drive_link) often advises against (or ignores) the use of a raw dataset as the source for automated shape generation for performance reasons. Instead it suggests approaches based on OWL definitions, RML mapping configs, etc.  
These resources however aren't guaranteed to be available for all of the datasets we'd like to analyse. Therefore we require an approach that is reasonably performant, but can handle larger raw datasets as a source for the analysis anyway. 
Since the [VoID](https://www.w3.org/TR/void/) vocabulary [structural metadata](https://www.w3.org/TR/void/#structural)-properties cover many of the performance-critical aggregations that are required for the basic SHACL properties, and mature tooling for VoID-analysis is readily available, we propose to use a VoID analysis of the to-be-described dataset as a starting point for SHACL shape generation based on raw datasets. 

### Steps

- Load dataset into triplestore
- Make VoID structural metadata analysis of the dataset. See https://github.com/redpencilio/void-generator-docker for a Dockerized version of J. Bolleman's VoID description generator.
```
docker run --network=host -it redpencil/void-generator-docker java -jar void-generator.jar -r http://localhost:8890/sparql --void-file void-rijksmuseum.ttl --iri-of-void 'https://example.com/.well-known/void#' -g http://mu.semte.ch/graphs/rijksmuseum
```
- Load produced VoID description into triplestore
- Run script to generate SHACL description

## parts of SHACL spec in scope

Up for debate. A `sh:targetClass` `sh:NodeShape` with `sh:property` `sh:path`s probably are the bare minimum.  
Current example result snippet:
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

## Datasets in scope

- Flanders' Mandatendatabank, available at https://mandaten.lokaalbestuur.vlaanderen.be/
- Rijksmuseum Amsterdam's heritage collection, available at https://data.rijksmuseum.nl/docs/data-dumps/ as suggested in https://github.com/DiSHACLed/shape-generation/issues/1
- VLIZ' MarineRegions dataset, obtained by syncing their LDES feed at https://www.marineregions.org/feed
- TODO: Riooloverstorten Aquafin, not in production just yet. Snippet available at https://informatievlaanderen.github.io/OSLO-mapping/water/Aquafin%20-%20Overstort%20In%20Vlaanderen/0_4_examples_overstort
