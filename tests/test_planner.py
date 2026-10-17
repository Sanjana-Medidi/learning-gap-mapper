import networkx as nx
from app.path_planner import roadmap, next_steps

def make_graph():
    g = nx.DiGraph()
    g.add_edges_from([("algebra", "derivatives"),
                      ("derivatives", "gradient_descent"),
                      ("linear_algebra", "gradient_descent")])
    return g

def test_roadmap_order_and_exclusion():
    path = roadmap(make_graph(), "gradient_descent", known={"algebra"})
    assert "algebra" not in path
    assert path.index("derivatives") < path.index("gradient_descent")
    assert path[-1] == "gradient_descent"

def test_known_goal_gives_empty_roadmap():
    assert roadmap(make_graph(), "derivatives", known={"derivatives"}) == []

def test_next_steps_frontier():
    assert next_steps(make_graph(), known={"algebra"}) == ["derivatives", "linear_algebra"]