// =============================================================================
// 06. Eigenvector centrality - gds.eigenvector
// =============================================================================
// Scores a domain higher if it is linked to by other highly-scored domains
// (recursive "importance begets importance"), unlike degree which just
// counts raw links. On this directed, real-world hyperlink graph the power
// iteration does NOT fully converge even at maxIterations: 1000 (see
// didConverge: false below) - a well-known limitation of eigenvector
// centrality on directed graphs with dangling nodes / disconnected sinks,
// and exactly the practical problem PageRank's damping factor was designed
// to fix (see 07_pagerank.cypher). We still write out the (non-converged)
// scores since GDS returns its best estimate after maxIterations, and the
// relative ranking is still informative for discussion purposes.
//
// Parameters:
//   writeProperty               - node property name to write the score to.
//   relationshipWeightProperty  - weight citations by LINKS_TO.weight.
//   maxIterations               - cap on power-iteration steps.
//   tolerance                   - L2-norm change threshold to declare
//                                 convergence between iterations.
CALL gds.eigenvector.write('domainGraph', {
  writeProperty: 'eigenvector',
  relationshipWeightProperty: 'weight',
  maxIterations: 1000,
  tolerance: 1e-7
})
YIELD nodePropertiesWritten, ranIterations, didConverge;

// Top 10 by eigenvector centrality
MATCH (d:Domain)
RETURN d.name AS domain, d.eigenvector AS eigenvector
ORDER BY eigenvector DESC
LIMIT 10;
