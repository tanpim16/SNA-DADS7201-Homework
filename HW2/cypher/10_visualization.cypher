// =============================================================================
// 10. Visualization queries - Neo4j Browser / Bloom
// =============================================================================

// --- A) Full styled graph: run this, then in Neo4j Browser open the
// "..." panel on the (:Domain) node category and set:
//   Size   -> pagerank    (bigger circle = higher PageRank / authority)
//   Color  -> community   (categorical color per Louvain community)
// Bloom: use a rule-based style with the same two properties, e.g.
//   Domain.size  = withinRange(pagerank, ...)
//   Domain.color = category(community)
MATCH (a:Domain)-[r:LINKS_TO]->(b:Domain)
RETURN a, r, b
LIMIT 500;

// --- B) Bridges highlighted separately in red: run A) above first for the
// base layout, then run this to overlay/inspect just the bridge edges -
// in Browser, bridge relationships can be recolored red via the
// relationship-type style panel, or by giving them a distinct :BRIDGE
// label as below so Browser/Bloom can color by relationship type directly.
MATCH (a:Domain)-[r:LINKS_TO {isBridge: true}]->(b:Domain)
RETURN a, r, b;

// Optional: materialize a second relationship type so Browser's default
// per-type coloring shows bridges in a distinct color automatically.
MATCH (a:Domain)-[r:LINKS_TO {isBridge: true}]->(b:Domain)
MERGE (a)-[b2:BRIDGE]->(b)
SET b2.weight = r.weight
RETURN count(b2) AS bridgeRelsCreated;

// --- C) Node size/color driven directly from Cypher (no manual Browser
// styling), useful when scripting a screenshot or exporting to another
// viz tool: bucket PageRank into a 1-5 size tier and return community
// as a color-mappable integer.
MATCH (d:Domain)
RETURN d.name AS domain,
       d.pagerank AS pagerank,
       CASE
         WHEN d.pagerank >= 2.0 THEN 5
         WHEN d.pagerank >= 1.0 THEN 4
         WHEN d.pagerank >= 0.5 THEN 3
         WHEN d.pagerank >= 0.2 THEN 2
         ELSE 1
       END AS sizeTier,
       d.community AS colorGroup
ORDER BY pagerank DESC;
