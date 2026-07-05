// =============================================================================
// 04. Betweenness centrality - gds.betweenness
// =============================================================================
// Measures how often a domain lies on the shortest path between two other
// domains. High betweenness = a "bridge"/broker that connects otherwise
// separate parts of the network (e.g. URL shorteners, redirect services,
// syndication feeds) - as opposed to a hub that simply has many links.
//
// Parameters:
//   writeProperty - node property name to write the score to.
//   samplingSize / samplingSeed (optional, not used here) - for very large
//                   graphs, approximate betweenness via random source-node
//                   sampling instead of exact computation over all pairs.
CALL gds.betweenness.write('domainGraph', {
  writeProperty: 'betweenness'
})
YIELD nodePropertiesWritten, centralityDistribution;

// Top 10 by betweenness
MATCH (d:Domain)
RETURN d.name AS domain, d.betweenness AS betweenness
ORDER BY betweenness DESC
LIMIT 10;
