import json
from pathlib import Path
import networkx as nx

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_graph(concepts_path=DATA_DIR / "concepts.json",
               prereq_path=DATA_DIR / "prerequisites.json") -> nx.DiGraph:
    concepts = json.loads(Path(concepts_path).read_text(encoding="utf-8"))
    edges = json.loads(Path(prereq_path).read_text(encoding="utf-8"))

    g = nx.DiGraph()
    for c in concepts:
        g.add_node(c["id"], **{k: v for k, v in c.items() if k != "id"})
    for e in edges:
        if e["from"] not in g or e["to"] not in g:
            raise ValueError(f"Edge references unknown concept: {e}")
        g.add_edge(e["from"], e["to"],
                   confidence=e.get("confidence", 1.0),
                   sources=e.get("sources", []))
    if not nx.is_directed_acyclic_graph(g):
        raise ValueError("Graph contains a cycle")
    return g