import csv
from typing import List, Dict


def rows_to_csv(rows: List[Dict]) -> bytes:
    if not rows:
        return b""
    # Pick a stable set of columns for demo
    cols = ["id","name","title","current_company","previous_company","city","undergraduate_year","sector"]

    out = []
    for r in rows:
        out.append({k: r.get(k, "") for k in cols})
    from io import StringIO
    buf = StringIO()
    w = csv.DictWriter(buf, fieldnames=cols)
    w.writeheader()
    for r in out:
        w.writerow(r)
    return buf.getvalue().encode("utf-8")