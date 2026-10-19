#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur 100 % automatique du site « Explorateur Unicode ».

À CHAQUE exécution (en local ou dans GitHub Actions), ce script :
  1. détecte automatiquement l'URL du site (via GITHUB_REPOSITORY en CI,
     sinon http://localhost:8000/ pour l'aperçu local) ;
  2. génère output/data.json (base consommée par l'app de recherche) ;
  3. génère ~1 500 pages SEO (emoji/*.html) + 17 pages catégories ;
  4. génère sitemap.xml, robots.txt et ads.txt ;
  5. MET À JOUR AUTOMATIQUEMENT le bloc SEO de index.html et la section
     contact de mentions-legales.html (entre leurs marqueurs AUTO-*).

⚙️ CONFIGURATION : AUCUNE ! Tout est détecté automatiquement.
   Variables d'environnement OPTIONNELLES (à définir plus tard dans
   GitHub → Settings → Secrets and variables → Actions → Variables) :
     • SITE_URL ................ forcer une URL (ex. domaine personnalisé)
     • ADSENSE_ID .............. l'ID éditeur sans « ca-pub- » (36 chiffres)
                                 → injecte le script AdSense sur TOUTES les
                                   pages + remplit ads.txt automatiquement
     • GOOGLE_SITE_VERIFICATION  jeton de la Search Console
                                 → injecte la balise meta de vérification
                                 partout (méthode alternative au fichier HTML)

Aucune dépendance externe : bibliothèque standard Python uniquement.
La version d'Unicode suivie est celle du Python utilisé (3.13 → Unicode 15.1).
"""

import json
import os
import re
import unicodedata
from datetime import date
from html import escape as esc
from pathlib import Path
from string import Template

SITE_NAME = "Explorateur Unicode"
SITE_DESC = ("Explorez et copiez plus de 1 500 caractères Unicode et émojis : "
             "recherche par nom ou code U+, entités HTML, échappements CSS et "
             "JavaScript, encodage UTF-8. Mis à jour automatiquement.")
TODAY = date.today().isoformat()


# ---------------------------------------------------------------------------
# Détection automatique de la configuration
# ---------------------------------------------------------------------------
def detect_config():
    repo = os.environ.get("GITHUB_REPOSITORY", "")  # « compte/dépôt » en CI
    owner, name = repo.split("/", 1) if "/" in repo else ("", "")

    url = os.environ.get("SITE_URL", "").strip()
    if not url:
        if owner and name:
            url = (f"https://{owner}.github.io/"
                   if name.lower() == f"{owner.lower()}.github.io"
                   else f"https://{owner}.github.io/{name}/")
        else:
            url = "http://localhost:8000/"
    site_url = url.rstrip("/") + "/"

    repo_url = f"https://github.com/{repo}" if repo else "https://github.com/"
    adsense = re.sub(r"[^0-9]", "", os.environ.get("ADSENSE_ID", ""))
    verify = os.environ.get("GOOGLE_SITE_VERIFICATION", "").strip()
    source = ("variable SITE_URL" if os.environ.get("SITE_URL")
              else "GitHub Actions" if repo else "aperçu local")
    return site_url, repo_url, adsense, verify, source


SITE_URL, REPO_URL, ADSENSE_ID, GSC_TOKEN, URL_SOURCE = detect_config()

ADSENSE_HEAD = (
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/'
    f'adsbygoogle.js?client=ca-pub-{ADSENSE_ID}" crossorigin="anonymous">'
    f'</script>'
) if ADSENSE_ID else ""

VERIFY_META = (f'<meta name="google-site-verification" content="{GSC_TOKEN}">'
               if GSC_TOKEN else "")

# ---------------------------------------------------------------------------
# Définition des catégories : plages de points de code (inclusives).
# Ajoutez / retirez des plages librement pour personnaliser le catalogue.
# ---------------------------------------------------------------------------
CATEGORIES = [
    {"id": "smileys", "name": "Smileys & émotions", "icon": "\U0001F600",
     "ranges": [(0x1F600, 0x1F64F), (0x2639, 0x263A), (0x1F970, 0x1F976)]},
    {"id": "gestes", "name": "Gestes & mains", "icon": "\U0001F44B",
     "ranges": [(0x1F446, 0x1F450), (0x1F590, 0x1F596), (0x1F918, 0x1F91F),
                (0x270A, 0x270D), (0x261D, 0x261D)]},
    {"id": "personnes", "name": "Personnes", "icon": "\U0001F9D1",
     "ranges": [(0x1F466, 0x1F487), (0x1F9D1, 0x1F9DD)]},
    {"id": "animaux", "name": "Animaux & nature", "icon": "\U0001F436",
     "ranges": [(0x1F400, 0x1F443), (0x1F980, 0x1F99E), (0x1F330, 0x1F343),
                (0x1F300, 0x1F320), (0x2600, 0x2604), (0x26C4, 0x26C5)]},
    {"id": "nourriture", "name": "Nourriture & boissons", "icon": "\U0001F354",
     "ranges": [(0x1F32D, 0x1F32F), (0x1F345, 0x1F37F), (0x2615, 0x2615),
                (0x1F382, 0x1F382)]},
    {"id": "activites", "name": "Sports & activités", "icon": "\u26BD",
     "ranges": [(0x1F3AE, 0x1F3BC), (0x1F3C0, 0x1F3CF), (0x26BD, 0x26BE)]},
    {"id": "voyages", "name": "Voyage & lieux", "icon": "\u2708\uFE0F",
     "ranges": [(0x1F680, 0x1F6C5), (0x1F30D, 0x1F310), (0x1F5FA, 0x1F5FF),
                (0x1F3E0, 0x1F3F0)]},
    {"id": "objets", "name": "Objets", "icon": "\U0001F4A1",
     "ranges": [(0x1F4A0, 0x1F4FF), (0x1F50A, 0x1F514), (0x1F525, 0x1F52F),
                (0x231A, 0x231B), (0x23F0, 0x23F3)]},
    {"id": "symboles", "name": "Symboles", "icon": "\u2764\uFE0F",
     "ranges": [(0x1F493, 0x1F49F), (0x2764, 0x2764), (0x2665, 0x2665),
                (0x2622, 0x2626), (0x262E, 0x262F), (0x2648, 0x2653),
                (0x2705, 0x2705), (0x2714, 0x2716), (0x2728, 0x2728),
                (0x2733, 0x2734), (0x274C, 0x274C), (0x274E, 0x274E),
                (0x2753, 0x2755), (0x2757, 0x2757), (0x2795, 0x2797),
                (0x3030, 0x3030)]},
    {"id": "fleches", "name": "Flèches", "icon": "\u27A1\uFE0F",
     "ranges": [(0x2190, 0x21FF), (0x27A1, 0x27A1), (0x2B05, 0x2B07),
                (0x2934, 0x2935)]},
    {"id": "maths", "name": "Mathématiques", "icon": "\u2211",
     "ranges": [(0x2200, 0x22FF), (0x00B0, 0x00B0), (0x00B1, 0x00B1),
                (0x00B2, 0x00B3), (0x00D7, 0x00D7), (0x00F7, 0x00F7),
                (0x00BC, 0x00BE), (0x2030, 0x2030)]},
    {"id": "monnaies", "name": "Monnaies", "icon": "\U0001F4B6",
     "ranges": [(0x0024, 0x0024), (0x00A2, 0x00A5), (0x20A0, 0x20BF)]},
    {"id": "grec", "name": "Alphabet grec", "icon": "\u03B1",
     "ranges": [(0x0391, 0x03A9), (0x03B1, 0x03C9)]},
    {"id": "formes", "name": "Formes géométriques", "icon": "\u2B21",
     "ranges": [(0x25A0, 0x25FF), (0x2B50, 0x2B50), (0x2B55, 0x2B55),
                (0x2726, 0x2727)]},
    {"id": "cadres", "name": "Cadres & blocs", "icon": "\u259B",
     "ranges": [(0x2500, 0x257F), (0x2580, 0x259F)]},
    {"id": "cartes", "name": "Cartes à jouer", "icon": "\U0001F0A1",
     "ranges": [(0x1F0A1, 0x1F0AE), (0x2660, 0x2660), (0x2663, 0x2663),
                (0x2666, 0x2667)]},
    {"id": "ponctuation", "name": "Ponctuation & typo", "icon": "\u203D",
     "ranges": [(0x2010, 0x2027), (0x2030, 0x2038), (0x203C, 0x2049),
                (0x00A7, 0x00A7), (0x00A9, 0x00A9), (0x00AB, 0x00AB),
                (0x00AE, 0x00AE), (0x00B6, 0x00B7), (0x00BB, 0x00BB),
                (0x2122, 0x2122)]},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def iter_characters(ranges):
    """Itère sur les caractères valides des plages données (dédoublonnés)."""
    seen = set()
    for start, end in ranges:
        for cp in range(start, end + 1):
            if cp in seen:
                continue
            seen.add(cp)
            char = chr(cp)
            try:
                name = unicodedata.name(char)
            except ValueError:
                continue  # non assigné ou contrôle
            if unicodedata.category(char).startswith(("C", "M")):
                continue  # contrôles / marques combinantes
            yield {"char": char, "code": f"U+{cp:04X}", "name": name}


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug or "caractere")[:60]


def char_filename(c):
    return f"{ord(c['char']):04x}-{slugify(c['name'])}.html"


def title_case(name):
    return name.title()


def char_formats(c):
    """Tous les formats copiables d'un caractère."""
    ch = c["char"]
    cp = ord(ch)
    hexu = f"{cp:X}"
    octets16 = ch.encode("utf-16-be")
    units = [f"{int.from_bytes(octets16[i:i + 2], 'big'):04X}"
             for i in range(0, len(octets16), 2)]
    js_units = "".join(f"\\u{u}" for u in units)
    js = f"\\u{{{hexu}}}   (ou {js_units})" if cp > 0xFFFF else js_units
    utf8 = " ".join(f"{b:02X}" for b in ch.encode("utf-8"))
    return [
        ("Caractère", ch),
        ("Point de code", f"{c['code']}   (décimal {cp})"),
        ("HTML (hexa)", f"&#x{hexu};"),
        ("HTML (décimal)", f"&#{cp};"),
        ("CSS", f"\\{hexu.zfill(6)}"),
        ("JavaScript", js),
        ("UTF-8", utf8),
    ]


# ---------------------------------------------------------------------------
# Gabarits HTML (pages générées, autonomes, optimisées SEO)
# ---------------------------------------------------------------------------
PAGE_CHARS_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0e1117;color:#e8ecf4;line-height:1.5;
font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
a{color:#38bdf8}
.wrap{max-width:780px;margin:0 auto;padding:24px 20px 40px}
.crumbs{font-size:.82rem;color:#93a0b8;margin-bottom:18px}
.crumbs a{color:#93a0b8;text-decoration:none}.crumbs a:hover{color:#38bdf8}
.hero{display:flex;align-items:center;gap:22px;padding:24px;border-radius:16px;
background:linear-gradient(135deg,rgba(139,92,246,.18),rgba(56,189,248,.12));
border:1px solid #2a3450;margin-bottom:22px}
.hero .face{font-size:64px;line-height:1;
font-family:"Noto Color Emoji","Segoe UI Emoji","Apple Color Emoji",sans-serif}
h1{font-size:1.35rem;margin-bottom:4px}
.code{color:#a78bfa;font-family:ui-monospace,Consolas,monospace;font-size:.92rem}
.kv{display:grid;grid-template-columns:120px 1fr auto;align-items:center;gap:10px;
padding:10px 0;border-bottom:1px solid #1f2740}
.kl{color:#93a0b8;font-size:.8rem}
.kv2{font-family:ui-monospace,Consolas,monospace;font-size:.86rem;background:#1a2133;
padding:6px 10px;border-radius:8px;white-space:nowrap;overflow-x:auto}
.kb{padding:6px 12px;border-radius:8px;border:1px solid #2a3450;background:transparent;
color:#93a0b8;font-size:.78rem;cursor:pointer;font-family:inherit}
.kb:hover{color:#fff;border-color:#8b5cf6;background:rgba(139,92,246,.18)}
.kb.ok{color:#4ade80;border-color:#4ade80}
.meta{margin:22px 0;color:#93a0b8;font-size:.85rem}
.cta{display:inline-block;margin-top:10px;padding:10px 18px;border-radius:10px;
background:rgba(139,92,246,.16);border:1px solid rgba(139,92,246,.5);
color:#e8ecf4;text-decoration:none;font-size:.88rem}
.cta:hover{background:rgba(139,92,246,.3)}
.prevnext{display:flex;justify-content:space-between;gap:12px;margin:26px 0;
font-size:.85rem}
.prevnext a{color:#93a0b8;text-decoration:none}
.prevnext a:hover{color:#38bdf8}
h2{font-size:1rem;margin:28px 0 12px;color:#93a0b8;font-weight:600}
.rel{display:grid;grid-template-columns:repeat(auto-fill,minmax(52px,1fr));gap:8px}
.rc{display:flex;align-items:center;justify-content:center;aspect-ratio:1;
background:#1a2133;border:1px solid #2a3450;border-radius:10px;font-size:1.5rem;
text-decoration:none;transition:transform .12s,border-color .12s;
font-family:"Noto Color Emoji","Segoe UI Emoji","Apple Color Emoji",sans-serif}
.rc:hover{transform:translateY(-2px) scale(1.06);border-color:#8b5cf6}
footer{margin-top:40px;padding-top:16px;border-top:1px solid #1f2740;color:#93a0b8;
font-size:.78rem}
footer a{color:#93a0b8}
@media(max-width:560px){.kv{grid-template-columns:1fr}.kb{justify-self:start}
.hero .face{font-size:48px}h1{font-size:1.1rem}}
"""

TEMPLATE_CHAR = Template("""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$TITLE</title>
<meta name="description" content="$DESC">
<link rel="canonical" href="$CANONICAL">
<meta property="og:type" content="website">
<meta property="og:site_name" content="$SITE_NAME">
<meta property="og:title" content="$TITLE">
<meta property="og:description" content="$DESC">
<meta property="og:url" content="$CANONICAL">
<script type="application/ld+json">$JSONLD</script>
$VERIFY_META
$ADSENSE_HEAD
<style>$CSS</style>
</head>
<body>
<div class="wrap">
<nav class="crumbs" aria-label="Fil d'Ariane">
  <a href="../">Accueil</a> &rsaquo;
  <a href="../categorie/$CAT_ID.html">$CAT_NAME</a> &rsaquo;
  <span>$NAME_TITLE</span>
</nav>

<div class="hero">
  <div class="face" aria-hidden="true">$CHAR</div>
  <div>
    <h1>$CHAR $NAME_TITLE</h1>
    <div class="code">$CODE &middot; <a href="../categorie/$CAT_ID.html">$CAT_NAME</a></div>
  </div>
</div>

$ROWS

<div class="meta">
  <p>Caractère issu de la base Unicode $UNICODE. Page générée et mise à jour
  automatiquement, chaque jour, via GitHub&nbsp;Actions.</p>
  <a class="cta" href="../">&#128269; Explorer tous les caractères</a>
</div>

<nav class="prevnext">$PREV $NEXT</nav>

<h2>Autres caractères de la catégorie &laquo;&nbsp;$CAT_NAME&nbsp;&raquo;</h2>
<div class="rel">$RELATED</div>

<footer>
  <p><a href="../">$SITE_NAME</a> &middot; Données de caractères &copy;
  Unicode Consortium &middot; <a href="../mentions-legales.html">Mentions
  légales &amp; confidentialité</a> &middot; <a href="../sitemap.xml">Plan du site</a></p>
</footer>
</div>

<script>
function cp(btn){
  var t=btn.dataset.v;
  function ok(){var o=btn.textContent;btn.textContent="Copi\u00e9 \u2713";
    btn.classList.add("ok");
    setTimeout(function(){btn.textContent=o;btn.classList.remove("ok")},1200)}
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(t).then(ok)
  }else{
    var ta=document.createElement("textarea");ta.value=t;
    ta.style.position="fixed";ta.style.opacity="0";
    document.body.appendChild(ta);ta.select();document.execCommand("copy");
    ta.remove();ok()}}
</script>
</body>
</html>
""")

TEMPLATE_CAT = Template("""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$ICON $NAME &mdash; $COUNT caractères Unicode à copier | $SITE_NAME</title>
<meta name="description" content="Liste des $COUNT caractères Unicode de la catégorie $NAME : nom, point de code et copie en un clic (HTML, CSS, JavaScript, UTF-8).">
<link rel="canonical" href="$CANONICAL">
<meta property="og:type" content="website">
<meta property="og:site_name" content="$SITE_NAME">
<meta property="og:title" content="$NAME — $COUNT caractères Unicode">
<meta property="og:url" content="$CANONICAL">
<script type="application/ld+json">$JSONLD</script>
$VERIFY_META
$ADSENSE_HEAD
<style>$CSS
.intro{color:#93a0b8;font-size:.9rem;margin-bottom:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(78px,1fr));gap:8px}
.cell{display:flex;flex-direction:column;align-items:center;gap:4px;padding:10px 4px;
background:#1a2133;border:1px solid #2a3450;border-radius:10px;text-decoration:none;
transition:transform .12s,border-color .12s}
.cell:hover{transform:translateY(-2px);border-color:#8b5cf6}
.cell .fc{font-size:1.6rem;line-height:1;
font-family:"Noto Color Emoji","Segoe UI Emoji","Apple Color Emoji",sans-serif}
.cell .uc{font-size:.62rem;color:#93a0b8;font-family:ui-monospace,Consolas,monospace}
</style>
</head>
<body>
<div class="wrap">
<nav class="crumbs"><a href="../">Accueil</a> &rsaquo; <span>$NAME</span></nav>
<h1>$ICON $NAME <span class="code">($COUNT caractères)</span></h1>
<p class="intro">Cette page liste les <b>$COUNT caractères Unicode</b> de la catégorie
&laquo;&nbsp;$NAME&nbsp;&raquo;. Cliquez sur un caractère pour afficher son nom complet,
son point de code et tous ses formats de copie : entités HTML, échappements CSS et
JavaScript, encodage UTF-8.</p>
<div class="grid">$CELLS</div>
<footer>
  <p><a href="../">$SITE_NAME</a> &middot; Données &copy; Unicode Consortium &middot;
  <a href="../mentions-legales.html">Mentions légales</a> &middot;
  <a href="../sitemap.xml">Plan du site</a></p>
</footer>
</div>
</body>
</html>
""")


def build_rows(c):
    parts = []
    for label, value in char_formats(c):
        v_attr = esc(value, quote=True)
        v_html = esc(value)
        parts.append(
            f'<div class="kv"><span class="kl">{label}</span>'
            f'<code class="kv2">{v_html}</code>'
            f'<button class="kb" type="button" data-v="{v_attr}" '
            f'onclick="cp(this)">Copier</button></div>'
        )
    return "\n".join(parts)


def breadcrumb_jsonld(cat, c, canonical):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil",
             "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": cat["name"],
             "item": f"{SITE_URL}categorie/{cat['id']}.html"},
            {"@type": "ListItem", "position": 3, "name": title_case(c["name"]),
             "item": canonical},
        ],
    }, ensure_ascii=False)


def gen_char_pages(categories, out_dir):
    version = unicodedata.unidata_version
    n = 0
    for cat in categories:
        chars = cat["characters"]
        for i, c in enumerate(chars):
            fn = char_filename(c)
            canonical = f"{SITE_URL}emoji/{fn}"
            name_title = title_case(c["name"])

            prev_html = (
                f'<a rel="prev" href="../emoji/{char_filename(chars[i - 1])}">'
                f'&larr; {esc(chars[i - 1]["char"])} '
                f'{esc(title_case(chars[i - 1]["name"]))}</a>'
            ) if i > 0 else "<span></span>"

            next_html = (
                f'<a rel="next" href="../emoji/{char_filename(chars[i + 1])}">'
                f'{esc(title_case(chars[i + 1]["name"]))} '
                f'{esc(chars[i + 1]["char"])} &rarr;</a>'
            ) if i < len(chars) - 1 else "<span></span>"

            others = [x for x in chars if x is not c][:24]
            related = "".join(
                f'<a class="rc" href="../emoji/{char_filename(o)}" '
                f'title="{esc(o["name"], quote=True)} ({o["code"]})">'
                f'{esc(o["char"])}</a>'
                for o in others
            )

            desc = (f'Copiez le caractère {c["char"]} « {name_title} » '
                    f'({c["code"]}) : entités HTML, échappements CSS et '
                    f'JavaScript, encodage UTF-8. Catégorie {cat["name"]} '
                    f'· Unicode {version}.')

            page = TEMPLATE_CHAR.substitute(
                TITLE=esc(f'{c["char"]} {name_title} ({c["code"]}) — '
                          f'copier le caractère Unicode', quote=True),
                DESC=esc(desc, quote=True),
                CANONICAL=esc(canonical, quote=True),
                JSONLD=breadcrumb_jsonld(cat, c, canonical),
                SITE_NAME=SITE_NAME,
                VERIFY_META=VERIFY_META,
                ADSENSE_HEAD=ADSENSE_HEAD,
                CSS=PAGE_CHARS_CSS,
                CHAR=esc(c["char"]),
                NAME_TITLE=esc(name_title),
                CODE=c["code"],
                CAT_ID=cat["id"],
                CAT_NAME=esc(cat["name"]),
                ROWS=build_rows(c),
                UNICODE=version,
                PREV=prev_html,
                NEXT=next_html,
                RELATED=related,
            )
            (out_dir / fn).write_text(page, encoding="utf-8")
            n += 1
    return n


def gen_category_pages(categories, out_dir):
    n = 0
    for cat in categories:
        canonical = f"{SITE_URL}categorie/{cat['id']}.html"
        cells = "\n".join(
            f'<a class="cell" href="../emoji/{char_filename(c)}" '
            f'title="{esc(c["name"], quote=True)}">'
            f'<span class="fc">{esc(c["char"])}</span>'
            f'<span class="uc">{c["code"]}</span></a>'
            for c in cat["characters"]
        )
        jsonld = json.dumps({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f"{cat['name']} — {cat['count']} caractères Unicode",
            "url": canonical,
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        }, ensure_ascii=False)
        page = TEMPLATE_CAT.substitute(
            ICON=esc(cat["icon"]),
            NAME=esc(cat["name"]),
            COUNT=cat["count"],
            SITE_NAME=SITE_NAME,
            CANONICAL=esc(canonical, quote=True),
            JSONLD=jsonld,
            VERIFY_META=VERIFY_META,
            ADSENSE_HEAD=ADSENSE_HEAD,
            CSS=PAGE_CHARS_CSS,
            CELLS=cells,
        )
        (out_dir / f"{cat['id']}.html").write_text(page, encoding="utf-8")
        n += 1
    return n


def gen_sitemap(categories):
    urls = [
        (SITE_URL, "1.0", "daily"),
        (f"{SITE_URL}mentions-legales.html", "0.1", "yearly"),
    ]
    seen_chars = set()  # un caractère présent dans plusieurs catégories
                        # n'apparaît qu'une fois dans le sitemap
    for cat in categories:
        urls.append((f"{SITE_URL}categorie/{cat['id']}.html", "0.7", "weekly"))
        for c in cat["characters"]:
            fn = char_filename(c)
            if fn in seen_chars:
                continue
            seen_chars.add(fn)
            urls.append((f"{SITE_URL}emoji/{fn}", "0.6", "monthly"))

    body = []
    for loc, prio, freq in urls:
        loc = loc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body.append(
            f"  <url><loc>{loc}</loc>"
            f"<changefreq>{freq}</changefreq>"
            f"<priority>{prio}</priority></url>"
        )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(body) + "\n</urlset>\n")


def gen_ads_txt():
    if ADSENSE_ID:
        return f"google.com, pub-{ADSENSE_ID}, DIRECT, f08c47fec0942fa0\n"
    return ("# Fichier généré automatiquement par script.py.\n"
            "# Il sera rempli tout seul le jour où vous définirez la variable\n"
            "# ADSENSE_ID dans GitHub (Settings → Secrets and variables →\n"
            "# Actions → Variables). Rien d'autre à faire.\n")


# ---------------------------------------------------------------------------
# Mise à jour automatique des fichiers édités à la main (marqueurs AUTO-*)
# ---------------------------------------------------------------------------
def patch_block(path, marker, block):
    """Remplace le contenu entre <!-- AUTO-X:BEGIN --> et <!-- AUTO-X:END -->."""
    p = Path(path)
    if not p.exists():
        print(f"  ⚠️  {path} introuvable, bloc « {marker} » non patché")
        return False
    text = p.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"<!--\s*{re.escape(marker)}:BEGIN.*?{re.escape(marker)}:END\s*-->",
        re.S,
    )
    if not pattern.search(text):
        print(f"  ⚠️  marqueurs AUTO-{marker} absents de {path}")
        return False
    new = pattern.sub(lambda _m: block, text)
    if new != text:
        p.write_text(new, encoding="utf-8")
        return True
    return False


def patch_index():
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "WebSite",
        "name": SITE_NAME, "url": SITE_URL, "description": SITE_DESC,
    }, ensure_ascii=False)
    block = (
        "<!-- AUTO-SEO:BEGIN — régénéré à chaque build, ne pas éditer -->\n"
        f'  <link rel="canonical" href="{SITE_URL}">\n'
        '  <meta property="og:type" content="website">\n'
        f'  <meta property="og:site_name" content="{SITE_NAME}">\n'
        f'  <meta property="og:title" content="{esc(SITE_NAME)} — '
        f'copiez 1 500 caractères &amp; émojis">\n'
        f'  <meta property="og:description" content="{esc(SITE_DESC, quote=True)}">\n'
        f'  <meta property="og:url" content="{SITE_URL}">\n'
        '  <script type="application/ld+json">'
        f'{jsonld}</script>\n'
        + (f"  {VERIFY_META}\n" if VERIFY_META else "")
        + (f"  {ADSENSE_HEAD}\n" if ADSENSE_HEAD else "")
        + "  <!-- AUTO-SEO:END -->"
    )
    return patch_block("index.html", "AUTO-SEO", block)


def patch_mentions():
    block = (
        "<!-- AUTO-CONTACT:BEGIN — régénéré à chaque build, ne pas éditer -->\n"
        "    <p>\n"
        "      Ce site est édité à titre personnel et non professionnel par le\n"
        "      propriétaire du dépôt GitHub :\n"
        f'      <a href="{REPO_URL}">{REPO_URL}</a>.<br>\n'
        "      Conformément à l'article 6 III-2° de la loi n°&nbsp;2004-575\n"
        "      (LCEN), l'éditeur, personne physique, a choisi de ne pas rendre\n"
        "      publiques ses données personnelles.<br>\n"
        "      <b>Contact</b> : via l'onglet « Issues » du dépôt GitHub ci-dessus\n"
        "      (questions, droits RGPD, signalements).\n"
        "    </p>\n"
        "    <!-- AUTO-CONTACT:END -->"
    )
    return patch_block("mentions-legales.html", "AUTO-CONTACT", block)


# ---------------------------------------------------------------------------
# Génération principale
# ---------------------------------------------------------------------------
def main():
    print(f"URL du site : {SITE_URL}  (détectée : {URL_SOURCE})")
    print(f"Dépôt       : {REPO_URL}")
    print(f"AdSense     : {'activé (pub-' + ADSENSE_ID + ')' if ADSENSE_ID else 'désactivé'}")
    print(f"Vérification Search Console : {'active' if GSC_TOKEN else 'désactivée'}\n")

    # 1. Données -----------------------------------------------------------
    categories = []
    total = 0
    for cat in CATEGORIES:
        characters = list(iter_characters(cat["ranges"]))
        total += len(characters)
        categories.append({
            "id": cat["id"], "name": cat["name"], "icon": cat["icon"],
            "count": len(characters), "characters": characters,
        })
        print(f"  {cat['name']:<26} {len(characters):>5} caractères")

    out_json = Path("output")
    out_json.mkdir(exist_ok=True)
    data = {
        "meta": {
            "generated_at": f"{TODAY}T00:00:00+00:00",
            "unicode_version": unicodedata.unidata_version,
            "total": total,
        },
        "categories": categories,
    }
    (out_json / "data.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    # 2. Pages SEO ----------------------------------------------------------
    print("\nGénération des pages…")
    emoji_dir = Path("emoji")
    cat_dir = Path("categorie")
    emoji_dir.mkdir(exist_ok=True)
    cat_dir.mkdir(exist_ok=True)
    n_chars = gen_char_pages(categories, emoji_dir)
    n_cats = gen_category_pages(categories, cat_dir)

    # 3. Fichiers racine générés --------------------------------------------
    Path("sitemap.xml").write_text(gen_sitemap(categories), encoding="utf-8")
    Path("robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n",
        encoding="utf-8",
    )
    Path("ads.txt").write_text(gen_ads_txt(), encoding="utf-8")
    Path(".nojekyll").touch(exist_ok=True)  # GitHub Pages 100 % statique

    # 4. Patchs automatiques des fichiers statiques -------------------------
    ok_index = patch_index()
    ok_legal = patch_mentions()
    print(f"\nPatchs automatiques : index.html {'✔' if ok_index else '(déjà à jour)'} "
          f"· mentions-legales.html {'✔' if ok_legal else '(déjà à jour)'}")

    print(f"\n✅ {total} caractères · {n_chars} pages caractères · "
          f"{n_cats} pages catégories · sitemap.xml · robots.txt · ads.txt · "
          f"output/data.json (Unicode {unicodedata.unidata_version})")


if __name__ == "__main__":
    main()
