// =============================================================================
// 08. Bridges - gds.bridges
// =============================================================================
// A bridge is an edge whose removal would disconnect the graph into more
// components - i.e. the ONLY path connecting two otherwise separate regions
// of the network. Bridges require an UNDIRECTED projection because "bridge"
// is a classical undirected graph-theory concept (domainGraphUndirected from
// 02_graph_projection.cypher).
//
// gds.bridges only has a `stream` mode (no write/mutate mode, since its
// result is a set of edges rather than a per-node/per-relationship score
// GDS can attach directly) - so we stream the bridge edges and then use a
// plain Cypher MATCH + SET to persist an r.isBridge = true flag onto the
// matching stored relationship ourselves.
CALL gds.bridges.stream('domainGraphUndirected')
YIELD from, to
WITH gds.util.asNode(from) AS a, gds.util.asNode(to) AS b
MATCH (a)-[r:LINKS_TO]-(b)
SET r.isBridge = true
RETURN count(r) AS bridgesFlagged;

// List the bridge edges. Matched directed (as stored) so each physical
// relationship is returned exactly once, not twice (once per direction).
MATCH (a:Domain)-[r:LINKS_TO {isBridge: true}]->(b:Domain)
RETURN a.name AS domainA, b.name AS domainB
ORDER BY domainA
LIMIT 25;
