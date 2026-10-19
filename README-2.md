# Explorateur Unicode 🔣 — site 100 % automatique

Site statique pour explorer et copier **~1 500 caractères Unicode**, optimisé
pour le référencement et la monétisation. **Aucune configuration, aucun
champ à remplacer** : l'URL du site, le sitemap, les balises SEO, les
mentions légales, AdSense et la vérification Google sont détectés ou injectés
**automatiquement** à chaque génération.

## Ce que le site contient

- **Application de recherche** (`index.html`) : recherche par nom, code `U+`
  ou caractère collé, copie en un clic (HTML, CSS, JS, UTF-8).
- **~1 500 pages SEO** (`emoji/*.html`) : une page indexable par caractère
  (title, description, canonical, Open Graph, JSON-LD, boutons de copie).
- **17 pages catégories** (`categorie/*.html`) : maillage interne complet.
- **`sitemap.xml`**, **`robots.txt`**, **`ads.txt`** : générés automatiquement.
- **Mentions légales / RGPD** : section contact remplie automatiquement avec
  l'adresse du dépôt (anonymat de l'éditeur conforme à l'art. 6 LCEN).
- Tout est **regénéré chaque nuit** par GitHub Actions (`script.py`).

## 🚀 Mise en ligne — 3 actions suffisent (~10 min)

1. **Créer le dépôt** sur github.com : *New repository* → nom quelconque
   (ex. `explorateur-unicode`) → **Public** → *Create*.
2. **Envoyer seulement les 6 fichiers de base** (les ~1 500 pages seront
   générées automatiquement par le workflow, inutile de tout uploader) :
   - *Add file → Upload files* → glisser-déposez **6 fichiers** :
     `index.html`, `style.css`, `app.js`, `script.py`,
     `mentions-legales.html`, `README.md` → *Commit changes* ;
   - *Add file → Create new file* → comme nom, tapez exactement :
     **`.github/workflows/unicode.yml`** (les `/` créent les dossiers) →
     collez le contenu du fichier du même nom présent dans ce dossier →
     *Commit changes*.

   Dès ce commit, le workflow démarre (onglet **Actions**) : il détecte
   l'URL, génère toutes les pages et commite le résultat en ~1 minute.
3. **Activer GitHub Pages** : *Settings → Pages → Source : Deploy from a
   branch → main / (root) → Save*.

C'est tout. Le workflow se lance seul, **détecte l'URL de votre site tout
seul** (`https://<votre-compte>.github.io/<dépôt>/`) à partir des variables
fournies par GitHub Actions, régénère toutes les pages avec les bonnes URL,
et commite le résultat. En cas de doute : onglet **Actions → Automatisation
Unicode → Run workflow** pour forcer une régénération après l'étape 3.

> ✏️ **Zéro édition de fichier, promis.** Les blocs marqués `AUTO-*` dans
> `index.html` et `mentions-legales.html` sont réécrits automatiquement.

## 🔎 Référencement (une fois le site en ligne)

1. [Google Search Console](https://search.google.com/search-console) →
   *Ajouter une propriété → Préfixe d'URL* → l'URL de votre site.
2. Vérifiez la propriété avec le **fichier HTML** fourni par Google
   (uploadez-le à la racine du dépôt, c'est un simple fichier — aucune édition).
   *Alternative sans fichier : créez la variable de dépôt
   `GOOGLE_SITE_VERIFICATION` (valeur = le jeton), le workflow injectera la
   balise meta sur toutes les pages au prochain run.*
3. *Sitemaps* → soumettez `sitemap.xml`. L'indexation des ~1 500 pages
   prend de quelques jours à quelques semaines.

## 💰 Monétisation (quand le trafic commence)

1. Créez un compte [Google AdSense](https://adsense.google.com) → ajoutez le
   site → laissez la vérification AdSense se faire (délai de quelques jours).
2. Une fois le site approuvé, dans votre dépôt :
   *Settings → Secrets and variables → Actions → Variables → New variable* :
   - **Nom** : `ADSENSE_ID` — **Valeur** : les chiffres de votre ID éditeur
     (dans AdSense, votre `ca-pub-XXXXXXXXXXXXXXXX` → mettez seulement les
     `XXXXXXXXXXXXXXXX`).
3. Relancez le workflow (*Actions → Run workflow*) : le script AdSense est
   injecté **sur toutes les ~1 500 pages** et `ads.txt` est rempli
   automatiquement. Dans AdSense, activez les **annonces automatiques** et
   créez le **message de consentement RGPD** (*Confidentialité et messagerie*).

### Variables optionnelles (Settings → Secrets and variables → Actions)

| Variable | Effet |
|---|---|
| `SITE_URL` | Force l'URL du site (ex. domaine personnalisé) partout |
| `ADSENSE_ID` | Injecte AdSense sur toutes les pages + remplit `ads.txt` |
| `GOOGLE_SITE_VERIFICATION` | Injecte la balise meta de vérification Google |

## 🧪 Tester en local

```bash
python3 script.py            # génère tout (URL locale localhost:8000)
python3 -m http.server 8000  # http://localhost:8000
```

## Arborescence

```
├── .github/workflows/unicode.yml   # Workflow de régénération automatique
├── .nojekyll                       # Hébergement 100 % statique
├── index.html                      # Accueil (bloc SEO auto-patché)
├── style.css / app.js              # Thème + logique (aucune dépendance)
├── script.py                       # Générateur (bibliothèque standard)
├── mentions-legales.html           # Contact auto-patché (dépôt GitHub)
├── ads.txt / robots.txt / sitemap.xml   # Générés
├── output/data.json                # Base de l'app (générée)
├── emoji/*.html                    # ~1 500 pages caractères (générées)
└── categorie/*.html                # 17 pages catégories (générées)
```

## Personnaliser les catégories

Modifiez la liste `CATEGORIES` dans `script.py` (plages de points de code
hexadécimales) : les pages, le sitemap et le JSON se régénèrent tout seuls.

> **Note Unicode** : la version suivie est celle de Python (3.13 → Unicode
> 15.1). Pour plus récent : bibliothèque `unicodedata2` + `requirements.txt`.
