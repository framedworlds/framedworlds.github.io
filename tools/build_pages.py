#!/usr/bin/env python3
"""Génère une page HTML par modèle, son image de partage et le sitemap.

    python tools/build_pages.py

À relancer après chaque modification de models.json. Produit :
  models/<id>/index.html     page du modèle (titre, description, galerie, caractéristiques)
  images/<id>/og.jpg         image d'aperçu pour les partages (1200 × 630)
  sitemap.xml                accueil + toutes les pages modèles
Nécessite Pillow (pip install pillow). Fonttools est facultatif (police du titre sur og.jpg).
"""
import html, io, json, os, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://framedworlds.com"
e = lambda s: html.escape(str(s), quote=True)


def load():
    with open(os.path.join(ROOT, "models.json"), encoding="utf-8") as f:
        return json.load(f)


def safe_url(u):
    return u if isinstance(u, str) and u.startswith(("https://", "http://")) else None


def meta_description(m):
    text = " ".join([m.get("description", "")] + list(m.get("details") or [])).strip()
    text = " ".join(text.split())
    if len(text) > 155:
        text = text[:152].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return text


# ---------- share image ----------
def _font(size, weight="700"):
    from PIL import ImageFont
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(os.path.join(ROOT, "assets", "fonts", f"cormorant-sc-{weight}.woff2"))
        f.flavor = None
        buf = io.BytesIO(); f.save(buf); buf.seek(0)
        return ImageFont.truetype(buf, size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSerif.ttf", int(size * 0.8))
        except Exception:
            return ImageFont.load_default()


def og_path(m):
    """Chemin de l'image de partage, ou None si la couverture n'est pas hébergée sur le site."""
    imgs = m.get("images") or []
    if not imgs or not imgs[0].get("src") or imgs[0]["src"].startswith("http"):
        return None
    return "images/" + m["id"] + "/og.jpg"


def make_og(m):
    """1200 × 630: portrait crop of the cover on the left, title on the right."""
    from PIL import Image, ImageDraw, ImageOps
    out = og_path(m)
    if not out:
        return None
    imgs = m["images"]
    cover = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, imgs[0]["src"]))).convert("RGB")
    W, H, PAD = 1200, 630, 40
    ph = H - 2 * PAD; pw = round(ph * 4 / 5)
    w, h = cover.size; tw = round(h * 4 / 5)
    if tw <= w:
        x = (w - tw) // 2; cover = cover.crop((x, 0, x + tw, h))
    cover = cover.resize((pw, ph), Image.LANCZOS)
    og = Image.new("RGB", (W, H), (15, 20, 36))
    og.paste(cover, (PAD, PAD))
    d = ImageDraw.Draw(og)
    x0 = PAD + pw + 50; maxw = W - x0 - PAD
    gold, light, muted = (212, 175, 94), (255, 239, 191), (167, 163, 151)
    if m.get("collection"):
        d.text((x0, 120), m["collection"].upper(), font=_font(26, "600"), fill=gold)
    # title, wrapped, shrinking if needed
    size = 76
    while True:
        f = _font(size)
        words, lines, cur = m["title"].split(), [], ""
        for wd in words:
            test = (cur + " " + wd).strip()
            if d.textlength(test, font=f) <= maxw: cur = test
            else: lines.append(cur); cur = wd
        lines.append(cur)
        if len(lines) <= 3 or size <= 44: break
        size -= 6
    y = 165
    for ln in lines:
        d.text((x0, y), ln, font=f, fill=light); y += int(size * 1.08)
    d.line((x0, y + 20, x0 + maxw, y + 20), fill=(90, 78, 50), width=2)
    d.text((x0, y + 40), "Framed bas-relief to 3D print & paint", font=_font(30, "600"), fill=muted)
    d.text((x0, H - PAD - 40), "framedworlds.com", font=_font(30), fill=gold)
    og.save(os.path.join(ROOT, out), "JPEG", quality=86, optimize=True, progressive=True)
    return out


