// =============================================================================
// 03. Degree centrality - gds.degree
// =============================================================================
// Measures how many (weighted) outbound LINKS_TO edges each domain has in the
// directed projection, i.e. how heavily a domain cites/links out to others.
// High degree = "hub" behaviour (a domain that posts/aggregates a lot of
// outbound citations), NOT necessarily a domain that others link back to.
//
// Parameters:
//   writeProperty              - node property name to write the score to.
//   relationshipWeightProperty - use LINKS_TO.weight so repeated citations
//                                count more than a single one-off link.
//                                Omit this parameter for unweighted degree
//                                (simple count of distinct outbound edges).
CALL gds.degree.write('domainGraph', {
  writeProperty: 'degree',
  relationshipWeightProperty: 'weight'
})
YIELD nodePropertiesWritten, centralityDistribution;

// Top 10 by degree
MATCH (d:Domain)
RETURN d.name AS domain, d.degree AS degree
ORDER BY degree DESC
LIMIT 10;
