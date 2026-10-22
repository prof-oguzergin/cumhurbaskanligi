"""basinda.html sayfasini assets/data/basin.json'dan uretir.

Kullanim (depo kokunden):  python tools/basinda_uret.py
Ust bilgi, menu ve alt bilgi calismalar.html'den alinir; boylece site ile ayni kalir.
"""
import collections, html, json, pathlib, re

KOK = pathlib.Path(__file__).resolve().parent.parent
VERI = KOK / "assets" / "data" / "basin.json"
SABLON = KOK / "calismalar.html"
CIKTI = KOK / "basinda.html"

ADIN_GECTIGI = "Adının geçtiği haberler"
ONE_CIKAN = [  # (yayin organi basi, basliktan bir parca, rozet)
    ("Hürriyet", "Tecrübesini oyuna çevirdi", "Rektör Oldum"),
    ("DW Türkçe", "Savunma sanayisinde", "Beyin göçü"),
    ("Dünya Gazetesi", "Big Mac değil", "Tantuni Endeksi"),
    ("Milliyet", "yapay zekâ", "YÖK çalıştayı"),
    ("Türkiye Today", "scholars go dark", "YouTube yasağı"),
    ("EE Times", "Make Its Own Chips", "Yerli çip"),
]
AY = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
      "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
TUR = {"haber": "Haber", "röportaj": "Röportaj", "köşe yazısı": "Köşe yazısı",
       "kendi yazısı": "Kendi yazısı", "radyo": "Radyo", "podcast": "Podcast"}

e = lambda s: html.escape(str(s or ""), quote=True)


def tarih(d, p):
    if not d:
        return ""
    s = d.split("-")
    if p == "year" or len(s) == 1:
        return s[0]
    ay = AY[int(s[1]) - 1]
    if p == "month" or len(s) == 2:
        return f"{ay} {s[0]}"
    return f"{int(s[2])} {ay} {s[0]}"


def kimlik(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().translate(str.maketrans("çğıöşüâ", "cgiosua"))).strip("-")


def organ_kisa(o):
    return o.split(" (")[0].split(",")[0]


veri = json.loads(VERI.read_text(encoding="utf-8"))
asil = [d for d in veri if d.get("category") != ADIN_GECTIGI]
anilan = sorted([d for d in veri if d.get("category") == ADIN_GECTIGI], key=lambda d: d["date"], reverse=True)
yillar = collections.Counter(d["date"][:4] for d in asil if d.get("date"))
y0, y1 = int(min(yillar)), int(max(yillar))
gruplar = collections.defaultdict(list)
for d in sorted(asil, key=lambda d: d.get("date") or "", reverse=True):
    gruplar[d["category"]].append(d)
sira = sorted(gruplar, key=lambda c: -len(gruplar[c]))

FOTOLU = {"Hürriyet"}  # habere Oguz'un kendi verdigi portre kullanildi
INGILIZCE_AD = {"EE Times": "EE TIMES"}


def tr_buyuk(m):
    if m in INGILIZCE_AD:
        return INGILIZCE_AD[m]
    return m.replace("i", "İ").replace("ı", "I").upper()


kartlar = []
for i, (org, parca, rozet) in enumerate(ONE_CIKAN):
    d = next((x for x in asil if x["outlet"].startswith(org) and parca.lower() in x["title"].lower()), None)
    if not d:
        continue
    ad = organ_kisa(d["outlet"])
    foto = ('<figure class="k-foto"><img src="assets/img/basin-kupur-portre.jpg" alt="Oğuz Ergin" width="92" height="92" loading="lazy">'
            '<figcaption>Prof. Dr. Oğuz Ergin</figcaption></figure>' if ad in FOTOLU else "")
    kartlar.append(f'''  <a class="kupur k{len(kartlar) % 3}" href="{e(d["url"])}" target="_blank" rel="noopener">
    <span class="k-ust"><span class="k-organ">{e(tr_buyuk(ad))}</span></span>
    <span class="k-tarih">{e(tr_buyuk(tarih(d["date"], d["date_precision"])))} · {e(tr_buyuk(rozet))}</span>
    <span class="k-baslik">{e(d["title"])}</span>
    <span class="k-govde">{foto}<span class="k-satirlar"></span></span>
    <span class="k-git">Habere git →</span>
  </a>''')

tepe = max(yillar.values())
sutunlar = "".join(
    f'<div class="sutun"><span class="adet">{yillar.get(str(y), 0) or ""}</span>'
    f'<span class="cubuk" style="height:{yillar.get(str(y), 0) / tepe * 100:.0f}%"></span></div>'
    for y in range(y0, y1 + 1))
yil_etiket = "".join(f"<span>{y}</span>" for y in range(y0, y1 + 1))


