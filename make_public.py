# 把工作助手 fund-finder.html 轉成 GitHub Pages 公開版 index.html：
# 獨立 HTML 文件，只留基金競品／穩月配／績效比較，市場指標、彭博路徑、Outlook 資料來源不公開。
# 用法：python3 make_public.py <fund-finder.html> <index.html>
import json, re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
for v in ("mk", "bp", "ol"):
    s, n = re.subn(r'\s*<button class="tab"[^>]*data-view="%s"[^>]*>.*?</button>' % v, "", s)
    assert n == 1, v
m = re.search(r"const DATA = (\{.*?\});\n", s)
d = json.loads(m.group(1)); d["mk"] = d["bp"] = d["ol"] = []
s = s[:m.start(1)] + json.dumps(d, ensure_ascii=False) + s[m.end(1):]
# 公開版不開放直接跳到私人頁籤
s = s.replace('if (["funds", "div", "pf", "mk", "bp", "ol"].includes(location.hash.slice(1)))',
              'if (["funds", "div", "pf"].includes(location.hash.slice(1)))')
i = s.index("<title>"); j = s.index("</title>") + 8
head = '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
open(dst, "w", encoding="utf-8").write(head + s[i:j] + "\n</head>\n<body>\n" + s[:i] + s[j:] + "\n</body>\n</html>\n")
