#!/usr/bin/env python3
"""Vérifie le site avant publication : python check.py
Erreurs = bloquant (code de sortie 1). Avertissements = à regarder.
"""
import json, os, re, sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
errors, warnings = [], []


def host_ok(url, domain):
    try:
        h = urlparse(url).hostname or ""
        return url.startswith("https://") and (h == domain or h.endswith("." + domain))
    except ValueError:
        return False


try:
    with open(os.path.join(ROOT, "models.json"), encoding="utf-8") as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    print(f"ERREUR  models.json invalide, ligne {e.lineno} col {e.colno} : {e.msg}")
    print("        (cause fréquente : virgule en trop après le dernier élément)")
    sys.exit(1)

profile = data.get("profile", {})
for key, domain in (("makerworld", "makerworld.com"), ("instagram", "instagram.com")):
    url = profile.get(key, "")
    if not url:
        warnings.append(f"profile.{key} vide : le lien sera masqué")
    elif "YOUR_HANDLE" in url:
        errors.append(f"profile.{key} contient encore YOUR_HANDLE")
    elif not host_ok(url, domain):
        errors.append(f"profile.{key} ne pointe pas vers https://{domain}")

cat_ids = []
for c in data.get("categories", []):
    cid = c.get("id", "") if isinstance(c, dict) else ""
    if not cid or not c.get("label"):
        errors.append(f"catégorie mal définie : {c} (id et label obligatoires)")
    elif not re.fullmatch(r"[a-z0-9-]+", cid):
        errors.append(f"catégorie « {cid} » : id en minuscules, chiffres et tirets uniquement")
    elif cid in cat_ids:
        errors.append(f"catégorie « {cid} » définie deux fois")
    else:
        cat_ids.append(cid)

models = data.get("models", [])
for cid in cat_ids:
    if not any(cid in (m.get("categories") or []) for m in models):
        warnings.append(f"catégorie « {cid} » sans modèle : le filtre sera masqué")
if not models:
    warnings.append("aucun modèle : la galerie affichera un message d'attente")

seen_ids = set()
for i, m in enumerate(models, 1):
    tag = f"modèle {i} « {m.get('title', '?')} »"
    for req in ("title", "makerworld"):
        if not m.get(req):
            errors.append(f"{tag} : champ « {req} » manquant")
    mid = m.get("id")
    if not mid:
        warnings.append(f"{tag} : pas d'« id », le lien direct ?model=… ne sera pas possible")
    elif not re.fullmatch(r"[a-z0-9-]+", mid):
        errors.append(f"{tag} : id « {mid} » en minuscules, chiffres et tirets uniquement")
    elif mid in seen_ids:
        errors.append(f"{tag} : id « {mid} » déjà utilisé")
    else:
        seen_ids.add(mid)
    mc = m.get("categories") or []
    if cat_ids and not mc:
        warnings.append(f"{tag} : aucune catégorie, visible seulement dans « All »")
    for cid in mc:
        if cid not in cat_ids:
            errors.append(f"{tag} : catégorie « {cid} » inconnue (définis-la dans \"categories\")")

    # photos : "images": [{"src", "caption"}] (ou l'ancien champ "image")
    imgs = m.get("images")
    if imgs is None and m.get("image"):
        imgs = [{"src": m["image"]}]
    if not imgs:
        errors.append(f"{tag} : aucune photo (champ « images »)")
        imgs = []
    for k, im in enumerate(imgs, 1):
        src = im.get("src", "") if isinstance(im, dict) else ""
        if not src:
            errors.append(f"{tag} : photo {k} sans « src »")
            continue
        if src.startswith("http"):
            if not host_ok(src, "makerworld.bblmw.com"):
                warnings.append(f"{tag} : photo {k} hébergée ailleurs que sur MakerWorld ({src[:50]}…)")
            continue
        path = os.path.join(ROOT, src)
        if not os.path.isfile(path):
            errors.append(f"{tag} : photo {k} introuvable ({src})")
            continue
        kb = os.path.getsize(path) / 1024
        if kb > 500:
            warnings.append(f"{tag} : photo {k} lourde ({kb:.0f} Ko), vise < 300 Ko")
        if os.path.basename(src).startswith("example-"):
            warnings.append(f"{tag} : photo d'exemple à remplacer")

    for s in m.get("specs") or []:
        if not (isinstance(s, list) and len(s) == 2):
            errors.append(f"{tag} : chaque ligne de « specs » doit être [\"Libellé\", \"Valeur\"]")
    for l in m.get("links") or []:
        if not (isinstance(l, dict) and l.get("label") and str(l.get("url", "")).startswith("https://")):
            errors.append(f"{tag} : lien mal formé dans « links » (label + url https)")
    mw = m.get("makerworld", "")
    if mw and not host_ok(mw, "makerworld.com"):
        errors.append(f"{tag} : lien MakerWorld invalide")
    elif re.search(r"/models/0000", mw):
        warnings.append(f"{tag} : lien MakerWorld d'exemple")
    ig = m.get("instagram")
    if ig and not host_ok(ig, "instagram.com"):
        errors.append(f"{tag} : lien Instagram invalide")
    if ig and ("XXXX" in ig or "YYYY" in ig):
        warnings.append(f"{tag} : lien Instagram d'exemple")
    d = m.get("date")
    if d and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        errors.append(f"{tag} : date au format AAAA-MM-JJ attendue")

with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
    if "YOUR-DOMAIN" in f.read():
        warnings.append("index.html : remplace YOUR-DOMAIN par ton domaine (aperçu des liens partagés)")

for w in warnings:
    print("ATTENTION ", w)
for e in errors:
    print("ERREUR    ", e)
print(f"\n{len(models)} modèle(s) · {len(errors)} erreur(s) · {len(warnings)} avertissement(s)")
sys.exit(1 if errors else 0)