def liste(kayitlar):
    return "".join(f'''
  <li><span class="t">{e(tarih(d["date"], d["date_precision"]))}</span>
    <span class="o">{e(d["outlet"])}<em>{e(TUR.get(d["type"], d["type"]))}</em></span>
    <a href="{e(d["url"])}" target="_blank" rel="noopener">{e(d["title"])}</a></li>''' for d in kayitlar)


bolumler = "".join(
    f'\n<h3 id="{kimlik(c)}">{e(c)} <small>{len(gruplar[c])}</small></h3>\n<ul class="basin-liste">{liste(gruplar[c])}\n</ul>\n'
    for c in sira)
dizin = " · ".join(f'<a href="#{kimlik(c)}">{e(c)}</a>' for c in sira)
anilan_html = (f'''
<h3 id="adinin-gectigi">{ADIN_GECTIGI}</h3>
<p class="not">Konusu ben olmayan, adımın yalnız bir listede ya da duyuruda geçtiği haberler.</p>
<ul class="basin-liste">{liste(anilan)}
</ul>''' if anilan else "")

STIL = """  <style>
    .haber-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.6rem 1.4rem;margin:1rem 0 .6rem;padding:6px 4px 12px}
    body.page main a.kupur{--kagit:#efece4;--murekkep:#22252b;position:relative;display:grid;gap:.5rem;align-content:start;padding:1rem 1.15rem 1.6rem;background:var(--kagit) repeating-linear-gradient(0deg,rgba(0,0,0,.018) 0 1px,transparent 1px 3px);color:var(--murekkep);text-decoration:none;font-weight:400;box-shadow:0 2px 3px rgba(15,32,55,.12),0 10px 22px rgba(15,32,55,.10);clip-path:polygon(0 0,100% 0,100% calc(100% - 8px),94% 100%,87% calc(100% - 6px),79% 100%,70% calc(100% - 7px),61% 100%,52% calc(100% - 5px),43% 100%,34% calc(100% - 8px),25% 100%,16% calc(100% - 6px),8% 100%,0 calc(100% - 7px));transition:transform .2s}
    body.page main a.kupur.k0{transform:rotate(-.8deg)} body.page main a.kupur.k1{transform:rotate(.6deg)} body.page main a.kupur.k2{transform:rotate(-.3deg)}
    body.page main a.kupur:hover{transform:rotate(0) translateY(-3px);color:var(--murekkep)}
    .kupur .k-ust{border-bottom:3px double var(--murekkep);padding-bottom:4px}
    .kupur .k-organ{font-family:Georgia,"Times New Roman",serif;font-weight:700;font-size:1.25rem;letter-spacing:.06em}
    .kupur .k-tarih{font-size:.66rem;letter-spacing:.12em;color:#5d5f63;border-bottom:1px solid rgba(0,0,0,.25);padding-bottom:5px}
    .kupur .k-baslik{font-family:Georgia,"Times New Roman",serif;font-weight:700;font-size:1.28rem;line-height:1.18;letter-spacing:-.01em;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:4;line-clamp:4;overflow:hidden}
    .kupur .k-govde{display:flex;gap:10px;align-items:flex-start}
    .kupur .k-foto{margin:0;flex:0 0 92px;display:grid;gap:3px}
    .kupur .k-foto img{width:92px;height:92px;object-fit:cover;filter:grayscale(1) contrast(1.15);mix-blend-mode:multiply;border-radius:0;box-shadow:none}
    .kupur .k-foto figcaption{font-size:.6rem;color:#5d5f63;font-style:italic;line-height:1.2;margin:0}
    .kupur .k-satirlar{flex:1;min-width:0;height:96px;background:repeating-linear-gradient(180deg,rgba(34,37,43,.30) 0 2px,transparent 2px 9px);-webkit-mask:linear-gradient(90deg,#000 47%,transparent 47% 53%,#000 53%),linear-gradient(180deg,#000 72%,transparent 100%);-webkit-mask-composite:source-in;mask-composite:intersect}
    .kupur .k-git{font-size:.8rem;font-weight:600;color:var(--c-primary-2)}
    p.kupur-not{color:var(--c-text-muted);font-size:.85rem}
    .yil-grafik{margin:1rem 0 .5rem}
    .yil-grafik .sutunlar{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));align-items:end;gap:4px;height:150px;border-bottom:1px solid var(--c-border)}
    .yil-grafik .sutun{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%;gap:3px;min-width:0}
    .yil-grafik .cubuk{width:100%;max-width:34px;background:var(--c-primary-2);border-radius:4px 4px 0 0}
    .yil-grafik .sutun:last-child .cubuk{background:var(--c-accent)}
    .yil-grafik .adet{font-size:.75rem;color:var(--c-text-muted)}
    .yil-grafik .yillar{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:4px;font-size:.72rem;color:var(--c-text-muted);text-align:center;margin-top:4px}
    .basin-liste{list-style:none;margin:0 0 1rem;padding:0;border-top:1px solid var(--c-border)}
    .basin-liste li{display:grid;grid-template-columns:125px minmax(0,1fr);column-gap:1rem;padding:.65rem 0;border-bottom:1px solid var(--c-border)}
    .basin-liste .t{grid-row:span 2;color:var(--c-text-muted);font-size:.88rem;padding-top:2px}
    .basin-liste .o{font-size:.85rem;color:var(--c-text-muted);font-weight:600}
    .basin-liste .o em{font-style:normal;font-weight:400;margin-left:.5rem}
    .basin-liste a{overflow-wrap:anywhere}
    body.page h3 small{font-size:.85rem;color:var(--c-text-muted);font-weight:500;margin-left:.4rem}
    p.not{color:var(--c-text-muted);font-size:.95rem}
    @media (max-width:560px){.basin-liste li{grid-template-columns:minmax(0,1fr)}.basin-liste .t{grid-row:auto}.yil-grafik .yillar span{writing-mode:vertical-rl;transform:rotate(180deg);justify-self:center}}
    @media (prefers-reduced-motion:reduce){body.page main a.kupur{transition:none}}
  </style>
"""

