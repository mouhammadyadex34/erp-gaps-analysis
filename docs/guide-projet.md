# Cartographier les manques des ERP
## Guide de projet, de A à Z

---

## 1. L'idée en une page

### Le point de départ

J'ai voulu développer un module Odoo pour prolonger un cas d'étude. Avant de me lancer, j'ai vérifié si la fonction existait déjà. Elle existait, en standard. J'ai cherché une variante plus fine. Elle existait aussi, dans les modules tiers de l'Apps Store.

Ce double échec contient l'idée du projet.

### Le raisonnement

Un module tiers n'existe que pour une seule raison : quelqu'un a payé un développeur parce que le progiciel standard ne répondait pas à son besoin. **Chaque module publié est la trace d'un manque.**

```
Un module tiers existe
        ↓
= un besoin non couvert par le standard
        ↓
Des milliers de modules publiés
        ↓
= une carte des manques des ERP
```

Personne n'a publié cette carte. Les éditeurs n'y ont pas intérêt : elle met en évidence les trous de leur propre produit. Les intégrateurs la connaissent empiriquement mais ne la formalisent pas. La place est libre.

### La question du projet

> **Qu'est-ce qui manque réellement aux ERP, et où ces manques se concentrent-ils ?**

### Les trois livrables

| Livrable | Contenu | Support |
|---|---|---|
| Le jeu de données | Les modules de l'Apps Store, nettoyés et structurés | GitHub (CSV + notebook) |
| L'analyse | Les manques récurrents par fonction, secteur, géographie | Document LaTeX (PDF) |
| Le récit | L'histoire du projet et ses résultats principaux | Post LinkedIn |

Les trois se publient **ensemble**. Le post renvoie au PDF, le PDF renvoie au dépôt.

---

## 2. Pourquoi ce projet est le bon pour toi

Tu cherches une alternance en data, tu aimes coder, analyser et comprendre le métier. Ce projet mobilise les trois, ce qui est rare dans un portfolio étudiant.

| Ce que cherche un recruteur data | Où ça apparaît dans le projet |
|---|---|
| Savoir aller chercher la donnée | Tu construis ton jeu de données, tu ne télécharges pas un CSV Kaggle |
| Savoir nettoyer | Données réelles, donc sales : doublons, champs manquants, formats incohérents |
| Poser de bonnes questions | Le projet part d'une question, pas d'un jeu de données |
| Comprendre un domaine | Tu parles ERP, un domaine que peu de juniors maîtrisent |
| Communiquer un résultat | Le PDF et le post prouvent que tu sais expliquer |

**Le différenciateur : data + ERP.** Les entreprises qui recrutent des analystes ont presque toutes un ERP. Un profil qui comprend les deux mondes est immédiatement utile.

### Ce que le projet n'est pas

Ce n'est pas un projet de développement logiciel. Tu ne construis pas un outil. Tu produis une **analyse**, et c'est précisément ce qui la rend crédible : elle ne prétend pas résoudre un problème que le marché a déjà résolu.

---

## 3. Les questions d'analyse

Classées de la plus simple à la plus intéressante. Commence par les premières, les dernières font la valeur du projet.

### Niveau 1 — Descriptif (échauffement)

1. Combien de modules au total ? Quelle répartition par catégorie ?
2. Quelle proportion de modules gratuits contre payants ? Quelle distribution des prix ?
3. Combien d'éditeurs distincts ? Le marché est-il concentré ou fragmenté ?

### Niveau 2 — Structurel (le cœur)

4. **Quelles fonctions métier concentrent le plus de modules tiers ?**
   C'est la carte des manques. Comptabilité ? RH ? Production ? Vente ?

5. **Quelle part des modules répond à une contrainte locale ou réglementaire ?**
   Fiscalité par pays, normes comptables, conformité. Cela mesure le poids du local dans un produit global.

6. **Quels secteurs d'activité sont visés ?**
   Un module « pour le BTP » ou « pour la pharmacie » signale un secteur mal servi par le standard.

### Niveau 3 — Dynamique (ce qui impressionne)

