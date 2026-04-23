# excel tab

See the time tab in the [generated excel file](./generated_output/report.xlsx).
Every result is to be interpreted as peak memory usage in *mb*.
Memory for *qse* is up to a granularity of 100mb (see below why).

# how memory is measured

- `qse` is written in java. 
    Garbage collection in java is very much an "under pressure only" matter, so actual ram usage is quite misleading.
    We'll use the -Xmx to set a max limit for the java virtual heap; we then search for the minimum value here such that the program does not crashes (up to a granularity of 100mb).
    To reduce the amounts of having to re-run the program, we use a binary search.
    I imagine this is the same as what they do in the qse-paper.

- for `shexer` (written in python) we use memray. Aside from a peak memory usage, memray also produces cool-looking graphs (see the html files in [shexer-memory](../generated-output/shexer-memory/)).

- With `play` and `void`/`voicl` the main load (memory but also execution time) is on the SPARQL endpoint.
    As of yet, did not find a meaningfully measure this.