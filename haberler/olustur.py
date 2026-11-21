"""Bizden Haberler liste sayfasini (haberler/index.html) ve sitemap.xml'i yazilar.json'dan yeniden uretir.
Yeni yazi: haberler/<slug>.html (baska sitedeki yazilar icin kayitta "url" alani olur, sitemap'e girmez) dosyasini ekle, yazilar.json'un basina kaydini yaz, sonra: python3 haberler/olustur.py"""
import json, html, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://smmmserkankaplan-cell.github.io/smmmserkankaplan/"
AYLAR = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
posts = sorted(json.loads((ROOT/"haberler/yazilar.json").read_text(encoding="utf-8")), key=lambda p: p["date"], reverse=True)
def tr(d):
    y, m, g = map(int, d.split("-")); return f"{g} {AYLAR[m-1]} {y}"
cards = "\n".join(f'''  <a class="card" href="{p.get("url") or p["slug"]+".html"}"><img src="{p["image"] if p["image"].startswith("http") else "../"+p["image"]}" alt="{html.escape(p.get('alt', ''))}" loading="lazy" width="1200" height="800"><div><span class="meta">{html.escape(p["tag"])} · <time datetime="{p["date"]}">{tr(p["date"])}</time></span><h3>{html.escape(p["title"])}</h3><p>{html.escape(p["summary"])}</p></div></a>''' for p in posts)
page = f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bizden Haberler: Vergi, SGK ve Mevzuat Rehberleri | İzmir Mali Müşavir Serkan Kaplan</title>
<meta name="description" content="Karşıyaka mali müşavir SMMM Serkan Kaplan'dan esnaf, şirketler ve sektörler için güncel vergi, SGK ve mevzuat yazıları. Ücretsiz ön görüşme: 0532 515 50 35">
<link rel="canonical" href="{BASE}haberler/">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#071B2C">
<link rel="icon" href="../img/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Manrope:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="../"><b>SERKAN KAPLAN</b><small>SMMM · İzmir Karşıyaka Mali Müşavir</small></a>
  <a class="call" href="tel:+905325155035">📞 0532 515 50 35</a>
</div></header>
<main class="wrap" style="max-width:980px">
  <p style="margin-top:22px;font-size:15px"><a href="../">Ana sayfa</a> › Bizden Haberler</p>
  <span class="meta">Bizden Haberler</span>
  <h1>Vergi, SGK ve mevzuat değişikliklerini sade bir dille anlatıyoruz</h1>
  <p class="lead">İzmir'de esnaf, şirketler ve farklı sektörler için güncel rehberler. Sorunuz varsa arayın: <a href="tel:+905325155035"><b>0532 515 50 35</b></a></p>
<div class="list">
{cards}
</div>
</main>
<footer><div class="wrap">© {datetime.date.today().year} Serkan Kaplan Mali Müşavirlik · Karşıyaka Tower, Karşıyaka/İzmir · <a href="tel:+905325155035">0532 515 50 35</a> · <a href="../">Ana sayfa</a></div></footer>
</body>
</html>
'''
(ROOT/"haberler/index.html").write_text(page, encoding="utf-8")
latest = posts[0]["date"] if posts else datetime.date.today().isoformat()
urls = [(BASE, latest), (BASE+"haberler/", latest)] + [(f'{BASE}haberler/{p["slug"]}.html', p["date"]) for p in posts if not p.get("url")]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls) + "\n</urlset>\n"
(ROOT/"sitemap.xml").write_text(sm, encoding="utf-8")
print(f"{len(posts)} yazi, sitemap {len(urls)} adres")

# Ana sayfa #haberler izgarasi: en yeni 6 yazi (2 blok: buyuk + 2 yan kart)
def link(p): return p.get("url") or f'haberler/{p["slug"]}.html'
def img(p): return p["image"] if p["image"].startswith("http") else p["image"]
def card(p, big):
    cls = "post big rv" if big else "post rv"
    para = f'\n        <p>{html.escape(p["summary"])}</p>' if big else ""
    return f'''<a class="{cls}" href="{link(p)}">
        <img class="bg" src="{img(p)}" alt="{html.escape(p.get('alt', p['tag'] + ' yazısının kapak görseli'))}" loading="lazy" decoding="async" style="width:100%;height:100%;object-fit:cover">
        <span class="tag">{html.escape(p["tag"])}</span>
        <time datetime="{p["date"]}">{tr(p["date"])}</time>
        <h3>{html.escape(p["title"])}</h3>{para}
      </a>'''
top = posts[:6]
blocks = []
for i in range(0, len(top), 3):
    g = top[i:i+3]
    side = "\n      ".join(card(x, False) for x in g[1:])
    mb = ' style="margin-bottom:22px"' if i == 0 and len(top) > 3 else ""
    blocks.append(f'<div class="news"{mb}>\n      {card(g[0], True)}\n      <div class="news-side">\n      {side}\n      </div>\n    </div>')
ip = ROOT/"index.html"; s = ip.read_text(encoding="utf-8")
a, b = "<!-- HABERLER:BASLA (haberler/olustur.py uretir) -->", "<!-- HABERLER:BITIR -->"
i, j = s.index(a) + len(a), s.index(b)
s = s[:i] + "\n    " + "\n    ".join(blocks) + "\n    " + s[j:]
ip.write_text(s, encoding="utf-8")
print("ana sayfa izgarasi guncellendi")
