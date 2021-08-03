/*
Parameters example:

Neo4j Browser:

:param seq_ids => [0, 1, 2]
:param n => 200

JetBrains Graph Database Support plug-in:

{
  "n": 200,
  "seq_ids": [
    0,
    1,
    2
  ]
}
*/

/*
(1) find all nodes of minimum in_degree n that cite or are cited by some node p for which we know the integer id
(2) all the nodes that are cited by at least two of the nodes (co-cited) in (1)
*/
UNWIND $seq_ids AS seq_id
MATCH (x1)--(p:Pub {seq_id: seq_id})--(y1)
WITH p, x1, y1, size((x1)<--()) AS x1_in_degree, size((y1)<--()) AS y1_in_degree
WHERE x1_in_degree >= $n AND y1_in_degree >= $n
MATCH (x1)-->(cc)<--(y1)
RETURN DISTINCT p.seq_id, cc.seq_id;

/*
(1) find all nodes of minimum in_degree n that cite or are cited by some node p for which we know the integer id
(3) all the nodes that cite at least two of the nodes (bibliographically coupled) in (1)
*/
UNWIND $seq_ids AS seq_id
MATCH (x1)--(p:Pub {seq_id: seq_id})--(y1)
WITH p, x1, y1, size((x1)<--()) AS x1_in_degree, size((y1)<--()) AS y1_in_degree
WHERE x1_in_degree >= $n AND y1_in_degree >= $n
MATCH (x1)<--(bc)-->(y1)
RETURN DISTINCT p.seq_id, bc.seq_id;
