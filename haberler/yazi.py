"""Gunluk haber .md dosyasindan (gunluk-haberler formati) haberler/<slug>.html sayfasi uretir ve yazilar.json'un basina ekler.
Kullanim: python3 haberler/yazi.py <yazi.md> <slug> "<kisa ozet>"   ardindan: python3 haberler/olustur.py
.md formati: '# Baslik', 'Etiket: X · Tarih: YYYY-MM-DD veya "6 Kasım 2026" · Kapak: img/....jpg', '## Giriş A' (bu sitede giris),
govde '##' bolumleri; 'Size nasıl'/'nasıl yardımcı' iceren bolum iletisim kutusuna, '## Kaynaklar' alta gider. 'Giriş B/C' atlanir."""
import sys, re, json, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://smmmserkankaplan-cell.github.io/smmmserkankaplan/"
AYLAR = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
md_path, slug, summary = sys.argv[1], sys.argv[2], sys.argv[3]
text = pathlib.Path(md_path).read_text(encoding="utf-8")
title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
meta = re.search(r"^Etiket: (.+?) · Tarih: (.+?) · Kapak: (\S+)", text, re.M)
tag, date_s, cover = meta.group(1).strip(), meta.group(2).strip(), meta.group(3).strip()
m = re.match(r"(\d+) (\w+) (\d{4})", date_s)
date = f"{m.group(3)}-{AYLAR.index(m.group(2))+1:02d}-{int(m.group(1)):02d}" if m else date_s
sections = re.split(r"^## ", text, flags=re.M)[1:]
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"(https?://\S+)", r'<a href="\1">\1</a>', s)
def block(body):
    out, lst = [], None
    for line in body.strip().splitlines():
        line = line.rstrip()
        mo = re.match(r"(\d+)\. (.+)", line); mu = re.match(r"- (.+)", line)
        kind = "ol" if mo else "ul" if mu else None
        if lst and kind != lst: out.append(f"</{lst}>"); lst = None
        if kind and not lst: out.append(f"<{kind}>"); lst = kind
        if kind: out.append(f"<li>{inline((mo or mu).group(2 if mo else 1))}</li>")
        elif line: out.append(f"<p>{inline(line)}</p>")
    if lst: out.append(f"</{lst}>")
    return "\n".join(out)
lead, body, cta, src = "", [], "", []
for sec in sections:
    head, _, rest = sec.partition("\n"); head = head.strip()
    if head.startswith("Giriş A"): lead = rest.strip()
    elif re.match(r"Giriş [A-Z]\b", head): continue
    elif head.startswith("Kaynaklar"): src = re.findall(r"- (.+?): (https?://\S+)", rest)
    elif "yardımcı" in head or "yanınızdayız" in head:
        cta = "\n".join(l for l in rest.strip().splitlines() if l.strip() and not l.startswith("**") and not l.startswith("Ofis:"))
    else: body.append(f"<h2>{inline(head)}</h2>\n{block(rest)}")
url = f"{BASE}haberler/{slug}.html"
desc = (summary + " İzmir Karşıyaka mali müşavir: 0532 515 50 35")[:300]
ld = json.dumps({"@context":"https://schema.org","@type":"Article","headline":title,"datePublished":date,"dateModified":date,"image":BASE+cover,"inLanguage":"tr","author":{"@type":"Person","name":"SMMM Serkan Kaplan"},"publisher":{"@type":"AccountingService","name":"Serkan Kaplan Mali Müşavirlik","telephone":"+90 532 515 50 35","address":{"@type":"PostalAddress","streetAddress":"Karşıyaka Tower, Bahçelievler Mah. 1831/14 Sok. No:12/1","addressLocality":"Karşıyaka","addressRegion":"İzmir","addressCountry":"TR"},"url":BASE},"mainEntityOfPage":url}, ensure_ascii=False)
e = lambda s: html.escape(s)
wa = "https://wa.me/905325155035?text=" + __import__("urllib.parse").parse.quote(f"Merhaba, '{title}' yazınız hakkında bilgi almak istiyorum.")
srchtml = " · ".join(f'<a href="{u}">{e(n)}</a>' for n, u in src)
page = f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | Mali Müşavir Serkan Kaplan</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow">
<meta property="og:type" content="article">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(summary)}">
<meta property="og:image" content="{BASE}{cover}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#071B2C">
<link rel="icon" href="../img/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Manrope:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="../"><b>SERKAN KAPLAN</b><small>SMMM · İzmir Karşıyaka Mali Müşavir</small></a>
  <a class="call" href="tel:+905325155035">📞 0532 515 50 35</a>
</div></header>
<main class="wrap">
  <p style="margin-top:22px;font-size:15px"><a href="../">Ana sayfa</a> › <a href="./">Bizden Haberler</a></p>
  <span class="meta">{e(tag)} · <time datetime="{date}">{e(date_s if m else date)}</time></span>
  <h1>{e(title)}</h1>
  <p class="lead">{inline(lead)}</p>
  <img class="cover" src="../{cover}" alt="{e(title)} yazısının kapak fotoğrafı, Serkan Kaplan Mali Müşavirlik ofisi" width="1200" height="800">
{chr(10).join(body)}
  <div class="cta">
    <h2>Bu konuda yanınızdayız</h2>
    <p>{inline(cta)}</p>
    <a class="phone" href="tel:+905325155035">0532 515 50 35</a>
    <p>Hemen arayın veya WhatsApp'tan yazın, ön görüşme ücretsiz.</p>
    <div class="row">
      <a href="{e(wa)}">WhatsApp'tan yaz</a>
      <a class="ghost" href="tel:+902325030030">Ofis: 0232 503 00 30</a>
      <a class="ghost" href="mailto:serkan@serkankaplan.com.tr">E-posta</a>
    </div>
  </div>
  <p class="src"><b>Kaynaklar:</b> {srchtml}. Bu yazı genel bilgilendirme amaçlıdır; kendi durumunuz için bizimle görüşün.</p>
</main>
<footer><div class="wrap">© {date[:4]} Serkan Kaplan Mali Müşavirlik · Karşıyaka Tower, Bahçelievler Mah. 1831/14 Sok. No:12/1, Karşıyaka/İzmir · <a href="tel:+905325155035">0532 515 50 35</a> · <a href="../">Ana sayfa</a></div></footer>
</body>
</html>
'''
(ROOT/f"haberler/{slug}.html").write_text(page, encoding="utf-8")
jp = ROOT/"haberler/yazilar.json"; L = json.loads(jp.read_text(encoding="utf-8"))
L = [p for p in L if p["slug"] != slug]
L.insert(0, {"slug": slug, "date": date, "tag": tag, "title": title, "summary": summary, "image": cover})
jp.write_text(json.dumps(L, ensure_ascii=False, indent=1), encoding="utf-8")
print("yazildi:", url)
