"""
Enhanced Graph Visualization Tool
Multiple layout strategies and visual improvements for clearer graph visualization.
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ConnectionStyle
import numpy as np
from typing import Dict, List, Optional, Tuple
import argparse
import sys
import math
from collections import defaultdict


def load_graph_from_json(json_file: str) -> dict:
    """Load graph from JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)


def smart_hierarchical_layout(G, node_type_map, spacing_factor=2.0):
    """
    Improved hierarchical layout with better node placement.
    Uses topology-based layering and barycentric crossing reduction.
    """
    G_undirected = G.to_undirected()
    
    # Group nodes by type
    depot_nodes = [n for n in G.nodes() if node_type_map.get(n) == 'depot']
    intersection_nodes = [n for n in G.nodes() if node_type_map.get(n) == 'intersection']
    bss_nodes = [n for n in G.nodes() if node_type_map.get(n) == 'bss']
    customer_nodes = [n for n in G.nodes() if node_type_map.get(n) == 'customer']
    
    # Build layers using BFS from depot
    layers = defaultdict(list)
    visited = set()
    
    if depot_nodes:
        # Start from depot
        queue = [(depot_nodes[0], 0)]
        visited.add(depot_nodes[0])
        layers[0].append(depot_nodes[0])
        
        while queue:
            node, level = queue.pop(0)
            for neighbor in G_undirected.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    layers[level + 1].append(neighbor)
                    queue.append((neighbor, level + 1))
    
    # Add unvisited nodes to appropriate layers
    for node in G.nodes():
        if node not in visited:
            node_type = node_type_map.get(node, 'intersection')
            if node_type == 'depot':
                layers[0].append(node)
            elif node_type == 'intersection':
                layers[1].append(node)
            else:
                layers[2].append(node)
    
    # Barycentric method to reduce crossings
    max_layer = max(layers.keys()) if layers else 0
    for iteration in range(3):  # Multiple passes
        for layer_idx in range(max_layer + 1):
            if layer_idx not in layers:
                continue
            
            # Calculate barycenter for each node based on neighbors
            positions = []
            for node in layers[layer_idx]:
                neighbor_positions = []
                for neighbor in G_undirected.neighbors(node):
                    for other_layer_idx, other_layer in layers.items():
                        if neighbor in other_layer:
                            neighbor_positions.append(other_layer.index(neighbor))
                
                if neighbor_positions:
                    barycenter = sum(neighbor_positions) / len(neighbor_positions)
                else:
                    barycenter = len(layers[layer_idx]) / 2
                
                positions.append((barycenter, node))
            
            # Sort by barycenter
            positions.sort()
            layers[layer_idx] = [node for _, node in positions]
    
    # Calculate positions
    pos = {}
    horizontal_spacing = spacing_factor * 2.5
    vertical_spacing = spacing_factor * 3.0
    
    for layer_idx in sorted(layers.keys()):
        layer_nodes = layers[layer_idx]
        num_in_layer = len(layer_nodes)
        y = -layer_idx * vertical_spacing
        
        if num_in_layer > 1:
            total_width = (num_in_layer - 1) * horizontal_spacing
            start_x = -total_width / 2
            for i, node in enumerate(layer_nodes):
                x = start_x + i * horizontal_spacing
                pos[node] = (x, y)
        else:
            pos[layer_nodes[0]] = (0, y)
    
    return pos


def force_directed_layout_enhanced(G, node_type_map, spacing_factor=2.0):
    """
    Enhanced force-directed layout with type-based constraints.
    """
    # Start with spring layout
    pos = nx.spring_layout(G, k=spacing_factor, iterations=200, seed=42)
    
    # Apply type-based adjustments
    depot_nodes = [n for n in G.nodes() if node_type_map.get(n) == 'depot']
    
    if depot_nodes:
        # Center depot at top
        depot_pos = pos[depot_nodes[0]]
        # Move depot to top center
        offset = np.array([0 - depot_pos[0], 1.0 - depot_pos[1]])
        pos[depot_nodes[0]] = (0, 1.0)
        
        # Adjust other nodes relative to depot
        for node in G.nodes():
            if node != depot_nodes[0]:
                current_pos = np.array(pos[node])
                pos[node] = tuple(current_pos + offset * 0.3)
    
    # Scale for better spacing
    center = np.array([np.mean([p[0] for p in pos.values()]), 
                      np.mean([p[1] for p in pos.values()])])
    for node in pos:
        pos[node] = tuple(center + (np.array(pos[node]) - center) * spacing_factor * 1.5)
    
    return pos


