// =============================================================================
// 11. Top-10 comparison table across all centrality metrics
// =============================================================================
// Builds a single side-by-side table: rank 1-10, and the domain holding that
// rank under each metric. Reading across a row shows how differently each
// metric ranks the network (see ANALYSIS.md for the full interpretation).

CALL {
  MATCH (d:Domain) RETURN d.name AS domain, d.degree AS v ORDER BY v DESC LIMIT 10
}
WITH collect(domain) AS byDegree
CALL {
  MATCH (d:Domain) RETURN d.name AS domain, d.betweenness AS v ORDER BY v DESC LIMIT 10
}
WITH byDegree, collect(domain) AS byBetweenness
CALL {
  MATCH (d:Domain) RETURN d.name AS domain, d.closeness AS v ORDER BY v DESC LIMIT 10
}
WITH byDegree, byBetweenness, collect(domain) AS byCloseness
CALL {
  MATCH (d:Domain) RETURN d.name AS domain, d.eigenvector AS v ORDER BY v DESC LIMIT 10
}
WITH byDegree, byBetweenness, byCloseness, collect(domain) AS byEigenvector
CALL {
  MATCH (d:Domain) RETURN d.name AS domain, d.pagerank AS v ORDER BY v DESC LIMIT 10
}
WITH byDegree, byBetweenness, byCloseness, byEigenvector, collect(domain) AS byPageRank
UNWIND range(0, 9) AS i
RETURN i + 1 AS rank,
       byDegree[i]      AS top_degree,
       byBetweenness[i] AS top_betweenness,
       byCloseness[i]   AS top_closeness,
       byEigenvector[i] AS top_eigenvector,
       byPageRank[i]    AS top_pagerank
ORDER BY rank;

// --- Community (Louvain) summary: size + representative domains per cluster
MATCH (d:Domain)
WITH d.community AS community, d
ORDER BY d.pagerank DESC
WITH community, count(*) AS size, collect(d.name)[0..5] AS topDomains
RETURN community, size, topDomains
ORDER BY size DESC
LIMIT 10;
