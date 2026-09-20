"""Reconstitution de la liste complete des categories de l'Apps Store.

Le probleme
-----------
La page /apps/modules/browse n'affiche que 18 categories, et la navigation
interne d'une page de categorie n'en montre pas davantage. Or la somme des
effectifs de ces 18 categories ne represente que ~68 % du total annonce par le
site : un tiers du corpus est range ailleurs. Sonder au hasard a suffi a
trouver « Tools » (12 210 modules), invisible depuis l'accueil.

La methode
----------
On sonde une liste de noms candidats tiree des categories standard d'Odoo
(`ir.module.category`) et on garde celles qui renvoient un effectif non nul.
La liste retenue n'est valide que si la somme des effectifs rejoint le total
annonce : ce controle est le seul garde-fou contre une categorie oubliee, et
son resultat doit etre publie avec le jeu de donnees.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from census import parse_count
from odoo_client import CATEGORIES, PoliteClient, browse_url

# Categories standard d'Odoo et variantes plausibles. Sonder large coute peu
# (une requete chacune) et rate moins qu'une liste prudente.
CANDIDATES = sorted(set(CATEGORIES + [
    "Tools", "Services", "Technical", "Uncategorized", "Administration",
    "Hidden", "Theme", "Themes", "Generic Modules", "Inventory", "CRM",
    "Helpdesk", "Field Service", "Maintenance", "Quality", "Fleet", "Events",
    "Timesheets", "Knowledge", "Sign", "Studio", "Internet of Things", "IoT",
    "Lunch", "Mass Mailing", "Notes", "Repair", "Subscription",
    "Subscriptions", "Website Theme", "Accounting/Localizations",
    "Human Resources/Employees", "Manufacturing/Manufacturing",
    "Sales/Sales", "Finance", "Payroll", "Recruitment", "Appraisals",
    "Time Off", "Expenses", "Invoicing", "Purchase", "Planning",
    "Appointment", "Surveys", "Social Marketing", "Email Marketing",
    "SMS Marketing", "Marketing Automation", "eLearning", "Forum", "Blog",
    "Live Chat", "Rental", "PLM", "Barcode", "Data Cleaning", "Spreadsheet",
    "Dashboards", "Reporting", "Localisation", "Connector", "Integration",
    "Payment", "Payment Providers", "Shipping", "Delivery", "Education",
    "Healthcare", "Real Estate", "Construction", "Restaurant", "Hotel",
    "Agriculture", "Transport", "Logistics", "Nonprofit", "Government",
    "Artificial Intelligence", "Security", "Extra Rights", "Usability",
    "Customizations", "Migration", "Backup", "API", "Mobile", "Other",
    "Others", "Miscellaneous", "Utilities", "Widgets", "Themes/Backend",
    "Point Of Sale", "Ecommerce", "Discuss/Discuss", "VoIP", "WhatsApp",
    "Documents", "Approvals", "Frontend", "Backend", "Portal", "Accounting/Accounting",
]))


def run(out_path: Path, delay: float = 2.0) -> None:
    client = PoliteClient(cache_dir="data/raw/cache_probe", delay=delay)
    found = []
    for i, name in enumerate(CANDIDATES, 1):
        url = browse_url(category=name)
        html = client.get(url)
        count = parse_count(html) if html else None
        status = "-" if not count else str(count)
        print(f"[{i:3d}/{len(CANDIDATES)}] {name:<28} {status}", flush=True)
        if count:
            found.append({"category": name, "n_modules": count, "url": url})

    found.sort(key=lambda r: -r["n_modules"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["category", "n_modules", "url"])
        writer.writeheader()
        writer.writerows(found)

    total = sum(r["n_modules"] for r in found)
    print(f"\nCategories non vides : {len(found)}")
    print(f"Somme des effectifs  : {total:,}")
    print(f"Ecrit : {out_path}")


if __name__ == "__main__":
    run(Path("data/interim/categories_found.csv"))
