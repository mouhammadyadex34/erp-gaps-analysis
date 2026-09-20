"""Collecte des fiches modules de l'Odoo Apps Store, categorie par categorie.

Strategie
---------
On parcourt les 111 categories du site et on pagine chacune jusqu'a
epuisement. Se limiter aux 18 categories affichees sur la page d'accueil
amputerait le corpus d'un tiers : voir `discover_categories.py`. La serie Odoo n'est PAS obtenue via le filtre `?series=` mais lue
dans l'URL de chaque carte (`/apps/modules/18.0/nom`). Deux raisons :

1. Le filtre `?series=` n'expose que les 16 versions majeures. Les releases
   intermediaires d'Odoo Online (`saas-19.4`) en sont absentes : un balayage
   categorie x serie les perdrait.
2. Un balayage par categorie seule demande ~4 550 pages, contre ~4 900 pour un
   balayage croise. Moins de requetes, et une information plus complete.

Le prix affiche est celui du couple module-version, en euros pour l'essentiel.
Une ligne du fichier de sortie = un couple (module, serie), pas un module.

Reprise
-------
Chaque page parsee est ecrite immediatement en CSV et son URL est journalisee
dans un fichier `.done`. Relancer le script reprend ou il s'est arrete : le
cache disque du client evite en plus tout retelechargement.
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from census import parse_count
from odoo_client import PoliteClient, browse_url, load_categories
from parse_cards import FIELDNAMES, as_row, parse_page

PER_PAGE = 20
MAX_PAGES = 2000  # garde-fou : aucune categorie ne devrait l'atteindre

log = logging.getLogger("scraper")


def scrape(out_csv: Path, done_path: Path, delay: float,
           categories: list[str], limit_pages: int | None = None) -> None:
    client = PoliteClient(cache_dir="data/raw/cache_cards", delay=delay)

    done: set[str] = set()
    if done_path.exists():
        done = set(done_path.read_text(encoding="utf-8").split("\n")) - {""}
        log.info("Reprise : %d pages deja collectees", len(done))

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out_csv.exists()
    fetched = 0

    with out_csv.open("a", newline="", encoding="utf-8") as fh, \
            done_path.open("a", encoding="utf-8") as done_fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()

        for category in categories:
            first_url = browse_url(category=category)
            first_html = client.get(first_url)
            if first_html is None:
                log.error("Categorie %s inaccessible, ignoree", category)
                continue

            total = parse_count(first_html)
            if total is None:
                log.error("Compteur illisible pour %s, ignoree", category)
                continue
            n_pages = min(-(-total // PER_PAGE), MAX_PAGES)
            if limit_pages:
                n_pages = min(n_pages, limit_pages)
            log.info("%s : %d modules, %d pages", category, total, n_pages)

            for page in range(1, n_pages + 1):
                url = browse_url(category=category, page=page)
                if url in done:
                    continue
                html = client.get(url)
                if html is None:
                    log.warning("Page manquante : %s", url)
                    continue
                cards = parse_page(html, source_category=category,
                                   source_url=url)
                if not cards:
                    # Une page vide avant la derniere signale un changement de
                    # structure : on prefere s'arreter et le voir.
                    log.warning("Aucune carte sur %s", url)
                writer.writerows(as_row(c) for c in cards)
                fh.flush()
                done_fh.write(url + "\n")
                done_fh.flush()
                fetched += 1
                if page % 25 == 0 or page == n_pages:
                    print(f"  {category:<20} page {page:>4}/{n_pages}  "
                          f"cache={client.stats}", flush=True)

    print(f"\nPages traitees cette session : {fetched}")
    print(f"Sortie : {out_csv}")
    print(f"Cache  : {client.stats}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/raw/modules_raw.csv")
    parser.add_argument("--done", default="data/raw/pages_done.txt")
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--categories", nargs="*", default=None)
    parser.add_argument("--limit-pages", type=int, default=None,
                        help="Limite de pages par categorie (pour tester).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%H:%M:%S")
    categories = args.categories or load_categories()
    log.info("%d categories a parcourir", len(categories))
    scrape(Path(args.out), Path(args.done), args.delay,
           categories, args.limit_pages)


if __name__ == "__main__":
    main()
