from typing import Optional

def minmax2constraints(mincount : int, maxcount : int) -> tuple[Optional[int],Optional[int]] :
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
