path = "D -> 2 -> C3 -> 7 -> C1 -> 4 -> BSS1 -> C5 -> 3 -> C6 -> BSS4 -> C7 -> C2 -> C4 -> C8 -> C9 -> 5 -> 1 -> D"

# Split by '->' and count edges as (number of nodes - 1)
nodes = [node.strip() for node in path.split("->")]
num_edges = len(nodes) - 1

print("Nodes:", nodes)
print("Number of edges:", num_edges)