def radial_layout(G, node_type_map, spacing_factor=2.0):
    """
    Radial layout with depot at center and other nodes in concentric circles.
    """
    G_undirected = G.to_undirected()
    pos = {}
    
    depot_nodes = [n for n in G.nodes() if node_type_map.get(n) == 'depot']
    
    if not depot_nodes:
        # Fall back to circular layout
        return nx.circular_layout(G, scale=spacing_factor * 2)
    
    # Place depot at center
    depot = depot_nodes[0]
    pos[depot] = (0, 0)
    
    # BFS to find distances from depot
    distances = nx.single_source_shortest_path_length(G_undirected, depot)
    
    # Group by distance
    rings = defaultdict(list)
    for node, dist in distances.items():
        if node != depot:
            rings[dist].append(node)
    
    # Place nodes in unvisited set
    unvisited = [n for n in G.nodes() if n not in distances]
    if unvisited:
        max_dist = max(rings.keys()) if rings else 0
        rings[max_dist + 1] = unvisited
    
    # Place nodes in concentric circles
    for ring_idx in sorted(rings.keys()):
        nodes = rings[ring_idx]
        num_nodes = len(nodes)
        radius = ring_idx * spacing_factor * 1.5
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / num_nodes
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            pos[node] = (x, y)
    
    return pos


def community_layout(G, node_type_map, spacing_factor=2.0):
    """
    Layout based on community detection (clustering).
    """
    # Use Louvain community detection
    G_undirected = G.to_undirected()
    
    try:
        import community as community_louvain
        communities = community_louvain.best_partition(G_undirected)
    except:
        # Fall back to simple connected components
        communities = {}
        for i, component in enumerate(nx.connected_components(G_undirected)):
            for node in component:
                communities[node] = i
    
    # Group by community
    community_groups = defaultdict(list)
    for node, comm in communities.items():
        community_groups[comm].append(node)
    
    # Layout communities in a grid
    num_communities = len(community_groups)
    cols = math.ceil(math.sqrt(num_communities))
    rows = math.ceil(num_communities / cols)
    
    pos = {}
    community_spacing = spacing_factor * 8
    
    for comm_idx, (comm_id, nodes) in enumerate(sorted(community_groups.items())):
        # Position for this community
        row = comm_idx // cols
        col = comm_idx % cols
        center_x = col * community_spacing
        center_y = -row * community_spacing
        
        # Layout within community (circular)
        num_nodes = len(nodes)
        if num_nodes == 1:
            pos[nodes[0]] = (center_x, center_y)
        else:
            radius = spacing_factor * 1.5
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / num_nodes
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                pos[node] = (x, y)
    
    return pos


def draw_edge_with_bundling(ax, edges, pos, node_type_map, curved=False, curvature=0.0):
    """
    Draw edges with improved bundling to reduce visual clutter.
    Uses straight edges by default.
    """
    # Draw all edges with simple arrows (straight lines)
    for edge in edges:
        from_node = edge['from']
        to_node = edge['to']
        
        if from_node not in pos or to_node not in pos:
            continue
        
        # Simple straight edge with arrow
        ax.annotate('',
                   xy=pos[to_node],
                   xytext=pos[from_node],
                   arrowprops=dict(
                       arrowstyle='->',
                       color='black',
                       alpha=0.6,
                       linewidth=1.5,
                       shrinkA=15,  # Shrink to not overlap with nodes
                       shrinkB=15
                   ),
                   zorder=1)


