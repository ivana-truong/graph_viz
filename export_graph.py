import json
from rcsbapi import data
import rustworkx
from rustworkx import PyDiGraph

from typing import Any
from dataclasses import dataclass, asdict

from pathlib import Path

schema = data.DataSchema()

num_nodes = 0

num_links: int = 0


@dataclass(frozen=True)
class NodeData:
    name: str
    rustworkx_idx: int

@dataclass(frozen=True)
class Node:
    id: int
    data: NodeData

    @staticmethod
    def new_node(data: NodeData) -> "Node":
        global num_nodes
        num_nodes += 1
        return Node(num_nodes, data)





@dataclass(frozen=True)
class Link:
    source: int
    target: int
    id: int
    data: Any

    @staticmethod
    def new_link(source: int, target: int, data: Any) -> "Link":
        global num_links
        num_links += 1
        return Link(source, target, num_links, data)

# _field_to_idx_dict

# _root_to_idx


def traverse_neighbors(root: Node, schema_graph: PyDiGraph[Any, Any], seen: set[int]) -> tuple[list[Node], list[Link]]:
    nodes: list[Node] = []
    links: list[Link] = []

    for neighbor_idx in schema_graph.neighbors(root_idx):
        if neighbor_idx not in seen:
            seen.add(neighbor_idx)

            # Create neighbor node
            node_for_neighbor = Node.new_node(data=NodeData(name=schema_graph[root_idx].name, rustworkx_idx=neighbor_idx))
            nodes.append(node_for_neighbor)

            # Create link between root and neighbor
            links.append(Link.new_link(root.id, node_for_neighbor.id, None))

            neighbor_nodes, neighbor_links = traverse_neighbors(node_for_neighbor, schema_graph, seen)
            nodes.extend(neighbor_nodes)
            links.extend(neighbor_links)

    return (nodes, links)


def get_root_graph(root_idx: int, schema_graph: PyDiGraph[Any, Any]) -> tuple[Node, list[Node], list[Link]]:
    seen: set[int] = {root_idx}
    node_for_root = Node.new_node(data=NodeData(name=schema_graph[root_idx].name, rustworkx_idx=root_idx))

    nodes, links = traverse_neighbors(node_for_root, schema_graph, seen=seen)
    return node_for_root, [node_for_root, *nodes], links


query_root_node = Node.new_node(NodeData("query", 0))
nodes: list[Node] = [query_root_node]
links: list[Link] = []


for root_idx in schema._schema_graph.neighbors(0):
    root_node, n, l = get_root_graph(root_idx, schema._schema_graph)
    # nodes.extend(n)
    # links.extend(l)

    nodes.append(root_node)

    links.append(Link.new_link(query_root_node.id, root_node.id, None))


Path("/home/ivanatruo/Repos/graph_viz/new_schema_graph.json").write_text(
    json.dumps({"directed": True, "multigraph": True, "attrs": None, "nodes": [asdict(node) for node in nodes], "links": [asdict(link) for link in links]})
)

# rustworkx.node_link_json(
#     graph=schema._schema_graph,
#     path="schema_graph_named.json",
#     node_attrs=lambda node: getattr(node, "name"),
# )

# TODO: export the graph so that type names and field names are retained
