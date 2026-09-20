"""Client HTTP poli pour l'Odoo Apps Store.

Trois garanties, dans l'ordre d'importance :

1. Cache disque. Une URL n'est jamais telechargee deux fois. Pendant le
   developpement du parseur, on retravaille sur le cache, pas sur le serveur.
2. Delai entre requetes. Par defaut 1,5 s, jamais desactivable a zero.
3. User-Agent identifiable, avec une adresse de contact.

Conformite robots.txt (verifie le 2026-09-21, https://apps.odoo.com/robots.txt) :
les regles pertinentes sont `Disallow: */page/*/*`, `Disallow: *?*page=` et
`Disallow: *?*order=`. Les URL utilisees ici sont de la forme
`/apps/modules[/category/<cat>]/browse/page/<n>[?series=<v>]` : la pagination
est un segment terminal (`/page/7`, sans segment suivant), donc hors du motif
`*/page/*/*` ; aucun parametre `page=` ni `order=` n'est employe. Le parametre
`series=` n'est pas restreint. Aucun `Crawl-delay` n'est declare.
"""

from __future__ import annotations

import hashlib
import logging
import random
import time
import warnings
from pathlib import Path
from urllib.parse import quote, urlencode

import requests

warnings.filterwarnings("ignore", message=".*OpenSSL.*")

BASE = "https://apps.odoo.com"
CONTACT = "ameth.yade@uadb.edu.sn"
USER_AGENT = (
    "erp-gaps-analysis/1.0 (academic research, M2 SIGLIS; "
    f"contact: {CONTACT}; )"
)

# Les 16 series Odoo exposees par le filtre `?series=` de l'Apps Store.
SERIES = [
    "5.0", "6.0", "6.1", "7.0", "8.0", "9.0", "10.0", "11.0",
    "12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0",
]

# Les 18 categories de premier niveau listees sur /apps/modules/browse.
CATEGORIES = [
    "Accounting", "Discuss", "Document Management", "Extra Tools",
    "Human Resources", "Industries", "Localization", "Manufacturing",
    "Marketing", "Point of Sale", "Productivity", "Project", "Purchases",
    "Sales", "Tutorial", "Warehouse", "Website", "eCommerce",
]

log = logging.getLogger(__name__)


def browse_url(category: str | None = None, page: int = 1,
               series: str | None = None) -> str:
    """Construit une URL de liste conforme au robots.txt."""
    path = "/apps/modules"
    if category:
        path += "/category/" + quote(category, safe="")
    path += "/browse"
    if page > 1:
        path += f"/page/{page}"
    query = urlencode({"series": series}) if series else ""
    return f"{BASE}{path}" + (f"?{query}" if query else "")


class PoliteClient:
    """Telecharge des pages en respectant un delai et un cache disque."""

    def __init__(self, cache_dir: str | Path = "data/raw/cache",
                 delay: float = 1.5, jitter: float = 0.5, timeout: int = 30,
                 max_retries: int = 4) -> None:
        if delay < 1.0:
            raise ValueError("delay < 1 s : ce n'est pas poli, et c'est detectable.")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.jitter = jitter
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_request = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en",
        })
        self.stats = {"hits": 0, "misses": 0, "errors": 0}

    def _cache_path(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
        return self.cache_dir / f"{digest}.html"

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last_request
        pause = self.delay + random.uniform(0, self.jitter) - elapsed
        if pause > 0:
            time.sleep(pause)
        self._last_request = time.monotonic()

    def get(self, url: str, use_cache: bool = True) -> str | None:
        """Renvoie le HTML de `url`, depuis le cache si possible, sinon None."""
        path = self._cache_path(url)
        if use_cache and path.exists():
            self.stats["hits"] += 1
            return path.read_text(encoding="utf-8")

        for attempt in range(1, self.max_retries + 1):
            self._wait()
            try:
                response = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as exc:
                log.warning("%s : %s (essai %d)", url, exc, attempt)
            else:
                if response.status_code == 200:
                    self.stats["misses"] += 1
                    path.write_text(response.text, encoding="utf-8")
                    return response.text
                if response.status_code == 404:
                    log.info("%s : 404", url)
                    self.stats["errors"] += 1
                    return None
                log.warning("%s : HTTP %d (essai %d)",
                            url, response.status_code, attempt)
            # Repli exponentiel : on ralentit quand le serveur proteste.
            time.sleep(min(60, 2 ** attempt))

        self.stats["errors"] += 1
        return None
