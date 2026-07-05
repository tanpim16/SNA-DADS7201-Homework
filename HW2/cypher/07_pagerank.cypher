// =============================================================================
// 07. PageRank - gds.pageRank
// =============================================================================
// Like eigenvector centrality, but adds a damping factor that periodically
// "teleports" the random walk to a random node instead of always following
// links. This fixes the convergence problems eigenvector centrality has on
// directed graphs with dangling nodes (see 06_eigenvector.cypher) and is the
// standard measure of "authority": a domain many other important domains
// point to, e.g. Wikipedia, major news sites, YouTube.
//
// Parameters:
//   writeProperty               - node property name to write the score to.
//   relationshipWeightProperty  - weight citations by LINKS_TO.weight.
//   dampingFactor               - probability of following an outbound link
//                                 vs. teleporting (0.85 is the original
//                                 Google PageRank default).
//   maxIterations               - cap on iterations (converges well before
//                                 this on our data - see ranIterations).
CALL gds.pageRank.write('domainGraph', {
  writeProperty: 'pagerank',
  relationshipWeightProperty: 'weight',
  dampingFactor: 0.85,
  maxIterations: 100
})
YIELD nodePropertiesWritten, ranIterations, didConverge;

// Top 10 by PageRank
MATCH (d:Domain)
RETURN d.name AS domain, d.pagerank AS pagerank
ORDER BY pagerank DESC
LIMIT 10;
