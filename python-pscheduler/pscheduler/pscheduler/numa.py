"""
NUMA Functions
"""

from .program import *

def numa_node_ok(node):
    """
    This function attempts to determine if a given NUMA node can run a
    guaranteed-not-to-fail program like true(1).  The purpose is to
    handle situations like that in #839 where the machine has no
    usable memory on the same node as the interface.
    # PORT: This is linux-only.
    """
    status, _out, err = run_program(["numactl", "-N", str(node), "true"])

    if status == 0:
        return (True, None)

    errs = err.split("\n")
    short_errs = []
    for line in errs:
        if line.startswith("usage: "):
            break
        short_errs.append(line)

    final_err = "\n".join(short_errs).strip()
    return (False, final_err)

def numa_cpu_core_ok(core):
    """
    This function attempts to determine if a given cpu core can run a
    guaranteed-not-to-fail program like true(1).  The purpose is to
    handle situations like that in #839 where the machine has no
    usable memory on the same node as the interface.
    # PORT: This is linux-only.
    """
    status, _out, err = run_program(["numactl", "-C", str(core), "true"])

    if status == 0:
        return (True, None)

    errs = err.split("\n")
    short_errs = []
    for line in errs:
        if line.startswith("usage: "):
            break
        short_errs.append(line)

    final_err = "\n".join(short_errs).strip()
    return (False, final_err)

if __name__ == "__main__":

    for node in range(0, 3):
        print(node, " -> ", numa_ok(node))

    print("Foo -> ", numa_ok("Foo"))
