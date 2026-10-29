# 解析 Morningstar 匯出的 CSV（2026-10 起的新模板：1M/YTD/3M/6M/1Y/2Y/3Y 累積報酬＋3 年標準差＋2022–2025 年度報酬，附同類四分位/百分位）
# 每一欄的期間一律用第 8、9 列的起訖日判斷，不看標題（2026-10-28 OPIN 曾因只看標題抓錯 YTD）。
# 用法：python3 parse_ms_csv.py <csv...>  → 印出 JSON：{isin: {v, q, sd3y, asof, file}}
import csv, json, sys, datetime as dt

def d(s):
    try: y, m, dd = map(int, s.strip().split("/")); return dt.date(y, m, dd)
    except Exception: return None

def period(a, b):
    if not a or not b: return None
    if (a.month, a.day) == (1, 1) and (b.month, b.day) == (12, 31) and a.year == b.year: return "Y%d" % b.year
    if (a.month, a.day) == (1, 1) and a.year == b.year: return "YTD"
    # 月初到月底：月數 = 結束月 − 起始月 + 1
    if a.day == 1:
        mo = (b.year - a.year) * 12 + (b.month - a.month) + 1
        return {1: "1M", 3: "3M", 6: "6M", 12: "1Y", 24: "2Y", 36: "3Y", 60: "5Y", 120: "10Y"}.get(mo)
    return None

out = {}
for path in sys.argv[1:]:
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    hi = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Group/Investment")
    H = [c.replace("\n", " ").strip() for c in rows[hi]]
    st, en = rows[hi - 2], rows[hi - 1]
    title = rows[0][0].strip()
    cols, asof = {}, None
    for j, c in enumerate(H):
        if c.startswith("Return"):
            p = period(d(st[j]), d(en[j]))
            if not p: raise SystemExit(f"{path} 第 {j} 欄期間認不出：{st[j]}–{en[j]}")
            if p in cols: raise SystemExit(f"{path} 期間 {p} 重複")
            cols[p] = j
            if not p.startswith("Y"): asof = asof or en[j].strip()
            if not p.startswith("Y") and en[j].strip() != asof: raise SystemExit(f"{path} 截止日不一致")
    sdj = next((j for j, c in enumerate(H) if c.startswith("Std Dev")), None)
    num = lambda s: float(s) if s.strip() else None
    qj = {p: next(k for k in range(j + 1, len(H)) if H[k].startswith("Peer group")) for p, j in cols.items()}
    qkind = {p: ("pct" if "percentile" in H[qj[p]] else "q") for p in cols}
    for r in rows[hi + 1:]:
        if len(r) < 2 or not r[1].strip(): continue
        isin = r[1].strip()
        v = {p: (round(num(r[j]), 2) if num(r[j]) is not None else None) for p, j in cols.items()}
        q = {p: (int(float(r[qj[p]])) if r[qj[p]].strip() else None) for p in cols}
        out[isin] = {"v": {k: x for k, x in v.items() if x is not None}, "q": {k: x for k, x in q.items() if x is not None},
                     "sd3y": round(num(r[sdj]), 2) if sdj is not None and num(r[sdj]) is not None else None,
                     "qk": qkind, "asof": asof, "file": title, "name": r[0].strip()}
    print(path.split("/")[-1], title, asof, sorted(cols), file=sys.stderr)
json.dump(out, sys.stdout, ensure_ascii=False)