7. **Quels manques Odoo a-t-il comblés au fil des versions ?**
   Si une catégorie comptait beaucoup de modules en version 14 et peu en version 19, l'éditeur a absorbé le besoin. Si elle reste dense, le manque persiste. **C'est le résultat le plus fort du projet.**

8. **Quels manques résistent depuis le début ?**
   Un besoin couvert par des modules tiers sur six versions consécutives est un manque structurel, pas un oubli.

### Le piège d'interprétation

Beaucoup de modules dans une catégorie ne signifie pas « Odoo est mauvais sur ce point ». Cela peut signifier :

- un besoin réellement non couvert,
- un besoin trop spécifique pour être standardisé,
- ou simplement une catégorie où il est facile de publier.

**Formule tes conclusions avec cette nuance.** Un professionnel te corrigera immédiatement si tu l'oublies, et il aura raison.

---

## 4. Étape 1 — La collecte

### Avant toute chose : les précautions

1. **Lis les conditions d'utilisation du site** et son fichier `robots.txt` avant d'écrire une ligne de code.
2. **Ne collecte que des données publiques** : ce qui s'affiche sans compte.
3. **Espace tes requêtes** (une à deux secondes entre chaque). Tu n'es pas pressé, et surcharger un serveur est à la fois impoli et détectable.
4. **Identifie-toi** dans l'en-tête `User-Agent` avec un contact.
5. **Mets en cache** chaque page téléchargée sur ton disque. Tu ne retélécharges jamais deux fois la même chose pendant le développement.

Si la collecte automatisée est interdite, deux replis existent :
- les dépôts publics de l'**OCA** (Odoo Community Association) sur GitHub, dont les métadonnées de modules sont librement accessibles ;
- les fichiers `__manifest__.py` des modules open source, qui contiennent nom, catégorie, version, dépendances et licence.

### Les champs à récupérer

| Champ | Pourquoi il compte |
|---|---|
| Nom du module | Identification, analyse textuelle |
| Description courte | Analyse sémantique des besoins |
| Catégorie | Axe d'analyse principal |
| Éditeur | Concentration du marché |
| Prix | Modèle économique |
| Version Odoo supportée | **Axe temporel, le plus précieux** |
| Date de publication | Dynamique du marché |
| Nombre de téléchargements ou d'installations | Mesure d'usage réel |
| Note et nombre d'avis | Qualité perçue |
| Licence | Open source ou propriétaire |

### Outils

- `requests` pour les requêtes HTTP
- `BeautifulSoup` ou `lxml` pour extraire le contenu HTML
- `time.sleep()` pour espacer, systématiquement
- `pandas` pour stocker au fur et à mesure

**Écris tes données brutes sur disque dès la collecte**, avant tout nettoyage. Si tu casses ton script de nettoyage, tu ne recollectes pas.

---

## 5. Étape 2 — Le nettoyage

C'est 70 % du travail réel d'un analyste, et c'est bien que cela se voie dans ton dépôt.

### Ce que tu vas rencontrer

| Problème | Traitement |
|---|---|
| Un même module publié pour plusieurs versions | Décider : une ligne par module, ou une par couple module-version ? **Documente ton choix.** |
| Prix en formats variés (`49 €`, `$59`, `Gratuit`) | Normaliser en une colonne numérique + une colonne devise |
| Catégories incohérentes ou multiples | Construire une table de correspondance vers un référentiel unique |
| Descriptions vides ou en plusieurs langues | Marquer plutôt que supprimer, et compter les manquants |
| Éditeurs nommés différemment selon les modules | Normaliser (minuscules, suppression des suffixes juridiques) |

### La règle d'or

**Chaque décision de nettoyage doit être écrite et justifiée.** Dans ton notebook, une cellule de texte avant chaque transformation : ce que tu fais et pourquoi. C'est ce qui distingue un travail sérieux d'un script jetable.

### Le livrable de cette étape

Un fichier `modules_clean.csv` avec une ligne par observation, des types cohérents, et un fichier `dictionnaire_donnees.md` qui décrit chaque colonne.

