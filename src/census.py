"""Recensement : nombre de modules par categorie x version Odoo.

L'Apps Store affiche un compteur « N Apps found » sur chaque page de liste.
Interroger ce compteur pour chaque couple (categorie, serie) donne la matrice
complete des volumes en ~320 requetes, la ou parcourir les 90 000 fiches en
demanderait 90 000.

C'est cette matrice qui repond aux questions 7 et 8 du projet : quels manques
Odoo a combles au fil des versions, et lesquels persistent.

Attention a l'interpretation : le compteur porte sur des couples module-version.
Un meme module publie pour 6 series compte 6 fois dans le total general. C'est
voulu — on mesure l'offre disponible pour une version donnee, pas le nombre
d'editeurs distincts.
"""

from __future__ import annotations

import csv
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from odoo_client import CATEGORIES, SERIES, PoliteClient, browse_url

RESUME_RE = re.compile(
    r'<span class="[^"]*loempia_search_resume[^"]*">(.*?)</span>', re.S)
TAG_RE = re.compile(r"<[^>]+>")
COUNT_RE = re.compile(r"([\d\s,\u202f\u00a0]+?)\s*Apps?\s+found", re.IGNORECASE)


def parse_count(html: str) -> int | None:
    """Extrait l'entier du libelle « N Apps found ».

    Le compteur vit dans `<span class="loempia_search_resume">`, ou le nombre
    et le libelle sont separes par des sauts de ligne et parfois des balises.
    On reduit d'abord a ce bloc, puis on retire les balises : chercher
    directement dans le HTML brut echouerait des qu'un `<b>` s'intercale.
    """
    resume = RESUME_RE.search(html)
    fragment = resume.group(1) if resume else html
    text = TAG_RE.sub(" ", fragment)
    match = COUNT_RE.search(text)
    if not match:
        return None
    digits = re.sub(r"[^\d]", "", match.group(1))
    return int(digits) if digits else None


def run(out_path: Path) -> None:
    client = PoliteClient(cache_dir="data/raw/cache_census")
    rows = []

    # `None` en tete de chaque liste = l'agregat « toutes categories » /
    # « toutes series ». On les collecte aussi : ils servent de controle de
    # coherence face a la somme des cellules.
    categories = [None] + CATEGORIES
    series_list = [None] + SERIES
    total = len(categories) * len(series_list)
    done = 0

    for category in categories:
        for series in series_list:
            url = browse_url(category=category, series=series)
            html = client.get(url)
            count = parse_count(html) if html else None
            rows.append({
                "category": category or "__ALL__",
                "series": series or "__ALL__",
                "n_modules": count if count is not None else "",
                "url": url,
            })
            done += 1
            print(f"[{done:3d}/{total}] {category or 'ALL':<20} "
                  f"{series or 'ALL':<6} -> {count}", flush=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["category", "series", "n_modules", "url"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nEcrit : {out_path} ({len(rows)} lignes)")
    print(f"Cache : {client.stats}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING,
                        format="%(levelname)s %(message)s")
    run(Path("data/interim/census_category_series.csv"))
