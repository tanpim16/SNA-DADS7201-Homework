// =============================================================================
// 02. GDS in-memory graph projections
// =============================================================================
// GDS algorithms run against an in-memory "projected" graph, not directly
// against the stored database, so we must project it first with
// gds.graph.project(graphName, nodeProjection, relationshipProjection).
//
// We create TWO projections because some algorithms need different
// orientations of the same edges:
//   - domainGraph            : NATURAL (directed, A->B as stored) - used by
//                              degree / betweenness / closeness / eigenvector /
//                              pageRank, where link direction matters
//                              (who cites whom).
//   - domainGraphUndirected  : UNDIRECTED - required by gds.bridges (a bridge
//                              is a graph-theory concept defined on undirected
//                              graphs) and conventionally used for Louvain
//                              community detection, which groups nodes by
//                              mutual connectivity regardless of direction.
//
// `properties: 'weight'` carries the LINKS_TO.weight (citation count) into
// the projection so weighted variants of each algorithm can use it.

CALL gds.graph.project(
  'domainGraph',
  'Domain',
  {
    LINKS_TO: { orientation: 'NATURAL', properties: 'weight' }
  }
)
YIELD graphName, nodeCount, relationshipCount;

CALL gds.graph.project(
  'domainGraphUndirected',
  'Domain',
  {
    LINKS_TO: { orientation: 'UNDIRECTED', properties: 'weight' }
  }
)
YIELD graphName, nodeCount, relationshipCount;

// --- To free the in-memory projections when finished (does NOT touch the
// stored graph in the database - only drops the GDS working copy):
// CALL gds.graph.drop('domainGraph');
// CALL gds.graph.drop('domainGraphUndirected');
