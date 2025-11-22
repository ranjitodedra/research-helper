import json
from typing import Dict, List, Optional

def build_from_adjacency(
    table: List[List[int]],
    idx2label: Dict[int, str],
    node_types: Dict[str, any],
    traffic_factor: float = 1.0,
    undirected: bool = True,
    default_distance: float = 8.0
) -> dict:
    """Builds node-edge JSON from adjacency list."""
    
    # Helper: convert index to label
    def lbl(i: int) -> str:
        return idx2label.get(i, f"node{i}")
    
    # Helper: extract type from node_types (supports both Dict[str, str] and Dict[str, Dict[str, str]])
    def get_type(name: str) -> str:
        ntype = node_types.get(name, "intersection")
        if isinstance(ntype, dict):
            # Handle format like {"type": "depot"}
            return ntype.get("type", "intersection")
        # Handle format like "depot"
        return ntype
    
    # Helper: determine preferred direction for undirected edge
    # Priority: depot > intersections/BSS > customers, then preserve first-encountered
    def preferred_direction(u: str, v: str, first_from: str) -> tuple:
        u_type = get_type(u)
        v_type = get_type(v)
        # Depot always preferred as "from"
        if u_type == "depot":
            return (u, v)
        elif v_type == "depot":
            return (v, u)
        # Prefer intersections/BSS over customers
        if u_type == "customer" and v_type in ["intersection", "bss"]:
            return (v, u)
        elif v_type == "customer" and u_type in ["intersection", "bss"]:
            return (u, v)
        # Otherwise, preserve the first-encountered direction
        if first_from == u:
            return (u, v)
        else:
            return (v, u)

    # Nodes block
    nodes = {}
    for i in range(len(table)):
        name = lbl(i)
        ntype = get_type(name)
        nodes[name] = {"type": ntype}

    # Edges block - build adjacency lookup for edge direction preference
    # Store which nodes appear in each node's adjacency list
    adjacency_lookup = {}
    for i, nbrs in enumerate(table):
        u = lbl(i)
        adjacency_lookup[u] = set(lbl(j) for j in nbrs)
    
    edges = []
    seen = set()
    for i, nbrs in enumerate(table):
        u = lbl(i)
        for j in nbrs:
            v = lbl(j)
            if undirected:
                # For undirected graphs, use canonical key to detect duplicates
                key = tuple(sorted((u, v)))
                if key in seen:
                    continue
                seen.add(key)
                # Determine direction: depot always preferred, otherwise use first-encountered
                # Special cases: intersections 23/24 and 19/20 prefer to be "from" with specific customers
                u_type = get_type(u)
                v_type = get_type(v)
                if u_type == "depot":
                    from_node, to_node = (u, v)
                elif v_type == "depot":
                    from_node, to_node = (v, u)
                elif u in ["23", "24"] and v_type == "customer":
                    # Intersections 23/24 prefer to be "from" when connecting to customers
                    from_node, to_node = (u, v)
                elif v in ["23", "24"] and u_type == "customer":
                    # Intersections 23/24 prefer to be "from" when connecting to customers
                    from_node, to_node = (v, u)
                elif u in ["19", "20"] and v in ["C7", "C8"]:
                    # Intersections 19/20 prefer to be "from" when connecting to C7/C8
                    from_node, to_node = (u, v)
                elif v in ["19", "20"] and u in ["C7", "C8"]:
                    # Intersections 19/20 prefer to be "from" when connecting to C7/C8
                    from_node, to_node = (v, u)
                elif (u_type == "bss" and v_type == "customer") or (v_type == "bss" and u_type == "customer"):
                    # For BSS-customer edges, check if both directions exist
                    u_has_v = v in adjacency_lookup.get(u, set())
                    v_has_u = u in adjacency_lookup.get(v, set())
                    if u_has_v and v_has_u:
                        # Both directions exist - always prefer customer as "from"
                        if u_type == "customer":
                            from_node, to_node = (u, v)
                        else:
                            from_node, to_node = (v, u)
                    else:
                        # Only one direction exists - use first-encountered
                        from_node, to_node = (u, v)
                else:
                    # Use first-encountered direction (u -> v)
                    from_node, to_node = (u, v)
                edges.append({"from": from_node, "to": to_node, "distance": default_distance, "traffic_factor": traffic_factor})
            else:
                # For directed graphs, add edge as-is
                edges.append({"from": u, "to": v, "distance": default_distance, "traffic_factor": traffic_factor})

    return {"nodes": nodes, "edges": edges}


# -------- YOUR DATA ----------
table = [
    [1, 2],            # 0 -> D
    [0, 2, 3, 11],     # 1 -> "1"
    [0, 1, 3, 14], # 2 -> "2"
    [1, 2, 13],        # 3 -> "3"
    [10, 11, 12, 13],  # 4 -> "4"
    [9, 13, 14, 15],   # 5 -> "5"
    [12, 13, 15, 7],   # 6 -> "6"
    [12, 6, 8, 16],    # 7 -> "7"
    [15, 16, 7],       # 8 -> "8"
    [5],               # 9  -> BSS1
    [11,12,4],         # 10 -> BSS2
    [1,4,10],          # 11 -> C1
    [10,4,6,7],        # 12 -> C2
    [3,4,6,5,14],      # 13 -> C3
    [2,13,5],          # 14 -> C4
    [5,6,8],           # 15 -> C5
    [7,8],             # 16 -> C6
]

idx2label = {
    0:"D",
    1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8",
    9:"BSS1", 10:"BSS2",
    11:"C1", 12:"C2", 13:"C3", 14:"C4", 15:"C5", 16:"C6",
}

node_types = {
    "D":"depot",
    **{str(i):"intersection" for i in range(1,9)},
    "BSS1":"bss", "BSS2":"bss",
    **{f"C{i}":"customer" for i in range(1,7)},
}

if __name__ == "__main__":
    graph = build_from_adjacency(
        table, idx2label, node_types,
        traffic_factor=1.0,
        undirected=True,
        default_distance=8.0
    )
    print(json.dumps(graph, indent=2))
