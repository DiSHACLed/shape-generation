# contents of repo

Repo contains a couple of things:
- test suite, see below; `suite`
- VOICL; home-brewn script to get shacl from void description (exposed as cli as well; `voicl`)
- wrapper to spin up other virtuoso dockers and load files (exposed as cli: `virtuoso`)
- wrappers for other tooling...

# get started

Go quickly over [config.py](./src/shape_gen/config.py)!

Without installation; inside this folder, run any of the exposed cli tools by running `uv run toolname` with ̀̀̀`toolname` any of the exposed interfaces: `voicl`, `vituoso`, `void`, `suite`,... E.g.
```
uv run suite
```
Installing tools to path (probably `~/.local`); 
```
uv tool install suite --editable .
```
You probably want `--editable` flag.

# test suite

First get your `ttl`-files in `SAMPLE_DATA` (see `config.py`).

```shell
suite input # outputs all the tasks
suite run # all files on all tasks
suite run file1 file2 # file1 & file2 with all tasks
suite run file1 file2 --task task1 --task2 --task task3 # file1 & file2 with task1 and task2 and task3
```

Results will be in `RESULTS`, virtuoso databases in `VIRTUOSO_DIR`.

TODO docstrings; correct most horrible offenders