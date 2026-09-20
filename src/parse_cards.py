"""Extraction des fiches modules depuis une page de liste de l'Apps Store.

Une page de liste contient 20 cartes `loempia_app_card`. Chaque carte porte
deja l'essentiel : nom technique, serie Odoo, titre, editeur, prix, resume, et
un compteur d'usage. Parcourir les listes plutot que les 90 000 pages de detail
divise le volume de requetes par 20, pour une perte d'information limitee
(note moyenne, licence et date de publication ne sont pas dans la carte — c'est
une limite a documenter, pas un defaut de collecte).

Deux variantes de carte coexistent et il faut les traiter separement :

- module gratuit : prix affiche « FREE », compteur « Total Downloads: N »
- module payant  : prix numerique + devise, compteur « Total Purchases: N »

Le compteur n'est donc pas la meme grandeur d'un module a l'autre. On le stocke
dans deux colonnes distinctes plutot que dans une colonne « usage » qui
melangerait des telechargements et des achats.
"""

from __future__ import annotations

import html as html_mod
import re
from dataclasses import asdict, dataclass

CARD_SPLIT_RE = re.compile(r'<div class="\s*loempia_app_entry loempia_app_card')
# Le segment de serie n'est pas toujours « 18.0 » : l'Apps Store publie aussi
# des releases intermediaires d'Odoo Online sous la forme « saas-19.4 ».
# Un motif limite a \d+\.\d+ les rejetait silencieusement (3 cartes sur 20 sur
# certaines pages) — d'ou un motif large, la distinction etant faite plus loin.
HREF_RE = re.compile(r'href="/apps/modules/([\w.-]+)/([^"/?#]+)"')
SUMMARY_RE = re.compile(
    r'<p class="loempia_panel_summary">(.*?)</p>', re.S)
TITLE_RE = re.compile(r'<h5 title="(.*?)"', re.S)
AUTHOR_RE = re.compile(
    r'loempia_panel_author[^>]*>\s*<b>(.*?)</b>', re.S)
PRICE_BLOCK_RE = re.compile(r'loempia_panel_price(.*?)</div>', re.S)
CURRENCY_VALUE_RE = re.compile(
    r'<span class="oe_currency_value">([\d.,]+)</span>\s*([^<\s]*)', re.S)
IMAGE_ID_RE = re.compile(r'module_image\?image_id=(\d+)')
COUNTER_RE = re.compile(
    r'title="Total (Downloads|Purchases):\s*([\d,\s]+),\s*'
    r'Last month:\s*([\d,\s]+)"', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def _text(fragment: str) -> str:
    """Retire les balises, decode les entites, normalise les espaces."""
    return re.sub(r"\s+", " ", html_mod.unescape(TAG_RE.sub(" ", fragment))).strip()


def _int(raw: str) -> int | None:
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


@dataclass
class Card:
    technical_name: str
    series: str
    series_kind: str  # "major" (18.0) ou "saas" (saas-19.4)
    title: str
    author: str
    is_free: bool
    price_value: float | None
    price_currency: str | None
    n_downloads: int | None
    n_purchases: int | None
    n_last_month: int | None
    summary: str
    image_id: str | None
    source_category: str
    source_url: str


def parse_page(html: str, source_category: str, source_url: str) -> list[Card]:
    """Renvoie les cartes d'une page de liste, dans l'ordre d'affichage."""
    cards = []
    for chunk in CARD_SPLIT_RE.split(html)[1:]:
        href = HREF_RE.search(chunk)
        if not href:
            # Une carte sans lien module n'est pas exploitable : on la laisse
            # tomber plutot que d'inventer une cle.
            continue
        series, technical_name = href.group(1), href.group(2)

        summary_match = SUMMARY_RE.search(chunk)
        summary = _text(summary_match.group(1)) if summary_match else ""

        title_match = TITLE_RE.search(chunk)
        title = html_mod.unescape(title_match.group(1)).strip() if title_match else ""

        author_match = AUTHOR_RE.search(chunk)
        author = _text(author_match.group(1)) if author_match else ""

        is_free, price_value, price_currency = False, None, None
        price_block = PRICE_BLOCK_RE.search(chunk)
        if price_block:
            block = price_block.group(1)
            money = CURRENCY_VALUE_RE.search(block)
            if money:
                # Les montants sont formates a l'anglaise (« 1053.85 »), le
                # separateur de milliers etant absent dans ce champ.
                price_value = float(money.group(1).replace(",", ""))
                price_currency = html_mod.unescape(money.group(2)).strip() or None
            elif "FREE" in _text(block).upper():
                is_free, price_value = True, 0.0

        n_downloads = n_purchases = n_last_month = None
        counter = COUNTER_RE.search(chunk)
        if counter:
            kind, total, last_month = counter.groups()
            n_last_month = _int(last_month)
            if kind == "Downloads":
                n_downloads = _int(total)
            else:
                n_purchases = _int(total)

        image = IMAGE_ID_RE.search(chunk)

        cards.append(Card(
            technical_name=technical_name,
            series=series,
            series_kind="saas" if series.startswith("saas") else "major",
            title=title,
            author=author,
            is_free=is_free,
            price_value=price_value,
            price_currency=price_currency,
            n_downloads=n_downloads,
            n_purchases=n_purchases,
            n_last_month=n_last_month,
            summary=summary,
            image_id=image.group(1) if image else None,
            source_category=source_category,
            source_url=source_url,
        ))
    return cards


FIELDNAMES = list(Card.__dataclass_fields__)


def as_row(card: Card) -> dict:
    return asdict(card)
