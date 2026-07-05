# HW2 — MemeTracker Domain Hyperlink Network (Neo4j GDS)

## Files

- `data_prep.py` — streams `quotes_YYYY-MM.txt.gz`, extracts `P`→`L`
  citations, normalizes domains, aggregates weighted edges, self-loop free.
- `cypher/01_constraints_and_import.cypher` — uniqueness constraint + `LOAD CSV` import.
- `cypher/02_graph_projection.cypher` — `gds.graph.project` (directed + undirected).
- `cypher/03_degree.cypher` … `09_louvain.cypher` — one file per metric (`gds.degree`,
  `gds.betweenness`, `gds.closeness`, `gds.eigenvector`, `gds.pageRank`,
  `gds.bridges`, `gds.louvain`), each writing the result back as a node/relationship
  property, plus a top-10 query.
- `cypher/10_visualization.cypher` — Neo4j Browser/Bloom queries (size by PageRank,
  color by Louvain community, bridges highlighted).
- `cypher/11_top10_comparison.cypher` — side-by-side top-10 table across all metrics
  + Louvain community summary.
- `data/edges.csv` — the processed (source_domain,target_domain,weight) edge list
  actually imported (induced subgraph on the top 300 domains by weighted degree,
  291 connected domains / 2,160 edges — see `ANALYSIS.md` for why).
- `data/domain_metrics.csv`, `data/domain_edges_bridges.csv` — snapshot of the
  computed centrality/community/bridge results, used by `app.py` so the Streamlit
  tab works standalone without a live Neo4j connection.
- `ANALYSIS.md` — interpretation of the results (hub vs. bridge vs. authority,
  what Louvain's communities reveal).
- `app.py` — Streamlit tab (auto-discovered by the root `main.py`).

## Reproducing from scratch

```bash
# 1. Download the full dataset (~2.7GB compressed)
curl -O https://snap.stanford.edu/data/bigdata/memetracker9/quotes_2009-04.txt.gz

# 2. Build the domain-level edge list
python data_prep.py --input quotes_2009-04.txt.gz --output edges_full.csv

# 3. Copy edges_full.csv (or a filtered/top-N subset - see ANALYSIS.md) into
#    Neo4j's import directory as edges.csv, then run the cypher/ files in order
#    (01 -> 11) in Neo4j Browser or cypher-shell, with the Graph Data Science
#    plugin installed.
```

This repo ships a pre-computed snapshot (`data/*.csv`) from an actual run of
this whole pipeline against a real Neo4j 5 + GDS instance, so `app.py` runs
without requiring a live database.