ANA = f"""<h1>Basında</h1>
<p>Hakkımda çıkan haberler, röportajlar, radyo yayınları ve yazdığım yazılar. Her kayıt, yayın organının kendi sayfasına bağlanır.</p>

<div class="stat-row">
  <div class="stat-card"><div class="stat-num">{len(asil)}</div><div class="stat-label">haber, röportaj ve yayın</div></div>
  <div class="stat-card"><div class="stat-num">{len({d["outlet"] for d in asil})}</div><div class="stat-label">yayın organı</div></div>
  <div class="stat-card"><div class="stat-num">{y0}</div><div class="stat-label">ilk kayıt</div></div>
  <div class="stat-card"><div class="stat-num">{len(sira)}</div><div class="stat-label">konu</div></div>
</div>

<h2 id="one-cikanlar">Öne çıkanlar</h2>
<div class="haber-grid">
{chr(10).join(kartlar)}
</div>
<p class="kupur-not">Kupürler haberlerin kendi görselleri değil, başlıklardan hazırladığım temsilî kesikler. Hürriyet kupüründeki fotoğraf, habere benim verdiğim portre.</p>

<h2 id="yillar">Yıllara göre</h2>
<div class="yil-grafik" style="--n:{y1 - y0 + 1}" role="img" aria-label="Yıllara göre haber sayısı">
  <div class="sutunlar">{sutunlar}</div>
  <div class="yillar">{yil_etiket}</div>
</div>

<h2 id="konular">Konulara göre</h2>
<p class="page-toc"><strong>Konular:</strong> {dizin}</p>
{bolumler}{anilan_html}

<hr>

<h2 id="basin-icin">Basın için</h2>
<p>Röportaj, bilgi notu ve yüksek çözünürlüklü fotoğraf için <a href="mailto:bilgi@oguzergin.net">bilgi@oguzergin.net</a> adresine yazabilirsiniz. Gözümden kaçan bir haber görürseniz de aynı adrese bildirmeniz beni sevindirir.</p>
"""

sablon = SABLON.read_text(encoding="utf-8")
bas = sablon[: sablon.index("<main>") + len("<main>")]
son = sablon[sablon.index("</main>"):]
ACIKLAMA = "Prof. Dr. Oğuz Ergin hakkında çıkan haberler, röportajlar, radyo yayınları ve yazılar; konulara göre."
bas = (bas.replace("<title>Çalışmalar · Prof. Dr. Oğuz Ergin</title>", "<title>Basında · Prof. Dr. Oğuz Ergin</title>")
          .replace('content="Çalışmalar · Prof. Dr. Oğuz Ergin"', 'content="Basında · Prof. Dr. Oğuz Ergin"')
          .replace("Akademik yayınlar, kitaplar, dersler, medya çıkışları ve açık kaynak projelerin tamamı.", ACIKLAMA)
          .replace("https://oguzergin.net/calismalar.html", "https://oguzergin.net/basinda.html"))
bas = bas.replace("</head>", STIL + "</head>", 1)
assert bas.count("basinda.html") == 2 and "Basında ·" in bas
CIKTI.write_text(bas + "\n" + ANA + son, encoding="utf-8", newline="\n")
print("basinda.html:", len(asil), "+", len(anilan))
