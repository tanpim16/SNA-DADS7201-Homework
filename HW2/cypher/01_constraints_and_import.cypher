// =============================================================================
// 01. Constraints + import: builds (:Domain)-[:LINKS_TO {weight}]->(:Domain)
// =============================================================================
// Prerequisite: copy edges.csv (source_domain,target_domain,weight) produced by
// data_prep.py into Neo4j's import directory (the folder configured by
// `dbms.directories.import`, default: <neo4j-home>/import). With the official
// Docker image, `docker cp edges.csv <container>:/var/lib/neo4j/import/edges.csv`
// (or bind-mount the folder to /var/lib/neo4j/import).

// --- Constraint: one node per unique domain name, and an index for lookups.
// Creating the uniqueness constraint also creates a backing index, so a
// separate `CREATE INDEX` is not needed for equality lookups on d.name.
CREATE CONSTRAINT domain_name_unique IF NOT EXISTS
FOR (d:Domain) REQUIRE d.name IS UNIQUE;

// --- Import: MERGE (not CREATE) so re-running this file is idempotent.
// toInteger() casts the CSV string column to a number so weight can be
// used as a numeric relationship property (needed for weighted algorithms).
LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MERGE (s:Domain {name: row.source_domain})
MERGE (t:Domain {name: row.target_domain})
MERGE (s)-[r:LINKS_TO]->(t)
SET r.weight = toInteger(row.weight);

// --- Sanity check: node/relationship counts after import.
MATCH (d:Domain) WITH count(d) AS domains
MATCH ()-[r:LINKS_TO]->() RETURN domains, count(r) AS links;