---

## 6. Étape 3 — L'analyse

### Méthode

Procède question par question. Pour chacune : le calcul, le résultat, puis **une phrase d'interprétation**. Un chiffre sans interprétation n'est pas une analyse.

### Techniques utiles, par ordre d'utilité

**1. Comptages et proportions par catégorie**
Basique, mais c'est l'ossature de tout le reste.

**2. Analyse de l'évolution par version**
Pour chaque catégorie, le nombre de modules par version Odoo. C'est ce qui révèle les manques comblés et les manques persistants.

**3. Concentration du marché**
Quelle part des modules est publiée par les dix plus gros éditeurs ? Un indice de concentration (Herfindahl) est facile à calculer et parle aux économistes.

**4. Analyse textuelle des descriptions**
Extraction des termes les plus fréquents par catégorie. Cela fait apparaître les besoins récurrents formulés dans les mots des développeurs eux-mêmes. Reste simple : fréquences et n-grammes suffisent, pas besoin de modélisation thématique sophistiquée.

**5. Croisement catégorie × prix**
Les besoins les plus critiques sont-ils les plus chers ?

### Discipline d'analyse

- **Ne conclus jamais depuis un seul chiffre.** Croise au moins deux angles.
- **Cherche activement ce qui contredit ton hypothèse.** C'est le réflexe qui distingue un analyste d'un militant.
- **Note les limites au fur et à mesure**, dans un fichier à part. Elles deviendront une section du PDF, et cette section est celle que les professionnels lisent en premier.

---

## 7. Étape 4 — Les visualisations

Cinq graphiques suffisent. Mieux vaut cinq lisibles que quinze décoratifs.

| Graphique | Ce qu'il montre | Type |
|---|---|---|
| 1 | Nombre de modules par catégorie métier | Barres horizontales triées |
| 2 | Évolution du nombre de modules par version, pour les 6 principales catégories | Lignes multiples |
| 3 | Répartition gratuit / payant et distribution des prix | Boîtes à moustaches par catégorie |
| 4 | Concentration des éditeurs | Courbe de Lorenz ou barres cumulées |
| 5 | Termes les plus fréquents par catégorie | Tableau ou barres groupées |

### Règles de lisibilité

- Un titre qui **énonce le résultat**, pas le sujet. « Les modules comptables dominent l'Apps Store » plutôt que « Modules par catégorie ».
- Axes nommés, unités précisées.
- Pas de couleur décorative : la couleur ne sert qu'à distinguer une information.
- Testez en noir et blanc : si le graphique reste lisible, il est bon.

Outils : `matplotlib` pour le contrôle fin, `seaborn` pour aller vite. Exporte en **PDF vectoriel** pour l'inclusion LaTeX, pas en PNG.

---

## 8. Le dépôt GitHub

### Structure

```
erp-gaps-analysis/
├── README.md                  ← la vitrine, soigne-le
├── LICENSE                    ← MIT, par défaut
├── requirements.txt
├── data/
│   ├── raw/                   ← non versionné (.gitignore)
│   └── processed/
│       ├── modules_clean.csv
│       └── dictionnaire_donnees.md
├── notebooks/
│   ├── 01_collecte.ipynb
│   ├── 02_nettoyage.ipynb
│   └── 03_analyse.ipynb
├── src/
│   ├── scraper.py
│   └── cleaning.py
├── figures/                   ← les PDF des graphiques
└── paper/
    ├── main.tex
    └── main.pdf
```

### Le README

C'est la page que les recruteurs ouvrent. Il contient, dans cet ordre :

1. **Une phrase** qui dit ce que fait le projet
2. **Le résultat principal**, en une ou deux lignes
3. **Un graphique** (le plus parlant)
4. La méthodologie en cinq lignes
5. Comment reproduire
6. Les limites
7. Le lien vers le PDF

### Les bonnes pratiques qui se voient

- Des commits nommés correctement, pas « update » quinze fois
- Un `requirements.txt` à jour
- Les données brutes exclues du dépôt, avec le script pour les régénérer
- Du code lisible : des fonctions nommées, des docstrings

