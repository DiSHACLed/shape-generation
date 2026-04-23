See the time tab in the [generated excel file](./generated_output/report.xlsx).

Everything is measured in *seconds*.

Description of tasks (`suite info` with some additional comments);
- `ntriples`
  generate nt file from ttl (needed for qse)
- `qse`
  generate SHACL from nt (depends on ntriples)
- `shexer`
  generate shex from turtle
- `shexer-profile`
  generates base profile from which shex/shacl can easily be generated using distinct settings
- `shexer-bunch`
  generates SHACL's/shex's from generated profile (using different settings)
- `virtuoso`
  sets up virtuoso SPARQL endpoint and uses dba to load ttl (time measurment is only about the loading of ttl file)
- `void`
  description: generate void from SPARQL endpoint
- `play`
  description: generate SHACL from virtuoso endpoint
- `voicl`
  generate SHACL from endpoint and void file (depends on void)

Some notes;
- `qse` task takes .nt files only (`ntriples` task converts ttl's to nt's)

# some notes

- Config parameters of `shexer` do not change execution time; we have a first phase (simulated with `shexer-profile`) after which a bunch of different shapes can be generated with different config parameters (`shexer-bunch`).

- With `play`, `void`, & `voicl` the main load (also wrt memory) is on the SPARQL endpoint. 