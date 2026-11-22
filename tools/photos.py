#!/usr/bin/env python3
"""Prépare les photos d'un modèle pour le site.

    python tools/photos.py <dossier_des_photos> <id-du-modele>

Pour chaque JPG/PNG du dossier (ordre alphabétique, le premier = couverture) :
  images/<id>/<nom>.webp      1600 px, pour la galerie
  images/<id>/<nom>-sm.webp    800 px, pour les cartes et miniatures
puis affiche le bloc "images" à coller dans models.json.
Nécessite Pillow : pip install pillow
"""
import json, os, sys
from PIL import Image, ImageOps

if len(sys.argv) != 3:
    sys.exit(__doc__)
src, mid = sys.argv[1], sys.argv[2]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "images", mid)
os.makedirs(out, exist_ok=True)

def caption(stem):
    s = stem.lower()
    if "rendu" in s or "render" in s:
        return "3D render (unpainted)"
    if "contexte" in s or "context" in s:
        return "On display"
    return "Close-up"

block = []
files = sorted(f for f in os.listdir(src) if f.lower().endswith((".jpg", ".jpeg", ".png")))
for n, f in enumerate(files):
    im = ImageOps.exif_transpose(Image.open(os.path.join(src, f))).convert("RGB")
    stem = os.path.splitext(f)[0]
    for suffix, edge, q in (("", 1600, 80), ("-sm", 800, 74)):
        c = im.copy()
        c.thumbnail((edge, edge), Image.LANCZOS)
        c.save(os.path.join(out, stem + suffix + ".webp"), "WEBP", quality=q, method=6)
    block.append({"src": f"images/{mid}/{stem}.webp", "thumb": f"images/{mid}/{stem}-sm.webp",
                  "caption": "In its frame" if n == 0 else caption(stem)})
    print(f"ok  {f}")
print('\n"images": ' + json.dumps(block, ensure_ascii=False, indent=2))
