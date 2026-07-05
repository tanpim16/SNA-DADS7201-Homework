// =============================================================================
// 05. Closeness centrality - gds.closeness
// =============================================================================
// Measures how close a domain is to all other reachable domains (inverse of
// average shortest-path distance). High closeness = a domain that can reach
// most of the rest of the network in few hops - useful for spotting domains
// well-positioned to spread content quickly.
//
// GDS uses the Wasserman-Faust improved formula by default, which normalizes
// by the size of the domain's own reachable component rather than the whole
// graph - this lets nodes in small disconnected components still score highly
// (even up to 1.0) relative to their own component, which is why some
// small/isolated clusters can outrank larger, better-connected domains here.
//
// Parameters:
//   writeProperty     - node property name to write the score to.
//   useWassermanFaust - true (default) uses the improved formula described
//                       above; set to false for the classic definition,
//                       which instead penalizes nodes in small components.
CALL gds.closeness.write('domainGraph', {
  writeProperty: 'closeness'
})
YIELD nodePropertiesWritten, centralityDistribution;

// Top 10 by closeness
MATCH (d:Domain)
RETURN d.name AS domain, d.closeness AS closeness
ORDER BY closeness DESC
LIMIT 10;
