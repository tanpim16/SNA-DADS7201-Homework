import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="MemeTracker Domain Network", layout="wide", page_icon="🔗")

st.markdown("""
<style>
.metric-card { background: #f8fafc; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.metric-value { font-size: 2rem; font-weight: 700; color: #7c3aed; }
.metric-label { font-size: 0.8rem; color: #64748b; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🔗 MemeTracker Domain Hyperlink Network")
st.markdown(
    "<p style='color:#64748b;margin-top:-12px;'>Domain-level hyperlink graph built from "
    "SNAP MemeTracker (quotes_2009-04) P&rarr;L citations, analyzed end-to-end in Neo4j "
    "GDS: degree, betweenness, closeness, eigenvector, PageRank, bridges and Louvain "
    "communities.</p>",
    unsafe_allow_html=True,
)

# ── DATA ─────────────────────────────────────────────────────────────────────

METRIC_LABELS = {
    "degree": "Degree",
    "betweenness": "Betweenness",
    "closeness": "Closeness",
    "eigenvector": "Eigenvector",
    "pagerank": "PageRank",
}

MODULARITY = 0.9054  # gds.louvain result on the imported demo graph (see ANALYSIS.md)


@st.cache_data
def load_data():
    nodes = pd.read_csv("data/domain_metrics.csv")
    edges = pd.read_csv("data/domain_edges_bridges.csv")
    return nodes, edges


nodes_df, edges_df = load_data()

community_sizes = nodes_df.groupby("community").size().sort_values(ascending=False)
top_community_ids = list(community_sizes.index)

# ── SESSION STATE / SIDEBAR ──────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🔍 Filters")
    community_options = ["All"] + [str(c) for c in top_community_ids]
    sel_community = st.selectbox("Louvain community", community_options)
    min_pagerank = st.slider("Min PageRank", 0.0, float(nodes_df["pagerank"].max()), 0.0, 0.05)
    only_bridges = st.checkbox("Show only bridge edges", value=False)
    layout_labels = {
        "spring": "🌐 Spring (กระจายอิสระ)",
        "circular": "⭕ Circular (วงกลม)",
        "kamada_kawai": "🔷 Balanced (สมดุล)",
    }
    layout_type = st.selectbox(
        "Layout", list(layout_labels.keys()), format_func=lambda x: layout_labels[x]
    )

    st.divider()
    st.markdown("### ℹ️ Legend")
    st.markdown("""
<div style='font-size:12.5px;line-height:2;color:#374151'>
<b style='color:#1e293b'>🔵 วงกลม = โดเมน</b><br>
<span style='color:#64748b'>
&nbsp;• <b>ขนาด</b> = PageRank (authority)<br>
&nbsp;• <b>สี</b> = Louvain community
</span>
<div style='border-top:1px solid #e2e8f0;margin:6px 0'></div>
<b style='color:#dc2626'>เส้นสีแดง = Bridge</b><br>
<span style='color:#64748b'>เอ็จที่เอาออกแล้วเครือข่ายจะขาดจากกัน</span>
</div>
""", unsafe_allow_html=True)

# ── FILTER ────────────────────────────────────────────────────────────────

fn = nodes_df.copy()
if sel_community != "All":
    fn = fn[fn["community"] == int(sel_community)]
fn = fn[fn["pagerank"] >= min_pagerank]
keep_names = set(fn["domain"])

fe = edges_df[edges_df["source"].isin(keep_names) & edges_df["target"].isin(keep_names)]
if only_bridges:
    fe = fe[fe["is_bridge"]]

# ── GRAPH BUILD ──────────────────────────────────────────────────────────

def build_graph(node_rows: pd.DataFrame, edge_rows: pd.DataFrame) -> nx.DiGraph:
    G = nx.DiGraph()
    for row in node_rows.itertuples():
        G.add_node(
            row.domain, degree=row.degree, betweenness=row.betweenness,
            closeness=row.closeness, eigenvector=row.eigenvector,
            pagerank=row.pagerank, community=row.community,
        )
    for row in edge_rows.itertuples():
        if row.source in G.nodes and row.target in G.nodes:
            G.add_edge(row.source, row.target, weight=row.weight, is_bridge=row.is_bridge)
    return G


G = build_graph(fn, fe)

COMMUNITY_PALETTE = [
    "#7C3AED", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444", "#EC4899",
    "#8B5CF6", "#14B8A6", "#F97316", "#3B82F6", "#84CC16", "#F43F5E",
]


def community_color(cid):
    return COMMUNITY_PALETTE[hash(str(cid)) % len(COMMUNITY_PALETTE)]


def draw_network(G: nx.DiGraph, layout_type="spring"):
    if G.number_of_nodes() == 0:
        return None

    if layout_type == "spring":
        pos = nx.spring_layout(G, k=1.2, iterations=100, seed=42)
    elif layout_type == "circular":
        pos = nx.circular_layout(G)
    else:
        pos = nx.kamada_kawai_layout(G)

    fig = go.Figure()

    # normal edges
    ex, ey = [], []
    bx, by = [], []
    for u, v, data in G.edges(data=True):
        xu, yu = pos[u]
        xv, yv = pos[v]
        if data.get("is_bridge"):
            bx.extend([xu, xv, None])
            by.extend([yu, yv, None])
        else:
            ex.extend([xu, xv, None])
            ey.extend([yu, yv, None])

    if ex:
        fig.add_trace(go.Scattergl(
            x=ex, y=ey, mode="lines",
            line=dict(width=0.6, color="#94a3b8"), opacity=0.35,
            hoverinfo="none", name="LINKS_TO", legendgroup="edges",
        ))
    if bx:
        fig.add_trace(go.Scattergl(
            x=bx, y=by, mode="lines",
            line=dict(width=2.2, color="#dc2626"), opacity=0.9,
            hoverinfo="none", name="Bridge", legendgroup="edges",
        ))

    pageranks = [d["pagerank"] for _, d in G.nodes(data=True)]
    max_pr = max(pageranks, default=1) or 1

    by_community = {}
    for n, d in G.nodes(data=True):
        by_community.setdefault(d["community"], []).append(n)

    for cid, members in by_community.items():
        sizes = [10 + 26 * (G.nodes[m]["pagerank"] / max_pr) for m in members]
        hover = [
            f"<b>{m}</b><br>Community: {cid}<br>"
            f"PageRank: {G.nodes[m]['pagerank']:.3f}<br>"
            f"Degree: {G.nodes[m]['degree']:.0f}<br>"
            f"Betweenness: {G.nodes[m]['betweenness']:.1f}<br>"
            f"Closeness: {G.nodes[m]['closeness']:.3f}<br>"
            f"Eigenvector: {G.nodes[m]['eigenvector']:.4f}"
            for m in members
        ]
        fig.add_trace(go.Scatter(
            x=[pos[m][0] for m in members], y=[pos[m][1] for m in members],
            mode="markers",
            marker=dict(size=sizes, color=community_color(cid),
                        line=dict(width=1, color="#1f2937"), opacity=0.9),
            hovertext=hover, hoverinfo="text",
            name=f"Community {cid}", legendgroup="communities",
            showlegend=False,
        ))

    fig.update_layout(
        showlegend=True, hovermode="closest",
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=700,
        legend=dict(font=dict(size=10, color="#374151"), bgcolor="rgba(255,255,255,0.92)",
                    bordercolor="#e2e8f0", borderwidth=1),
    )
    return fig


# ── KPI STRIP ────────────────────────────────────────────────────────────

n_domains = G.number_of_nodes()
n_edges = G.number_of_edges()
n_bridges = sum(1 for _, _, d in G.edges(data=True) if d.get("is_bridge"))
n_communities = len(set(nx.get_node_attributes(G, "community").values())) if n_domains else 0

k1, k2, k3, k4 = st.columns(4)
for col, val, label in [
    (k1, n_domains, "Domains"), (k2, n_edges, "Hyperlinks"),
    (k3, n_bridges, "Bridges"), (k4, n_communities, "Louvain communities"),
]:
    col.markdown(f"""
<div class='metric-card'>
  <div class='metric-value'>{val}</div>
  <div class='metric-label'>{label}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs(
    ["🕸️  Network Graph", "📋  Data Table", "📊  Centrality Comparison", "🧠  Analysis"]
)

with tab1:
    fig = draw_network(G, layout_type)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No domains match the current filters.")

with tab2:
    st.dataframe(
        fn.sort_values("pagerank", ascending=False),
        use_container_width=True, hide_index=True,
        column_config={
            "pagerank": st.column_config.ProgressColumn(
                "pagerank", format="%.3f", min_value=0,
                max_value=float(nodes_df["pagerank"].max())),
        },
    )
    st.caption(f"Bridge edges among current filter: {fe['is_bridge'].sum()} / {len(fe)}")
    st.dataframe(fe.sort_values("is_bridge", ascending=False), use_container_width=True, hide_index=True)

with tab3:
    col_a, col_b = st.columns(2)

    def top10_bar(metric, color):
        top = nodes_df.nlargest(10, metric)[["domain", metric]].iloc[::-1]
        fig = go.Figure(go.Bar(
            x=top[metric], y=top["domain"], orientation="h",
            marker=dict(color=top[metric], colorscale=[[0, "#ede9fe"], [1, color]], showscale=False),
            text=[f"{v:.3g}" for v in top[metric]], textposition="outside",
            textfont=dict(color="#374151", size=10),
        ))
        fig.update_layout(
            title=dict(text=f"<b>Top 10 by {METRIC_LABELS[metric]}</b>",
                       font=dict(color="#1e293b", size=13)),
            paper_bgcolor="white", plot_bgcolor="#fafafa",
            xaxis=dict(color="#9ca3af", gridcolor="#f1f5f9"),
            yaxis=dict(color="#374151", tickfont=dict(size=10)),
            height=360, margin=dict(l=10, r=60, t=45, b=20), showlegend=False,
        )
        return fig

    with col_a:
        st.plotly_chart(top10_bar("pagerank", "#7c3aed"), use_container_width=True)
        st.plotly_chart(top10_bar("betweenness", "#dc2626"), use_container_width=True)
        st.plotly_chart(top10_bar("closeness", "#0ea5e9"), use_container_width=True)
    with col_b:
        st.plotly_chart(top10_bar("degree", "#10b981"), use_container_width=True)
        st.plotly_chart(top10_bar("eigenvector", "#f59e0b"), use_container_width=True)

        comm_fig = go.Figure(go.Pie(
            labels=[f"Community {c}" for c in community_sizes.index[:10]],
            values=community_sizes.values[:10],
            marker=dict(colors=[community_color(c) for c in community_sizes.index[:10]]),
            hole=0.4,
        ))
        comm_fig.update_layout(
            title=dict(text="<b>Top 10 Louvain Communities (by size)</b>",
                       font=dict(color="#1e293b", size=13)),
            paper_bgcolor="white", height=360, margin=dict(l=10, r=10, t=45, b=20),
        )
        st.plotly_chart(comm_fig, use_container_width=True)

    st.divider()
    st.markdown(f"**Louvain modularity:** `{MODULARITY:.4f}` across **{len(community_sizes)}** communities "
                f"(computed by `gds.louvain.write` on the full domain graph).")

with tab4:
    try:
        with open("ANALYSIS.md", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.info("ANALYSIS.md not found.")
