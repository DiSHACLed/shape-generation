from ..config import RESULTS
from typing import Callable, Optional
from dataclasses import dataclass
import time
from pathlib import Path

Key = str

Command = Callable[[Key], None]
CommandRW = Callable[[Key,bool], None]

skip : Command = (lambda _ : None)

@dataclass
class Task():
    description: str
    code: str
    done : Callable[[Key], bool]
    meat : Command
    prep : Optional[Command] = None
    post : Optional[Command] = None
    stats : Optional[Command] = None
    validate : Optional[CommandRW] = None

from .report import report_add

def execute(task : Task, key : Key, repeat : bool) :
    if not repeat and task.done(key) :
        print(f"Task code-named {task.code} already ran on {key}.")
        return
    if task.prep is not None :
        print(f"Preparation {task.code} on {key}...")
        task.prep(key)
    print(f"Executing {task.code} on {key}...")
    t_i = time.time()
    try :
        task.meat(key)
        print(f"Finished executing {task.code} on {key} :)")
        Path(f"{RESULTS}/{task.code}/{key}.error").unlink(missing_ok=True)
    except Exception as e :
        print(f"Error while executing {task.code} on {key} :( See {RESULTS}/{task.code}/{key}.error")
        with open(f"{RESULTS}/{task.code}/{key}.error", 'w') as f :
            f.write(str(e))
    t_f = time.time()
    total = str(t_f - t_i)
    report_add('time', task.code, key, total)
    with open(f"{RESULTS}/{task.code}/{key}.time", 'w') as f :
        # f.write(struct.pack("d", (t_f - t_i))) "wb"
        f.write(total)
    if task.post is not None :
        print(f"Cleaning {task.code} on {key}...")
        task.post(key)
    # if task.stats is not None :
    #     task.stats(key)
    # else :
    #     _generic_stats(task.code, key)