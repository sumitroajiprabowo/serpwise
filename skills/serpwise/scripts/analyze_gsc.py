#!/usr/bin/env python3
"""Find the queries or pages that lost (and gained) the most in a Search Console export.

Stdlib only. Usage:
    python3 analyze_gsc.py queries.csv --metric clicks --top 20
    python3 analyze_gsc.py pages.csv --metric impressions --top 10

Reads the Queries.csv or Pages.csv file from a Performance report export made in
Compare mode. The first column is the query or page; each metric has one column
for the later period followed by one for the earlier period. For Position, a
lower number is better, so a rise in position counts as a drop.
"""

import argparse
import csv
import json


def load_gsc_csv(filepath):
    """Read a GSC Performance export CSV and return the header and data rows."""
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if not header:
            return [], []
        header = [h.strip() for h in header]
        for row in reader:
            if not row or not row[0].strip():
                continue
            rows.append([c.strip() for c in row])
    return header, rows


def find_metric_columns(header, metric):
    """Find the column indices for the given metric in both comparison periods."""
    metric_lower = metric.lower()
    indices = []
    for i, h in enumerate(header):
        if metric_lower in h.lower():
            indices.append(i)
    return indices


def parse_number(s):
    """Parse a number from a GSC export, ignoring thousands separators, '<' and '%'."""
    s = s.replace(",", "").replace("<", "").replace("%", "").strip()
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return 0


def analyze(filepath, metric="clicks", top_n=20):
    """Analyze a GSC CSV and return the top drops sorted by absolute change."""
    header, rows = load_gsc_csv(filepath)
    if not header or not rows:
        return {"error": "Empty or unreadable CSV", "results": []}

    indices = find_metric_columns(header, metric)
    if len(indices) < 2:
        return {
            "error": f"Could not find two columns for metric '{metric}'. Headers: {header}",
            "results": [],
        }

    # First metric column is the later period, second is the earlier period.
    col_later, col_earlier = indices[0], indices[1]
    results = []
    for row in rows:
        if len(row) <= max(col_later, col_earlier):
            continue
        dimension = row[0]
        val_later = parse_number(row[col_later])
        val_earlier = parse_number(row[col_earlier])
        change = val_later - val_earlier
        pct = (change / val_earlier * 100) if val_earlier else 0
        results.append(
            {
                "dimension": dimension,
                "current": val_later,
                "previous": val_earlier,
                "change": change,
                "change_pct": round(pct, 1),
            }
        )

    # Biggest drops first. For position a higher number is worse, so flip the sign.
    worse = (lambda r: -r["change"]) if metric.lower() == "position" else (lambda r: r["change"])
    top_drops = sorted(results, key=worse)[:top_n]
    top_gains = sorted(results, key=lambda r: -worse(r))[:top_n]

    return {
        "metric": metric,
        "total_rows": len(results),
        "top_drops": top_drops,
        "top_gains": top_gains,
        "summary": {
            "total_current": sum(r["current"] for r in results),
            "total_previous": sum(r["previous"] for r in results),
            "total_change": sum(r["change"] for r in results),
        },
    }


def print_report(data):
    """Print the analysis as a readable text report."""
    if data.get("error"):
        print("Error: " + data["error"])
        return
    print("# GSC {} Analysis".format(data["metric"].title()))
    s = data["summary"]
    pct = round(s["total_change"] / s["total_previous"] * 100, 1) if s["total_previous"] else 0
    print(
        "Total: {:,} -> {:,} ({:+,}, {:+.1f}%)".format(
            s["total_previous"], s["total_current"], s["total_change"], pct
        )
    )
    print("\n## Biggest Drops")
    print(
        "{:<60s} {:>10s} {:>10s} {:>10s} {:>8s}".format("Query/Page", "Previous", "Current", "Change", "Pct")
    )
    print("-" * 100)
    for r in data["top_drops"]:
        dim = r["dimension"][:58]
        print(
            "{:<60s} {:>10,} {:>10,} {:>+10,} {:>+7.1f}%".format(
                dim, r["previous"], r["current"], r["change"], r["change_pct"]
            )
        )
    print("\n## Biggest Gains")
    print(
        "{:<60s} {:>10s} {:>10s} {:>10s} {:>8s}".format("Query/Page", "Previous", "Current", "Change", "Pct")
    )
    print("-" * 100)
    for r in data["top_gains"]:
        dim = r["dimension"][:58]
        print(
            "{:<60s} {:>10,} {:>10,} {:>+10,} {:>+7.1f}%".format(
                dim, r["previous"], r["current"], r["change"], r["change_pct"]
            )
        )


def main():
    """Parse arguments and run the analysis."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_file", help="Path to a GSC Performance export CSV")
    ap.add_argument(
        "--metric",
        default="clicks",
        help="Metric to analyze: clicks, impressions, ctr, position (default: clicks)",
    )
    ap.add_argument("--top", type=int, default=20, help="Number of top drops/gains to show (default: 20)")
    ap.add_argument("--json", action="store_true", help="Output as JSON")
    a = ap.parse_args()
    data = analyze(a.csv_file, metric=a.metric, top_n=a.top)
    if a.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print_report(data)


if __name__ == "__main__":
    main()
