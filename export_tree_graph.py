import json
from rcsbapi import data
import rustworkx
from rustworkx import PyDiGraph

from typing import Any, Union
from dataclasses import dataclass, asdict

from pathlib import Path

schema = data.DataSchema()


@dataclass(frozen=True)
class EndChild:
    name: str


@dataclass(frozen=True)
class Child:
    name: str
    children: list[Union["Child", EndChild]]


children_t = Child | EndChild

children: list[children_t] = []


def get_child(root_idx: int, schema_graph: PyDiGraph[Any, Any], seen: set[int]) -> children_t:
    if root_idx in seen:
        return []

    seen.add(root_idx)

    node_name = schema_graph[root_idx].name

    if len(schema_graph.neighbors(root_idx)) == 0:
        return EndChild(node_name)
    else:
        children = []

        for neighbor_idx in schema_graph.neighbors(root_idx):
            children.append(get_child(neighbor_idx, schema_graph, seen))

        return Child(name=node_name, children=children)


for root_idx in schema._schema_graph.neighbors(0):
    children.append(get_child(root_idx, schema._schema_graph, seen=set()))

Path("/home/ivanatruo/Repos/graph_viz/schema_tree_graph.json").write_text(
    json.dumps({"name": "query", "children": [asdict(child) for child in children]})
)
