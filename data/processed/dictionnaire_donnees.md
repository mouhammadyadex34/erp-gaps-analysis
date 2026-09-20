# Dictionnaire des donnees

Fichier : `data/processed/modules_clean.csv`

**Unite d'observation : un couple (module, serie Odoo).** Un module publie pour
six versions occupe six lignes. Compter des lignes n'est donc pas compter des
modules : pour les modules distincts, dedupliquer sur `technical_name`.

| Colonne | Type | Description |
|---|---|---|
| `technical_name` | texte | Nom technique du module, unique par serie |
| `series` | texte | Version Odoo visee (5.0 a 19.0, ou saas-XX.Y) |
| `series_kind` | texte | major = version majeure ; saas = release intermediaire Odoo Online |
| `series_order` | decimal | Cle de tri numerique des series (evite 10.0 < 9.0) |
| `is_saas` | booleen | Vrai pour les releases intermediaires |
| `title` | texte | Titre commercial affiche |
| `author` | texte | Nom de l'editeur, tel qu'affiche |
| `author_clean` | texte | Nom normalise : minuscules, suffixes juridiques retires |
| `is_free` | booleen | Vrai si le module est gratuit |
| `price_value` | decimal | Prix ; 0 pour les gratuits ; vide si illisible |
| `price_currency` | texte | Devise affichee ; vide pour les gratuits |
| `price_missing` | booleen | Vrai si module payant dont le prix n'a pas pu etre lu |
| `n_downloads` | entier | Telechargements cumules (modules GRATUITS uniquement) |
| `n_purchases` | entier | Achats cumules (modules PAYANTS uniquement) |
| `n_last_month` | entier | Telechargements ou achats du dernier mois |
| `usage_kind` | texte | downloads | purchases | none : quelle grandeur est mesuree |
| `summary` | texte | Resume affiche sur la carte, mots-cles SEO compris |
| `summary_prose` | texte | Resume ampute de la section << Search Keywords >> |
| `has_seo_keywords` | booleen | Vrai si le resume contenait des mots-cles SEO |
| `summary_missing` | booleen | Vrai si le resume est vide |
| `image_id` | texte | Identifiant de la vignette sur le CDN Odoo |
| `source_category` | texte | Categorie du site d'ou la fiche a ete lue |
| `fonction` | texte | Fonction metier du referentiel (17 valeurs) |
| `n_categories` | entier | Nombre de categories du site ou le module apparait |
| `categories_all` | texte | Liste de ces categories, separees par | |
| `source_url` | texte | URL de la page de liste d'origine |

## Avertissements

- `n_downloads` et `n_purchases` **ne mesurent pas la meme chose** et ne doivent
  jamais etre additionnes. `usage_kind` indique laquelle est renseignee.
- `fonction` resulte d'une table de correspondance interpretative
  (`category_mapping.csv`), pas d'une donnee du site.
- La note moyenne, la licence et la date de publication ne figurent pas sur les
  cartes de liste et sont donc absentes du corpus.