# Cartographier les manques des ERP

**Chaque module tiers publié sur l'Odoo Apps Store est la trace d'un besoin que
le progiciel standard ne couvrait pas. Ce dépôt collecte ces modules et en tire
une carte des manques des ERP.**

> *Résultat principal : à compléter une fois l'analyse terminée.*

![Figure principale](figures/01_modules_par_categorie.pdf)

---

## La question

Un module tiers n'existe que pour une raison : quelqu'un a payé un développeur
parce que le standard ne répondait pas à son besoin. Les dizaines de milliers de
modules publiés dessinent donc, en creux, une carte des manques des ERP.

**Qu'est-ce qui manque réellement aux ERP, et où ces manques se concentrent-ils ?**

## Méthodologie en cinq lignes

1. **Source** — l'Odoo Apps Store (`apps.odoo.com`), **111 catégories**,
   séries Odoo 5.0 à 19.0 plus les releases intermédiaires `saas-*`.
2. **Collecte** — les pages de liste, qui portent déjà nom, éditeur, prix,
   série et compteur d'usage. Une requête pour 20 modules au lieu d'une par
   module.
3. **Unité d'observation** — un couple *(module, série Odoo)*. Un module publié
   pour six versions donne six lignes : on mesure l'offre disponible pour une
   version donnée, pas le nombre de modules distincts.
4. **Recensement croisé** — le compteur « N Apps found » interrogé pour chaque
   couple (catégorie, série) donne la matrice temporelle complète en ~320
   requêtes.
5. **Analyse** — concentration par fonction métier, poids des contraintes
   locales, spécialisation sectorielle, et évolution par version.

## Reproduire

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Puis les trois notebooks, dans l'ordre :

| Notebook | Ce qu'il fait | Durée |
|---|---|---|
| `01_collecte.ipynb` | robots.txt, catégories, recensement, fiches | ~2 h |
| `02_nettoyage.ipynb` | nettoyage, référentiel, dictionnaire | < 1 min |
| `03_analyse.ipynb` | analyses et cinq figures | < 1 min |

Ils sont **autonomes** : tout le code y figure, aucun module à importer.

Les deux scripts mettent en cache chaque page sur disque et reprennent où ils
se sont arrêtés. Relancer ne retélécharge rien.

Puis les notebooks, dans l'ordre : `01_collecte`, `02_nettoyage`, `03_analyse`.

## Un piège qui coûtait un tiers du corpus

La page d'accueil de l'Apps Store affiche **18 catégories**. Les prendre pour
la liste complète est l'erreur naturelle — et elle est silencieuse.

Le contrôle de cohérence l'a révélée : la somme des effectifs de ces 18
catégories ne représente que **68 %** du total annoncé par le site. Un tiers du
catalogue était rangé ailleurs. Un sondage a suffi à trouver `Tools`, **la plus
grosse catégorie du site avec 12 210 modules**, qui n'est affichée nulle part.

`discover_categories.py` sonde 122 noms candidats tirés des catégories standard
d'Odoo et en retient **111 non vides**. La liste est validée par le seul test
qui vaille :

| | |
|---|---:|
| Somme des 111 catégories | 90 774 |
| Total annoncé par le site | 90 848 |
| **Résidu non attribué** | **74 (0,08 %)** |

Ce résidu est publié plutôt que dissimulé. Il prouve aussi que les catégories
forment une **partition** et non une hiérarchie : aucun double comptage.

## Éthique de la collecte

Le `robots.txt` d'`apps.odoo.com` a été lu avant d'écrire la première ligne de
code (vérifié le 21 septembre 2026). Les règles pertinentes sont
`Disallow: */page/*/*`, `Disallow: *?*page=` et `Disallow: *?*order=`.

Les URL utilisées ici sont de la forme
`/apps/modules/category/<catégorie>/browse/page/<n>` : la pagination est un
segment terminal, donc hors du motif `*/page/*/*` ; aucun paramètre `page=` ni
`order=` n'est employé. Aucun `Crawl-delay` n'est déclaré ; le collecteur
s'impose **1,5 seconde** entre deux requêtes, avec un délai aléatoire
supplémentaire et un repli exponentiel en cas d'erreur serveur. Le
`User-Agent` identifie le projet et donne une adresse de contact.

Seules des données publiques sont collectées : aucune page nécessitant un
compte, aucune donnée personnelle au-delà du nom commercial de l'éditeur.

## Limites

*Section à compléter au fil de l'analyse. Les limites déjà identifiées :*

- **Le nombre de modules ne mesure pas directement un manque.** Une catégorie
  dense peut signaler un besoin non couvert, un besoin trop spécifique pour
  être standardisé, ou simplement une catégorie où il est facile de publier.
- **Le compteur d'usage n'est pas homogène** : « téléchargements » pour les
  modules gratuits, « achats » pour les payants. Les deux sont stockés dans des
  colonnes distinctes et ne doivent pas être additionnés.
- **La catégorie est celle déclarée par l'éditeur**, avec ce que cela suppose
  d'optimisation pour la visibilité.
- **La note moyenne, la licence et la date de publication** ne figurent pas sur
  les cartes de liste et ne sont donc pas collectées.
- **Un module retiré du store est invisible.** Le corpus décrit l'offre à la
  date de collecte, pas l'histoire complète des publications.

## Structure du dépôt

```
├── notebooks/
│   ├── 01_collecte.ipynb   robots.txt, catégories, recensement, fiches
│   ├── 02_nettoyage.ipynb  nettoyage, référentiel, dictionnaire
│   └── 03_analyse.ipynb    analyses et figures
├── data/
│   ├── raw/                non versionné, régénéré par le notebook 01
│   └── processed/
│       ├── categories.csv           les 111 catégories du site
│       ├── category_mapping.csv     la table de correspondance
│       └── dictionnaire_donnees.md  description de chaque colonne
├── figures/                figures en PDF vectoriel (générées)
└── paper/                  document LaTeX
```

Le corpus nettoyé (`data/processed/modules_clean.csv`, ~70 Mo) n'est pas versionné :
il se régénère intégralement depuis les notebooks 01 et 02.

## Compiler le document

Le document se compile avec [Tectonic](https://tectonic-typesetting.github.io/),
qui télécharge lui-même les paquets nécessaires :

```bash
cd paper && tectonic main.tex
```

La bibliographie utilise le moteur `bibtex` plutôt que `biber` : Tectonic embarque
le premier, le second demanderait une installation séparée.

## Licence

Code sous licence MIT. Les données collectées restent la propriété de leurs
éditeurs respectifs et ne sont redistribuées que sous forme agrégée.