---

## 9. Le document LaTeX

### Pourquoi LaTeX est un bon choix ici

Un PDF composé proprement signale un travail achevé. Il se partage, s'archive et se cite. Et pour un profil data, savoir produire un document technique propre est une compétence en soi.

### Le plan

```
1. Introduction                                        ~1 page
   1.1 Le contexte : le marché des ERP et le modèle modulaire
   1.2 La question de recherche
   1.3 Ce que ce travail apporte

2. Méthodologie                                        ~2 pages
   2.1 Source des données et périmètre
   2.2 Protocole de collecte (et précautions éthiques)
   2.3 Nettoyage : décisions prises et justifications
   2.4 Variables retenues (tableau du dictionnaire)

3. Description du corpus                               ~2 pages
   3.1 Volumétrie
   3.2 Répartition par catégorie
   3.3 Structure du marché des éditeurs

4. Résultats                                           ~4 pages
   4.1 Où se concentrent les modules tiers
   4.2 Le poids des contraintes locales et réglementaires
   4.3 La spécialisation sectorielle
   4.4 Évolution par version : manques comblés, manques persistants

5. Discussion                                          ~2 pages
   5.1 Interprétation : que révèle cette carte
   5.2 Ce que cela implique pour un projet ERP (make or buy)
   5.3 Limites de l'étude

6. Conclusion                                          ~0.5 page

Annexes
   A. Dictionnaire des données
   B. Table de correspondance des catégories
   C. Code source (ou renvoi au dépôt)
```

**Cible : 12 à 15 pages.** Au-delà, personne ne lit.

### Le squelette du préambule

```latex
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{lmodern}

\usepackage[margin=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}      % tableaux propres : \toprule \midrule \bottomrule
\usepackage{caption}
\usepackage{hyperref}
\usepackage{csquotes}

\usepackage[backend=biber,style=numeric]{biblatex}
\addbibresource{references.bib}

\title{Cartographier les manques des ERP :\\
       une analyse des modules tiers de l'écosystème Odoo}
\author{Prénom Nom \\ \small M2 --- Université de Pau et des Pays de l'Adour}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
Quatre à six phrases. Le problème, la méthode, le résultat principal,
la portée. C'est la seule partie que la majorité des lecteurs lira.
Écris-la en dernier.
\end{abstract}

\tableofcontents
\newpage

% ... sections ...

\printbibliography
\end{document}
```

### Trois conseils de rédaction

1. **Écris le résumé en dernier**, mais place-le en premier. Il doit tenir seul.
2. **Chaque figure a une légende qui énonce le résultat**, pas le contenu. Le lecteur qui ne lit que les figures et leurs légendes doit comprendre l'essentiel.
3. **La section « Limites » est ta meilleure section.** Elle montre que tu sais ce que ton analyse ne prouve pas. C'est la marque d'un esprit rigoureux, et les professionnels la repèrent immédiatement.

### Compilation

