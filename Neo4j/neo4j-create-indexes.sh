#!/usr/bin/env bash
echo "Indexing"

cypher-shell <<HEREDOC
CREATE INDEX FOR (p:pub) ON (p.seq_id);
CREATE INDEX FOR (p:pub) ON (p.pub_year);

CREATE INDEX FOR (c:cluster_testing_k10_b0) ON (c.cluster_no);
CREATE INDEX FOR (c:cluster_testing_k5_b0) ON (c.cluster_no);

// Wait until index creation finishes. Increase timeOutSeconds to 600. Default = 300.
CALL db.awaitIndexes(600);
HEREDOC
