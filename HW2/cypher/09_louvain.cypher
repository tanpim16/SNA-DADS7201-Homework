// =============================================================================
// 09. Louvain community detection - gds.louvain
// =============================================================================
// Groups domains into communities that are more densely connected to each
// other than to the rest of the network, by greedily optimizing modularity.
// Run on the UNDIRECTED projection (domainGraphUndirected) since community
// membership is a mutual/reciprocal notion (A and B "belong together"
// regardless of which one links to the other) rather than a directional one.
//
// Parameters:
//   writeProperty               - node property to write the community id to.
//   relationshipWeightProperty  - weight edges by LINKS_TO.weight so heavily
//                                 cited connections pull nodes into the same
//                                 community more strongly than one-off links.
//   maxLevels / maxIterations (optional, defaults used here) - control the
//                                 hierarchical merge passes Louvain performs;
//                                 defaults are sufficient at this graph size.
CALL gds.louvain.write('domainGraphUndirected', {
  writeProperty: 'community',
  relationshipWeightProperty: 'weight'
})
YIELD communityCount, modularity, nodePropertiesWritten;

// Community sizes with their top domain (by PageRank) as a label
MATCH (d:Domain)
WITH d.community AS community, d
ORDER BY d.pagerank DESC
WITH community, collect(d.name)[0..5] AS topDomains, count(*) AS size
RETURN community, size, topDomains
ORDER BY size DESC
LIMIT 10;
