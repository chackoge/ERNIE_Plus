#!/usr/bin/env bash
echo "Indexing"

cypher-shell <<HEREDOC
CREATE INDEX FOR (n:Pub) ON (n.pub_id);
CREATE INDEX FOR (n:Pub) ON (n.pub_year);

// Wait until index creation finishes. Increase timeOutSeconds to 600. Default = 300.
CALL db.awaitIndexes(600);
HEREDOC
