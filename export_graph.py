from rcsbapi import data
import rustworkx

schema = data.DataSchema()
rustworkx.node_link_json(
    graph=schema._schema_graph,
    path="schema_graph_named.json",
    node_attrs=lambda node: getattr(node, "name"),
)