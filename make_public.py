# 把工作助手 fund-finder.html 轉成 GitHub Pages 公開版 index.html：
# 獨立 HTML 文件，只留基金競品／穩月配／績效比較，市場指標、彭博路徑、Outlook 資料來源、業績追蹤不公開。
# 用法：python3 make_public.py <fund-finder.html> <index.html>
import json, re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
for v in ("mk", "bp", "ol", "sl"):
    s, n = re.subn(r'\s*<button class="tab"[^>]*data-view="%s"[^>]*>.*?</button>' % v, "", s)
    assert n == 1 or (v == "sl" and n == 0), v  # 業績追蹤頁籤不一定在
m = re.search(r"const DATA = (\{.*?\});\n", s)
d = json.loads(m.group(1)); d["mk"] = d["bp"] = d["ol"] = []
s = s[:m.start(1)] + json.dumps(d, ensure_ascii=False) + s[m.end(1):]
# 公開版不開放直接跳到私人頁籤
s = s.replace('if (["funds", "div", "pf", "mk", "bp", "ol", "sl"].includes(location.hash.slice(1)))',
              'if (["funds", "div", "pf"].includes(location.hash.slice(1)))')
# 優勢總結、風險與報酬、配息穩定度（近 12 次、降配）先不公開（vivi 2026-10-23）
def cut(a, b, new=""):
    global s
    i = s.index(a); j = s.index(b, i) + len(b); s = s[:i] + new + s[j:]
cut('<div class="pfcard">\n      <div class="pfhead"><h2 id="sumtitle">', '<div class="legend" id="sumweak"></div>\n    </div>\n    ')
cut('<div class="pfcard">\n      <div class="pfhead"><h2 id="rrtitle">', '<div class="legend" id="rrnote"></div>\n    </div>\n    ')
for a, b in [('<th>近 12 次配息率</th><th>降配</th>', ''), ('<table style="min-width:1040px"><thead><tr><th>競品組', '<table><thead><tr><th>競品組'),
             ('「近 12 次配息率」與「降配」取自鉅亨網同一級別的配息紀錄；降配 = 每單位配息金額比前一次少。', ''),
             ('      ${divCells(f.zh)}\n', ''), ('colspan="8" class="empty">沒有符合的基金', 'colspan="6" class="empty">沒有符合的基金')]:
    assert s.count(a) == 1, a; s = s.replace(a, b)
m = re.search(r"const DIV = (\{.*?\});\n", s); s = s[:m.start(1)] + "{}" + s[m.end(1):]
# 業績是內部資料：業績追蹤的頁面和程式（含 SALES 資料）整段拿掉
if '<section id="v-sl"' in s:
    cut('  <section id="v-sl" hidden>', '</section>\n')
    cut('// 業績追蹤：', 'slOpts();\n')
i = s.index("<title>"); j = s.index("</title>") + 8
head = '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
open(dst, "w", encoding="utf-8").write(head + s[i:j] + "\n</head>\n<body>\n" + s[:i] + s[j:] + "\n</body>\n</html>\n")