# ---------- page ----------
def page(m, data, others, year):
    mid, title = m["id"], m["title"]
    url = f"{SITE}/models/{mid}/"
    desc = meta_description(m)
    imgs = m.get("images") or []
    og = og_path(m)
    og_url = f"{SITE}/{og}" if og else f"{SITE}/assets/og-image.png"
    prof = data.get("profile", {})
    mw_prof, ig_prof = safe_url(prof.get("makerworld")), safe_url(prof.get("instagram"))
    mw, ig = safe_url(m.get("makerworld")), safe_url(m.get("instagram"))
    cats = {c["id"]: c["label"] for c in data.get("categories", []) if c.get("id")}
    tags = [(cats[c], True) for c in (m.get("categories") or []) if c in cats] + [(t, False) for t in (m.get("tags") or [])]

    def src(img, small=False):
        s = img.get("thumb") if small and img.get("thumb") else img["src"]
        return s if s.startswith("http") else "/" + s

    alt = lambda img: e(f"{title} — {img.get('caption', '')}".rstrip(" —"))
    gallery = ""
    if imgs:
        first = imgs[0]
        thumbs = "".join(
            f'<button type="button" data-full="{e(src(i))}" data-alt="{alt(i)}" data-caption="{e(i.get("caption", ""))}"'
            f'{" aria-current=\"true\"" if k == 0 else ""} aria-label="Photo {k + 1} of {len(imgs)}: {e(i.get("caption", ""))}">'
            f'<img src="{e(src(i, True))}" alt="" loading="lazy" decoding="async"></button>'
            for k, i in enumerate(imgs))
        gallery = f"""
      <div class="mp-gallery">
        <figure class="mp-stage">
          <img id="mp-main" src="{e(src(first))}" alt="{alt(first)}" width="1600" height="1200" decoding="async">
          <figcaption id="mp-caption">{e(first.get("caption", ""))}</figcaption>
        </figure>
        <div class="mp-thumbs">{thumbs}</div>
      </div>"""

    details = "".join(f"<p>{e(p)}</p>" for p in (m.get("details") or []))
    specs = "".join(f"<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>" for a, b in (m.get("specs") or []))
    tag_html = "".join(f'<li class="cat">{e(t)}</li>' if is_cat else f"<li>{e(t)}</li>" for t, is_cat in tags)
    actions = ""
    if mw: actions += f'<a class="btn btn-primary" href="{e(mw)}" target="_blank" rel="noopener">Download free on MakerWorld ↗</a>'
    if ig: actions += f'<a class="btn btn-ghost" href="{e(ig)}" target="_blank" rel="noopener">Instagram ↗</a>'
    links = "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])} ↗</a></li>'
                    for l in (m.get("links") or []) if safe_url(l.get("url")) and l.get("label"))
    more = "".join(
        f'<li><a href="/models/{e(o["id"])}/"><img src="{e(src(o["images"][0], True))}" alt="" loading="lazy" width="800" height="600">'
        f'<span>{e(o["title"])}</span></a></li>' for o in others if o.get("images"))
    ld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CreativeWork", "name": title, "description": desc, "url": url,
             "image": [SITE + src(i) for i in imgs[:3]],
             "creator": {"@type": "Organization", "name": "Framed Worlds", "url": SITE + "/"},
             **({"isPartOf": {"@type": "CreativeWorkSeries", "name": m["collection"]}} if m.get("collection") else {}),
             **({"sameAs": mw} if mw else {})},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Framed Worlds", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": title, "item": url}]}]}, ensure_ascii=False).replace("</", "<\\/")

    nav_mw = f'<a href="{e(mw_prof)}" target="_blank" rel="noopener">MakerWorld</a>' if mw_prof else ""
    nav_ig = f'<a href="{e(ig_prof)}" target="_blank" rel="noopener">Instagram</a>' if ig_prof else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Page générée par tools/build_pages.py à partir de models.json : ne pas modifier à la main -->
  <title>{e(title)} — framed bas-relief to 3D print &amp; paint | Framed Worlds</title>
  <meta name="description" content="{e(desc)}">
  <meta name="theme-color" content="#0F1424">
  <link rel="canonical" href="{e(url)}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Framed Worlds">
  <meta property="og:url" content="{e(url)}">
  <meta property="og:title" content="{e(title)} — Framed Worlds">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{e(og_url)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <link rel="preload" href="/assets/fonts/cormorant-sc-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/styles.css">
  <script type="application/ld+json">{ld}</script>
</head>
<body class="model-page">
  <header class="site-header">
    <a class="brand" href="/" aria-label="Framed Worlds — home">
      <img src="/assets/icon.svg" alt="" width="40" height="40">
      <span>Framed Worlds</span>
    </a>
    <nav aria-label="Main">
      <a href="/#models">Models</a>
      {nav_mw}
      {nav_ig}
    </nav>
  </header>

  <main class="mp">
    <p class="mp-back"><a href="/#models">← All worlds</a></p>
    <article class="mp-layout">{gallery}
      <div class="mp-info">
        {f'<p class="eyebrow">{e(m["collection"])}</p>' if m.get("collection") else ""}
        <h1>{e(title)}</h1>
        {f'<p class="lead">{e(m["description"])}</p>' if m.get("description") else ""}
        {details}
        {f'<dl class="specs">{specs}</dl>' if specs else ""}
        {f'<ul class="tags">{tag_html}</ul>' if tag_html else ""}
        {f'<div class="viewer-actions">{actions}</div>' if actions else ""}
        {f'<ul class="extra-links">{links}</ul>' if links else ""}
      </div>
    </article>
    {f'<section class="mp-more" aria-labelledby="more-title"><div class="section-head"><h2 id="more-title">More worlds</h2><span class="rule" aria-hidden="true"></span></div><ul>{more}</ul></section>' if more else ""}
  </main>

  <footer class="site-footer">
    <img src="/assets/icon.svg" alt="" width="28" height="28">
    <p>© {year} Framed Worlds · Models published on MakerWorld</p>
    <nav aria-label="Footer">{nav_mw}{nav_ig}</nav>
  </footer>

  <script>
  (function () {{
    var main = document.getElementById("mp-main"), cap = document.getElementById("mp-caption");
    var btns = [].slice.call(document.querySelectorAll(".mp-thumbs button"));
    var pos = 0;
    function show(i) {{
      if (!btns.length) return;
      pos = (i + btns.length) % btns.length;
      var b = btns[pos];
      main.src = b.getAttribute("data-full"); main.alt = b.getAttribute("data-alt");
      cap.textContent = b.getAttribute("data-caption");
      btns.forEach(function (x, k) {{ if (k === pos) x.setAttribute("aria-current", "true"); else x.removeAttribute("aria-current"); }});
    }}
    btns.forEach(function (b, k) {{ b.addEventListener("click", function () {{ show(k); }}); }});
    document.addEventListener("keydown", function (ev) {{
      if (ev.key === "ArrowRight") show(pos + 1);
      if (ev.key === "ArrowLeft") show(pos - 1);
    }});
    var x0 = null, stage = document.querySelector(".mp-stage");
    if (stage) {{
      stage.addEventListener("touchstart", function (ev) {{ x0 = ev.touches[0].clientX; }}, {{ passive: true }});
      stage.addEventListener("touchend", function (ev) {{
        if (x0 === null) return; var dx = ev.changedTouches[0].clientX - x0; x0 = null;
        if (Math.abs(dx) > 40) show(pos + (dx < 0 ? 1 : -1));
      }});
    }}
  }})();
  </script>
</body>
</html>
"""


def sitemap(models):
    today = date.today().isoformat()
    dates = [m.get("date") or today for m in models]
    urls = [(f"{SITE}/", max(dates, default=today))] + [(f"{SITE}/models/{m['id']}/", d) for m, d in zip(models, dates)]
    body = "".join(f"  <url>\n    <loc>{e(u)}</loc>\n    <lastmod>{d}</lastmod>\n  </url>\n" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def build(data):
    """Retourne {chemin relatif: contenu} pour toutes les pages + sitemap (utilisé aussi par check.py)."""
    models = [m for m in data.get("models", []) if m.get("id") and m.get("title")]
    dates = [m["date"] for m in models if m.get("date")]
    year = max(dates)[:4] if dates else str(date.today().year)
    files = {}
    for m in models:
        others = [o for o in models if o is not m]
        files[f"models/{m['id']}/index.html"] = page(m, data, others, year)
    files["sitemap.xml"] = sitemap(models)
    return models, files


def main():
    data = load()
    models, files = build(data)
    for rel, content in files.items():
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    for m in models:
        make_og(m)
        print(f"ok  models/{m['id']}/")
    out_dir = os.path.join(ROOT, "models")
    existing = os.listdir(out_dir) if os.path.isdir(out_dir) else []
    stale = sorted(set(existing) - {m["id"] for m in models})
    for s in stale:
        print(f"ATTENTION  models/{s}/ ne correspond plus à aucun modèle : supprime le dossier")
    print(f"{len(models)} page(s) + sitemap.xml")


if __name__ == "__main__":
    sys.exit(main())
