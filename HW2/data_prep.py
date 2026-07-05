"""
MemeTracker -> domain-level hyperlink network preparation.

Reads a MemeTracker quotes file (e.g. quotes_2009-04.txt.gz), which is a
stream of blocks like:

    P   <url of the post/page>
    T   <timestamp>
    Q   <quoted phrase>
    Q   <quoted phrase>
    L   <url this post links to>
    L   <url this post links to>

For every (P, L) pair inside a block we take an edge from the domain of P
(source) to the domain of L (target). Edges are aggregated across the whole
file into a weighted, self-loop-free, domain-level graph and written out as
a CSV of (source_domain, target_domain, weight).

Usage:
    python data_prep.py --input quotes_2009-04.txt.gz --output edges.csv
    python data_prep.py --input quotes_2009-04.txt.gz --output edges.csv --max-lines 2000000
"""

import argparse
import csv
import gzip
from collections import Counter
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


_VALID_HOST_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789.-")


def normalize_domain(url: str) -> str:
    """Lowercase host, strip a leading 'www.'. Returns '' if unparseable."""
    url = url.strip()
    if not url:
        return ""
    if "://" not in url:
        url = "http://" + url
    try:
        host = urlparse(url).netloc.lower()
    except ValueError:
        return ""
    if not host:
        return ""
    host = host.split("@")[-1]  # drop userinfo if present
    host = host.split(":")[0]  # drop port
    if host.startswith("www."):
        host = host[4:]
    if "." not in host or not set(host) <= _VALID_HOST_CHARS:
        return ""
    return host


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", errors="ignore")
    return open(path, mode="rt", encoding="utf-8", errors="ignore")


def parse_edges(path: Path, max_lines: Optional[int] = None) -> Counter:
    """Stream the file and accumulate (source_domain, target_domain) -> weight."""
    edge_weights = Counter()
    current_post_domain = None
    n_lines = 0
    n_edges_seen = 0

    with open_text(path) as fh:
        try:
            for line in fh:
                n_lines += 1
                if max_lines is not None and n_lines > max_lines:
                    break

                if not line or line[0] not in "PL" or "\t" not in line:
                    continue

                tag, _, value = line.partition("\t")
                value = value.strip()

                if tag == "P":
                    current_post_domain = normalize_domain(value)
                elif tag == "L":
                    if not current_post_domain:
                        continue
                    target_domain = normalize_domain(value)
                    if not target_domain or target_domain == current_post_domain:
                        continue
                    edge_weights[(current_post_domain, target_domain)] += 1
                    n_edges_seen += 1
        except (EOFError, OSError):
            # Truncated / partial .gz (e.g. a downloaded sample chunk) - keep
            # whatever was decoded successfully up to the cut-off point.
            pass

    print(f"Lines read: {n_lines:,} | raw P->L links kept: {n_edges_seen:,} "
          f"| unique domain edges: {len(edge_weights):,}")
    return edge_weights


def write_edges_csv(edge_weights: Counter, output_path: Path) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["source_domain", "target_domain", "weight"])
        for (source, target), weight in sorted(
            edge_weights.items(), key=lambda kv: kv[1], reverse=True
        ):
            writer.writerow([source, target, weight])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path,
                         help="Path to quotes_YYYY-MM.txt.gz (or plain .txt)")
    parser.add_argument("--output", required=True, type=Path,
                         help="Path to write the aggregated edges CSV")
    parser.add_argument("--max-lines", type=int, default=None,
                         help="Optional cap on lines read, for quick sampling")
    args = parser.parse_args()

    edge_weights = parse_edges(args.input, args.max_lines)
    write_edges_csv(edge_weights, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
