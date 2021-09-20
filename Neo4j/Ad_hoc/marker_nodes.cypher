MATCH (p:pub {is_marker_node: true})
SET p:marker_node;

// Sub-graph for 1 marker node
MATCH (p:marker_node)
WITH p
LIMIT 1
MATCH (p)-[r:cites]-(n)
RETURN *;