```
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

Ou utilise Overleaf si tu ne veux pas installer de distribution LaTeX.

---

## 10. Le post LinkedIn

### La structure

```
[1. L'accroche — une histoire, pas une annonce]
En cours, j'ai voulu développer un module Odoo.
J'ai vérifié avant de me lancer : la fonction existait déjà.
J'ai cherché une variante plus fine. Elle existait aussi.

[2. Le retournement — c'est ce qui fait lire la suite]
Alors j'ai retourné la question.
Un module tiers n'existe que parce que le standard ne suffisait pas.
Chaque module publié est donc la trace d'un manque.

[3. Ce que tu as fait — concret et chiffré]
J'ai analysé [N] modules de l'Odoo Apps Store pour
cartographier ce qui manque vraiment aux ERP.

[4. Trois résultats — les vrais, pas des généralités]
→ [résultat 1]
→ [résultat 2]
→ [résultat 3]

[5. Les liens]
L'analyse complète (PDF) : [lien]
Les données et le code : [lien GitHub]

[6. L'invitation — c'est elle qui génère les commentaires]
Je suis preneur de retours, surtout de ceux qui travaillent
sur des projets ERP au quotidien. Si un résultat vous paraît
faux, dites-le moi.
```

### Pourquoi ce post fonctionne

- Il **raconte** au lieu d'annoncer
- Il contient un **retournement** : l'échec devient la méthode
- Il apporte des **chiffres que personne n'a**
- Il se termine par une **invitation à te contredire**, et les commentaires font remonter la publication

### Les erreurs qui tuent un post étudiant

| À éviter | Pourquoi |
|---|---|
| « Je suis fier de vous annoncer » | Tout le monde l'écrit, plus personne ne le lit |
| Des emojis à chaque ligne | Signale un contenu faible |
| Quinze hashtags | Idem. Trois suffisent. |
| Parler de soi plutôt que du problème | Le lecteur s'intéresse au problème, pas à ton parcours |
| Taguer des gens sans les prévenir | Associer leur nom à ton contenu sans accord |

### Le calendrier

1. Publie le PDF et le dépôt **d'abord**
2. Publie le post **ensuite**, avec les liens actifs
3. Mardi ou jeudi matin, entre 8h et 10h
4. **Réponds à chaque commentaire** dans les 24 heures

### Sur le fait de taguer ton enseignante

Demande-lui avant. Une phrase suffit : « Cela vous dérange-t-il si je vous mentionne dans un post où je partage ce travail ? » Si elle accepte, une mention sobre en fin de post : « Merci à [Nom] dont le cours est à l'origine de ce travail. »

---

## 11. Planning et checklist

### Planning réaliste

| Phase | Durée | Livrable |
|---|---|---|
| Cadrage et vérification des sources | 0,5 jour | Décision sur la source de données |
| Développement du collecteur | 1 à 2 jours | `scraper.py` fonctionnel |
| Collecte effective | 0,5 jour (souvent en arrière-plan) | Données brutes |
| Nettoyage | 1,5 jour | `modules_clean.csv` + dictionnaire |
| Analyse | 2 jours | Notebook complet |
| Visualisations | 1 jour | 5 figures en PDF |
| Rédaction LaTeX | 2 jours | `main.pdf` |
| README et mise au propre du dépôt | 0,5 jour | Dépôt public |
| Post LinkedIn | 0,5 jour | Publication |

**Total : environ 10 jours de travail effectif**, soit trois à quatre semaines en parallèle des cours.

### Checklist avant publication

**Données et code**
- [ ] Le collecteur respecte le `robots.txt` et espace ses requêtes
- [ ] Les données brutes ne sont pas versionnées, mais le script pour les régénérer l'est
- [ ] Le dictionnaire des données décrit chaque colonne
- [ ] Le notebook s'exécute de bout en bout sans erreur, dans un environnement neuf
- [ ] Le `requirements.txt` est à jour

**Analyse**
- [ ] Chaque chiffre avancé est reproductible depuis le notebook
- [ ] Chaque conclusion est nuancée : je dis ce que le chiffre prouve et ce qu'il ne prouve pas
- [ ] La section « Limites » est écrite et honnête
- [ ] J'ai cherché ce qui contredit mes conclusions

**Document**
- [ ] Le résumé tient seul, sans le reste du document
- [ ] Chaque figure a une légende qui énonce un résultat
- [ ] Le document est compilé sans avertissement
- [ ] Une relecture à voix haute a été faite

**Publication**
- [ ] Les liens du post fonctionnent
- [ ] Le dépôt est public
- [ ] L'accord a été demandé avant toute mention de quelqu'un
- [ ] Je suis disponible dans les 24h pour répondre aux commentaires

---

## En résumé

Ce projet ne prétend pas résoudre un problème que le marché a déjà résolu. Il **documente** un problème que personne n'a documenté. C'est plus modeste en apparence, et beaucoup plus solide.

Et il répond, avec des données, à la question que tu as posée à ton enseignante — sans avoir eu besoin d'attendre sa réponse.
