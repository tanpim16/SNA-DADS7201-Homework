# MemeTracker Domain Hyperlink Network — Analysis

## Dataset & graph

Source: `quotes_2009-04.txt.gz` (SNAP MemeTracker9). `data_prep.py` streamed a
~400MB slice of the file (26.8M raw lines), extracted every `P` → `L`
citation, normalized hosts (lowercase, stripped `www.`), dropped self-loops,
and aggregated repeated citations into an edge weight. That pass alone
produced **323,793 unique domains and 617,979 weighted edges** — too large to
browse or lay out meaningfully in a single view. For the importable/visual
deliverable we took the induced subgraph on the **top 300 domains by weighted
degree** (the same "curated core" approach as HW1's SET50 subset), which
resolved to **291 connected domains and 2,160 edges** after intersection
filtering. All numbers below are from that graph, computed with real
`gds.*` calls against a local Neo4j 5 + GDS instance (see `cypher/`).

Louvain: **42 communities, modularity = 0.9054**.

## What each metric actually surfaced

**Degree** (weighted out-degree — how much a domain cites outward) topped
with `golivewire.com`, `mashget.com`, `articlesbase.com`,
`forums.hardwarezone.com` — high-volume blog/article aggregators and forums
that post a large number of outbound citations. This is a **hub** in the
"broadcasts a lot" sense. Notably, `en.wikipedia.org`, `news.google.com`, and
`craigslist.org` all show **degree = 0** here: in this dataset they were never
observed as the *source* of a post (`P`), only ever cited (`L`) — they are
pure sinks/targets, which is exactly why degree alone under-describes them.

**Betweenness** (how often a domain sits on the shortest path between two
others) told a completely different story: `us.rd.yahoo.com` (a Yahoo
redirect endpoint) and `tinyurl.com` (a URL shortener) ranked #1 and #2 —
ahead of any content site. This is a clean, intuitive result: link-shortening
and redirect infrastructure is *literally* the structural bridge connecting
otherwise unrelated blog communities, which is exactly what betweenness is
built to detect. `blog.wired.com`, `bbc.co.uk`, and `blog.livedoor.jp` follow,
i.e. syndication/media hubs that cross-link many smaller communities.

**Closeness** was dominated by several small, tightly-knit clusters
(`corruptlogic.com`, `students.sessions.edu`, several `*.craigslist.org`
regional mirrors) hitting the maximum score of 1.0. This is a direct
consequence of GDS's Wasserman–Faust normalization: closeness is normalized
by the size of each domain's *own* reachable component, so nodes in a small,
fully-reachable component score as "close to everything they can reach" even
though that reach is small — it does not by itself imply global importance,
only *local* reachability efficiency. This is a genuine and useful teaching
point about closeness on disconnected real-world graphs, not a data error.

**Eigenvector centrality did not converge** even at 1,000 iterations
(`didConverge: false`), a known failure mode on directed graphs with
dangling/sink nodes. The (non-converged) scores were dominated almost
entirely by a single reciprocal pair, `slickdeals.net` ↔
`forums.slickdeals.net`, which mutually cite each other densely — eigenvector
centrality's recursive "important nodes are cited by important nodes"
definition can get trapped amplifying a strongly-connected pair like this
instead of reflecting the whole graph. This is precisely the practical
problem **PageRank's damping factor solves**.

**PageRank**, in contrast, converged cleanly (87 iterations) and produced the
most intuitively correct **authority** ranking: `news.google.com`,
`en.wikipedia.org`, `youtube.com`, `bbc.co.uk`, `google.com`, `nytimes.com`,
`craigslist.org`, `edition.cnn.com` — exactly the reference/major-media sites
a 2009 blogosphere would cite constantly. Reading degree vs. PageRank
side-by-side is the clearest illustration in this dataset of **hub
(cites a lot) vs. authority (is cited by important sources)**: the two lists
barely overlap.

**Bridges** (53 edges whose removal disconnects the graph) reinforce the
betweenness finding: many bridge edges connect a small regional/topical
cluster to the rest of the graph through exactly one link, e.g.
`en.wikipedia.org ↔ marvel.wikia.com`, `d.hatena.ne.jp ↔ java.com`,
`feedproxy.google.com ↔ bloggar.se`. These are the single points of failure
in the network's connectivity — remove them and a whole regional/topical
sub-community goes dark from the rest of the graph.

## What Louvain reveals about community structure

Modularity of **0.9054** is very high, meaning the graph is strongly
partitioned into near-separate clusters rather than one blended mass — and
the clusters Louvain found are overwhelmingly explained by **language and
region**, not just topic:

| Community | Size | Representative domains |
|---|---|---|
| 190 | 74 | news.google.com, en.wikipedia.org, bbc.co.uk, news.bbc.co.uk, amazon.com — English-language global reference/media |
| 65  | 28 | youtube.com, twitter.com, search.twitter.com, online.wsj.com, washingtonpost.com — US media/social |
| 168 | 25 | nytimes.com, us.rd.yahoo.com, topix.net, sports.yahoo.com — US news/Yahoo ecosystem |
| 41  | 19 | d.hatena.ne.jp, b.hatena.ne.jp, blog.livedoor.jp, amazon.co.jp — **Japanese** blogosphere |
| 97  | 15 | news.google.de, bild.de, maerkischeallgemeine.de — **German** media |
| 17  | 10 | craigslist.org + its regional mirrors (newyork/sfbay/washingtondc/boston.craigslist.org) |
| 78  | 9  | edition.cnn.com, topics.cnn.com, cnn.com — CNN's own sub-domain cluster |
| 39  | 8  | globo.com, globoesporte.com, news.google.com.br — **Brazilian/Portuguese** media |

This is a strong, real finding: citation behavior in the blogosphere clusters
almost entirely along **language/regional lines** (Japanese sites cite
Japanese sites, German sites cite German sites, Craigslist's own regional
mirrors cite each other) rather than by topic alone. A few communities are a
single site's own subdomain family (CNN, Craigslist), which Louvain correctly
keeps together since they cite each other far more than they cite the outside
world.

## Summary: hub vs. bridge vs. authority

- **Hub** (degree): domains that *originate* a lot of citations — content
  aggregators and prolific bloggers (`golivewire.com`, `mashget.com`).
- **Bridge** (betweenness / `gds.bridges`): domains/edges that structurally
  connect otherwise separate regions of the network — often infrastructure,
  not content (`tinyurl.com`, `us.rd.yahoo.com`), or the single link keeping
  a niche cluster attached to the main graph.
- **Authority** (PageRank, and to a lesser/unstable extent eigenvector): domains
  that *receive* citations from other important domains — reference and major
  media sites (`en.wikipedia.org`, `bbc.co.uk`, `nytimes.com`).

No single centrality metric captures all three roles — which is exactly why
the assignment asks for all of them together.
