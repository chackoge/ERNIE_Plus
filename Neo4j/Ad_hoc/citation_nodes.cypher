// Sample data
CREATE (:Pub {id: 'd'})<-[:Cites]-(:Pub {id: 'a'})-[:Cites]->(:Pub {id: 'b'})-[:Cites]->(:Pub {id: 'c'})

// Clean citation nodes
MATCH (c:Citation)
DETACH DELETE c

// Create citation nodes
MATCH (p1:Pub)-[:Cites]->(p2:Pub)
CREATE (p1)<-[:Citing]-(:Citation {id: p1.id + p2.id, citing: p1.id, cited: p2.id})-[:Cited]->(p2)

// Create citation edges
MATCH (c1:Citation)
MATCH (c2:Citation)
WHERE c1 <> c2 AND (c1.citing = c2.citing OR c1.cited = c2.cited OR c1.citing = c2.cited OR c1.cited = c2.citing)
CREATE (c1)-[:Related]->(c2)