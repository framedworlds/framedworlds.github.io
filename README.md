# Framed Worlds — site galerie

Une seule page statique : pas de base de données, pas de cookies, pas de traceurs.
La police est hébergée avec le site (aucun appel à Google Fonts).

```
index.html     la page (textes du haut et métadonnées)
styles.css     couleurs et mise en page
app.js         construit la galerie à partir de models.json
models.json    ← le seul fichier à modifier au quotidien
images/        photos des modèles
assets/        logo, favicon, image de partage, police
check.py       vérification avant publication
```

## Ajouter un modèle (2 min)

1. Mets la photo dans `images/` : **carrée, 1200 × 1200 px, JPG, moins de 300 Ko**.
2. Ajoute un bloc dans `models.json` :

```json
{
  "title": "Nom du modèle",
  "categories": ["medium"],
  "description": "Une ou deux phrases.",
  "image": "images/nom-du-modele.jpg",
  "alt": "Description de la photo (accessibilité)",
  "makerworld": "https://makerworld.com/en/models/123456",
  "instagram": "https://www.instagram.com/p/ABC123/",
  "tags": ["Gothique", "15 × 15 cm"],
  "date": "2026-12-01"
}
```

`title`, `image` et `makerworld` sont obligatoires. Le reste est optionnel :
sans `instagram`, le bouton n'apparaît pas. Les modèles sont triés du plus récent au plus ancien d'après `date`.

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
- `label` : le texte affiché sur le site, modifiable librement (par exemple `"Small frame (≤ 10 cm)"`).
- Un modèle peut avoir plusieurs catégories, par exemple `["medium", "bas-relief"]`.
- Une catégorie qui n'a encore aucun modèle est masquée automatiquement.
- Chaque filtre a son propre lien, par exemple `https://ton-domaine/?category=bas-relief`,
  pratique pour une story ou un post Instagram.

3. Lance `python check.py`. Il signale le JSON cassé (virgule en trop),
   les images manquantes ou trop lourdes et les liens d'exemple oubliés.

## Avant la première mise en ligne

- `models.json` : remplace `YOUR_HANDLE` par tes pseudos MakerWorld et Instagram,
  et remplace les 3 modèles d'exemple ainsi que les images `images/example-*.jpg`.
- `index.html` : remplace `YOUR-DOMAIN` (3 lignes en haut). Ces lignes donnent l'aperçu
  du lien quand tu le partages (Instagram, Discord…).
- La langue du site est l'anglais (public international sur MakerWorld). Pour passer en français,
  il suffit de modifier les textes dans `index.html` et les 3 libellés de boutons dans `app.js`.

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
