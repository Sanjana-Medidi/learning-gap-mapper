import networkx as nx

def expand_known(g, known):
    """If you know a concept, assume you know all of its prerequisites."""
    known = set(known)
    implied = set()
    for k in known:
        implied |= nx.ancestors(g, k)
    return known | implied

def roadmap(g, goal, known, infer_known=True):
    if goal not in g:
        raise KeyError(f"Unknown goal: {goal}")
    known_all = expand_known(g, known) if infer_known else set(known)
    needed = (nx.ancestors(g, goal) | {goal}) - known_all
    return list(nx.lexicographical_topological_sort(g.subgraph(needed)))

def next_steps(g, known, goal=None, infer_known=True):
    known_all = expand_known(g, known) if infer_known else set(known)
    candidates = set(g.nodes) - known_all
    if goal:
        candidates &= nx.ancestors(g, goal) | {goal}
    return sorted(n for n in candidates
                  if all(p in known_all for p in g.predecessors(n)))