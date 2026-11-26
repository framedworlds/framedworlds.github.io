# Framed Worlds — site galerie

Un site statique : pas de base de données, pas de cookies, pas de traceurs.
La police est hébergée avec le site (aucun appel à Google Fonts).

```
index.html     la page d'accueil (textes du haut et métadonnées)
styles.css     couleurs et mise en page
app.js         construit la galerie à partir de models.json
models.json    ← le seul fichier à modifier au quotidien
models/<id>/   une page par modèle, générée (ne pas modifier à la main)
sitemap.xml    liste des pages pour Google, générée
robots.txt     autorise l'indexation et indique le sitemap
images/        photos des modèles (+ og.jpg : aperçu des partages, généré)
assets/        logo, favicon, image de partage de l'accueil, police
check.py       vérification avant publication
tools/         photos.py (préparation des photos), build_pages.py (pages modèles)
```

## Ajouter un modèle

Chaque modèle est un bloc dans `models.json`. Sur le site, il donne une carte (photo de couverture,
nombre de photos) ; un clic ouvre la fiche : galerie de toutes les photos (flèches, clavier, glissé
sur mobile, miniatures), description, caractéristiques et liens.

```json
{
  "id": "gothic-cathedral",
  "title": "Gothic Cathedral Facade",
  "collection": "Sacred Facades",
  "categories": ["bas-relief"],
  "description": "Une phrase d'accroche (affichée sur la carte).",
  "details": ["Premier paragraphe de la fiche.", "Deuxième paragraphe."],
  "specs": [
    ["Relief", "70 × 146 × 15 mm"],
    ["Print time", "≈ 6 h 53 min · 42 g · single colour"]
  ],
  "images": [
    {"src": "images/gothic-cathedral/01-cover.webp", "thumb": "images/gothic-cathedral/01-cover-sm.webp", "caption": "In its frame"},
    {"src": "images/gothic-cathedral/02-detail.webp", "caption": "Close-up"}
  ],
  "makerworld": "https://makerworld.com/en/models/3664967-…",
  "instagram": "https://www.instagram.com/p/ABC123/",
  "links": [{"label": "Frame & stand (separate free model)", "url": "https://makerworld.com/en/models/…"}],
  "tags": ["Cathedral", "Gothic"],
  "date": "2026-11-22"
}
```

- **Obligatoires** : `title`, `images` (au moins une) et `makerworld`. Tout le reste est optionnel :
  un champ absent n'est simplement pas affiché.
- **`id`** : en minuscules, avec des tirets. Il donne l'adresse de la page du modèle,
  par exemple `https://framedworlds.com/models/gothic-cathedral/` : c'est le lien à partager
  (bio Instagram, Reddit, forums), car il affiche un aperçu avec la photo et le titre du modèle.
  L'ancien lien `https://framedworlds.com/?model=gothic-cathedral` ouvre toujours la fiche sur l'accueil.
- **Photos** : la première sert de couverture (format 4:3 conseillé). Elles sont hébergées sur le site,
  dans **`images/<id>/`**, en deux tailles : `src` (1600 px, ~150 Ko) pour la galerie et `thumb`
  (800 px, ~40 Ko) pour les cartes et les miniatures. `thumb` est facultatif.
  Une adresse de photo MakerWorld fonctionne aussi : le site en demande alors une version allégée.
- **Préparer les photos d'un nouveau modèle** : `python tools/photos.py <dossier_des_photos> <id>`
  crée les deux tailles dans `images/<id>/` et affiche le bloc `"images"` à coller dans `models.json`
  (le premier fichier par ordre alphabétique sert de couverture ; ajuste les légendes si besoin).
- `caption` : la légende affichée sous la photo dans la galerie.
- Les modèles sont triés du plus récent au plus ancien d'après `date` ; à date égale, l'ordre du fichier est conservé.

## Catégories (filtres)

Elles sont définies une seule fois en haut de `models.json`, et les filtres s'affichent dans cet ordre :

```json
"categories": [
  {"id": "small", "label": "Small frame"},
  {"id": "medium", "label": "Medium frame"},
  {"id": "large", "label": "Large frame"},
  {"id": "bas-relief", "label": "Bas-relief"}
]
```

- `id` : en minuscules, sans espace (c'est ce que tu mets dans `"categories"` de chaque modèle).
- `label` : le texte affiché sur le site, modifiable librement.
- Un modèle peut avoir plusieurs catégories, par exemple `["large", "bas-relief"]`.
- Une catégorie sans modèle est masquée, et la barre de filtres n'apparaît qu'à partir de
  **deux catégories utilisées**.
- Chaque filtre a son propre lien, par exemple `https://framedworlds.com/?category=bas-relief`.

## Pages modèles (référencement Google)

Chaque modèle a sa propre page (`models/<id>/index.html`) avec un vrai titre, une description,
les photos et les caractéristiques : c'est ce que Google indexe et ce qui s'affiche quand on partage
le lien. Ces pages, leurs images de partage (`images/<id>/og.jpg`) et `sitemap.xml` sont **générés**
à partir de `models.json` :

```
python tools/build_pages.py
```

À relancer après **chaque** modification de `models.json` (nécessite Pillow : `pip install pillow`).
Si tu supprimes un modèle, supprime aussi son dossier `models/<id>/`.

## Vérifier avant de publier

Le cycle complet : modifier `models.json` → `python tools/build_pages.py` → `python check.py` → envoyer.

`check.py` signale le JSON cassé (virgule en trop), les champs obligatoires manquants, les `id`
en double, les photos introuvables ou trop lourdes, les liens mal formés, et les pages modèles
ou le sitemap qui ne sont plus à jour (dans ce cas : relance `build_pages.py`).

La langue du site est l'anglais (public international sur MakerWorld). Pour passer en français,
il suffit de modifier les textes dans `index.html`, les libellés de boutons dans `app.js` et le
gabarit des pages dans `tools/build_pages.py`.

## Aperçu en local

Un double-clic sur `index.html` ne charge pas la galerie (le navigateur bloque la lecture du JSON).
Lance plutôt un petit serveur depuis le dossier du site :

```
python -m http.server
```

puis ouvre http://localhost:8000

## Mise en ligne sur GitHub Pages (gratuit)

1. Crée un dépôt public sur GitHub, par exemple `framed-worlds`.
2. Envoie-y tout le contenu de ce dossier, à la racine du dépôt (glisser-déposer dans
   « Add file › Upload files » suffit).
3. Va dans **Settings › Pages** et choisis **Source : Deploy from a branch**,
   puis **Branch : main**, dossier **/ (root)**.
4. Au bout d'une minute environ, le site est en ligne sur `https://<ton-pseudo>.github.io/framed-worlds/`.

### Nom de domaine (optionnel, une dizaine d'euros par an)

1. Achète `framedworlds.com` ou `.fr` chez un registrar.
2. Dans **Settings › Pages › Custom domain**, saisis ton domaine, puis coche **Enforce HTTPS**
   quand l'option devient disponible.
3. Chez le registrar, crée les enregistrements DNS indiqués dans la documentation
   GitHub Pages (section « Managing a custom domain »).

Netlify et Cloudflare Pages fonctionnent aussi : il suffit de glisser-déposer le dossier, sans configuration.

## Règle MakerWorld à garder en tête

Le trafic va du site et d'Instagram **vers** MakerWorld. Ne mets pas l'adresse du site dans
tes descriptions de modèles : MakerWorld encadre les liens externes.

## Crédits

Police Cormorant SC, sous licence SIL Open Font License (`assets/fonts/OFL.txt`).
