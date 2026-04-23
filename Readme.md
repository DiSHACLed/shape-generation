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

Discription of can be found [here](./samples-input/descriptions.md)

# Findings

Findings are split up in different files;

- [qualitative musings](./report/qualitative.md)
- more quantitative results (see also the [generated excel file](./generated_output/report.xlsx))
  + [execution time](./report/time.md)
  + [memory usage](./report/memory.md)
  + [stats](./report/stats.md) 
  + [soundness](./report/soundness.md)
  + [precision](./report/precision.md)

# References

[1]: Extracting shapes from large RDF data collections - Fernández-Álvarez ...

[2]: Link; https://drive.google.com/file/d/1xQwWoM1ktWHWts4-k4_li1JCr8SPgpGe/view?usp=drive_link

[3]: Extraction of Validating Shapes from very large Knowledge Graphs - Rabbani...

[4]: Automatic Extraction of Shapes Using sheXer - Fernández-Álvarez ...