def visualize_graph(
    graph: dict,
    output_file: Optional[str] = None,
    show_labels: bool = True,
    show_edge_labels: bool = False,
    layout: str = "smart_hierarchical",
    figsize: tuple = (18, 14),
    node_size: int = 1200,
    font_size: int = 9,
    curved_edges: bool = False,
    edge_curvature: float = 0.0,
    spacing_factor: float = 2.5
):
    """
    Enhanced visualization with multiple layout options.
    
    Args:
        layout: 'smart_hierarchical', 'radial', 'force_directed', 'community', 'spring'
    """
    # Create NetworkX graph
    G = nx.DiGraph()
    
    node_type_map = {}
    for node_name, node_data in graph['nodes'].items():
        node_type = node_data.get('type', 'intersection')
        G.add_node(node_name)
        node_type_map[node_name] = node_type
    
    for edge in graph['edges']:
        G.add_edge(
            edge['from'],
            edge['to'],
            distance=edge.get('distance', 8.0),
            traffic_factor=edge.get('traffic_factor', 1.0)
        )
    
    # Color scheme inspired by reference image
    type_colors = {
        'depot': '#DC143C',        # Crimson red (like D, D2)
        'customer': '#FF8C00',     # Dark orange (like C1-C6)
        'bss': '#FFD700',          # Gold/yellow (like BSS1, BSS2)
        'intersection': '#00CED1'  # Dark turquoise/cyan (like nodes 1-8)
    }
    
    type_markers = {
        'depot': 's',              # Square for depot
        'customer': 'o',           # Circle for customer
        'bss': '^',                # Triangle for BSS
        'intersection': 'o'        # Circle for intersection
    }
    
    # Create figure with white background
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')
    
    # Choose layout
    if layout == "smart_hierarchical":
        pos = smart_hierarchical_layout(G, node_type_map, spacing_factor)
    elif layout == "radial":
        pos = radial_layout(G, node_type_map, spacing_factor)
    elif layout == "force_directed":
        pos = force_directed_layout_enhanced(G, node_type_map, spacing_factor)
    elif layout == "community":
        pos = community_layout(G, node_type_map, spacing_factor)
    elif layout == "spring":
        pos = nx.spring_layout(G, k=spacing_factor, iterations=200, seed=42, scale=2.0)
    else:
        pos = smart_hierarchical_layout(G, node_type_map, spacing_factor)
    
    # Draw edges with bundling (straight edges)
    draw_edge_with_bundling(ax, graph['edges'], pos, node_type_map, 
                           curved=False, curvature=0.0)
    
    # Draw nodes by type
    nodes_by_type = defaultdict(list)
    for node, node_type in node_type_map.items():
        nodes_by_type[node_type].append(node)
    
    for node_type, nodes in nodes_by_type.items():
        color = type_colors.get(node_type, '#95A5A6')
        marker = type_markers.get(node_type, 'o')
        
        # BSS nodes are slightly bigger (like in reference image)
        size = node_size * 1.3 if node_type == 'bss' else node_size
        
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=nodes,
            node_color=color,
            node_size=size,
            node_shape=marker,
            alpha=1.0,
            edgecolors='black',
            linewidths=2.5,
            ax=ax
        )
    
    # Draw labels with better styling (black text)
    if show_labels:
        nx.draw_networkx_labels(
            G, pos,
            font_size=font_size,
            font_weight='bold',
            font_color='black',
            ax=ax
        )
    
    # Edge labels
    if show_edge_labels:
        edge_labels = {}
        for edge in graph['edges']:
            edge_labels[(edge['from'], edge['to'])] = f"{edge.get('distance', 8.0):.1f}"
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels,
            font_size=font_size - 2,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
            ax=ax
        )
    
    # Enhanced legend
    legend_elements = []
    for node_type in ['depot', 'customer', 'bss', 'intersection']:
        if node_type in nodes_by_type:
            color = type_colors.get(node_type, '#95A5A6')
            marker = type_markers.get(node_type, 'o')
            legend_elements.append(
                plt.Line2D([0], [0], marker=marker, color='w',
                          markerfacecolor=color, markersize=14,
                          markeredgewidth=2.5, markeredgecolor='black',
                          label=f"{node_type.capitalize()} ({len(nodes_by_type[node_type])})",
                          linestyle='None')
            )
    
    legend = ax.legend(handles=legend_elements, loc='upper left', 
                      fontsize=11, framealpha=0.95, edgecolor='gray')
    legend.get_frame().set_facecolor('white')
    
    # Title with graph stats
    num_nodes = len(G.nodes())
    num_edges = len(graph['edges'])
    ax.set_title(f'Graph Visualization - {num_nodes} nodes, {num_edges} edges\nLayout: {layout}',
                fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Visualization saved to {output_file}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Graph Visualization Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Layout Options:
  smart_hierarchical : Topology-based layers with crossing reduction (DEFAULT - BEST FOR MOST GRAPHS)
  radial            : Depot at center, nodes in concentric circles
  force_directed    : Physics-based with type constraints
  community         : Cluster-based layout
  spring            : Standard force-directed layout

Examples:
  %(prog)s graph.json                                    # Smart hierarchical layout
  %(prog)s graph.json --layout radial -o output.png     # Radial layout, save to file
  %(prog)s graph.json --layout community --spacing 3    # Community layout, more spacing
        """
    )
    parser.add_argument('input_file', nargs='?', help='JSON file containing the graph')
    parser.add_argument('-o', '--output', help='Output file path (e.g., graph.png)')
    parser.add_argument('--no-labels', action='store_true', help='Hide node labels')
    parser.add_argument('--edge-labels', action='store_true', help='Show edge distances')
    parser.add_argument('--layout', 
                       choices=['smart_hierarchical', 'radial', 'force_directed', 'community', 'spring'],
                       default='smart_hierarchical',
                       help='Layout algorithm (default: smart_hierarchical)')
    parser.add_argument('--size', type=int, default=1200, help='Node size (default: 1200)')
    parser.add_argument('--spacing', type=float, default=2.5,
                       help='Node spacing factor (default: 2.5)')
    
    args = parser.parse_args()
    
    if args.input_file:
        try:
            graph = load_graph_from_json(args.input_file)
            visualize_graph(
                graph,
                output_file=args.output,
                show_labels=not args.no_labels,
                show_edge_labels=args.edge_labels,
                layout=args.layout,
                node_size=args.size,
                spacing_factor=args.spacing
            )
        except FileNotFoundError:
            print(f"✗ Error: File '{args.input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("✗ No input file provided. Usage: python script.py graph.json")
        print("  Run with --help for more options")
        sys.exit(1)


if __name__ == "__main__":
    main()