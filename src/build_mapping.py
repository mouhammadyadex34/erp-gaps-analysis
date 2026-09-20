"""Table de correspondance : 111 categories du site -> 17 fonctions metier.

Pourquoi cette table existe
---------------------------
La taxonomie de l'Apps Store n'a pas ete concue pour l'analyse. Elle contient
des quasi-doublons (`Purchase` / `Purchases`, `Inventory` / `Warehouse`,
`Localization` / `Localisation`, `Other` / `Others`), des rubriques fourre-tout
(`Tools` et `Extra Tools`, 24 205 modules a elles deux) et des categories de
trois modules. Compter par categorie brute reviendrait a mesurer les habitudes
de rangement des editeurs plutot que la structure du besoin.

Le statut de cette table
------------------------
C'est une **interpretation**, pas une verite. Un autre analyste regrouperait
autrement, et les resultats bougeraient. Elle est donc versionnee comme une
donnee, pas enfouie dans du code : `data/processed/category_mapping.csv` se
relit, se conteste et se modifie sans toucher aux scripts.

Deux choix a signaler explicitement dans le document final :

- `Tools` et `Extra Tools` sont classees en « Outils transverses » et non
  reparties de force. Leur poids (27 % du catalogue) est un resultat en soi :
  il dit que le besoin le plus massif est celui que la taxonomie ne sait pas
  nommer. Les diluer effacerait ce constat.
- `Uncategorized`, `Other`, `Others` et `Hidden` restent groupees en
  « Non renseigne » plutot que d'etre supprimees : leur volume mesure la
  qualite du rangement, et les retirer gonflerait artificiellement les autres.
"""

from __future__ import annotations

import csv
from pathlib import Path

# fonction metier -> categories du site
GROUPS: dict[str, list[str]] = {
    "Comptabilite & finance": [
        "Accounting", "Finance", "Invoicing", "Payment", "Payment Providers",
        "Expenses",
    ],
    "Ventes & CRM": [
        "Sales", "CRM", "Subscription", "Subscriptions", "Rental",
        "Appointment",
    ],
    "Achats": ["Purchase", "Purchases"],
    "Point de vente": ["Point Of Sale", "Restaurant"],
    "Logistique & stocks": [
        "Inventory", "Warehouse", "Delivery", "Shipping", "Logistics",
        "Transport", "Barcode",
    ],
    "Production": ["Manufacturing", "PLM", "Quality", "Maintenance", "Repair"],
    "Ressources humaines": [
        "Human Resources", "Payroll", "Time Off", "Recruitment", "Timesheets",
        "Appraisals", "Lunch", "Fleet",
    ],
    "Site web & e-commerce": [
        "Website", "Ecommerce", "Blog", "Forum", "Theme", "Website Theme",
        "Frontend", "Portal",
    ],
    "Marketing": [
        "Marketing", "Social Marketing", "Email Marketing", "SMS Marketing",
        "Marketing Automation", "Mass Mailing", "Events", "Surveys",
    ],
    "Projets & services": [
        "Project", "Services", "Field Service", "Helpdesk", "Planning",
    ],
    "Collaboration & documents": [
        "Productivity", "Discuss", "Documents", "Document Management",
        "Knowledge", "Sign", "Notes", "Approvals", "WhatsApp", "VoIP",
        "Live Chat", "eLearning",
    ],
    "Decisionnel & reporting": [
        "Reporting", "Dashboards", "Spreadsheet", "Data Cleaning",
    ],
    "Localisation & conformite": ["Localization", "Localisation"],
    "Verticaux sectoriels": [
        "Industries", "Education", "Real Estate", "Agriculture",
        "Construction", "Healthcare", "Hotel", "Government", "Nonprofit",
    ],
    "Integrations & connecteurs": [
        "Connector", "Integration", "IoT", "Internet of Things",
        "Artificial Intelligence", "API",
    ],
    "Outils transverses & technique": [
        "Tools", "Extra Tools", "Technical", "Administration",
        "Generic Modules", "Customizations", "Security", "Usability",
        "Extra Rights", "Backend", "Utilities", "Migration", "Backup",
        "Mobile", "Widgets", "Studio",
    ],
    "Non renseigne": [
        "Uncategorized", "Other", "Others", "Hidden", "Tutorial",
    ],
}


def build(categories_path: Path, out_path: Path) -> None:
    with categories_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    counts = {r["category"]: int(r["n_modules"]) for r in rows}

    lookup: dict[str, str] = {}
    for function, members in GROUPS.items():
        for category in members:
            if category in lookup:
                raise ValueError(
                    f"{category!r} affectee deux fois : "
                    f"{lookup[category]!r} et {function!r}")
            lookup[category] = function

    # Toute categorie du site doit etre affectee, et toute categorie de la
    # table doit exister sur le site. Les deux controles echouent bruyamment :
    # une categorie oubliee disparaitrait silencieusement des totaux.
    missing = sorted(set(counts) - set(lookup))
    unknown = sorted(set(lookup) - set(counts))
    if missing:
        raise ValueError(f"categories du site non affectees : {missing}")
    if unknown:
        raise ValueError(f"categories inconnues du site : {unknown}")

    out = [{"category": c, "fonction": lookup[c], "n_modules": counts[c]}
           for c in sorted(counts, key=lambda c: (-counts[c], c))]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["category", "fonction", "n_modules"])
        writer.writeheader()
        writer.writerows(out)

    total = sum(counts.values())
    print(f"{len(counts)} categories -> {len(GROUPS)} fonctions")
    print(f"Total conserve : {total:,}\n")

    per_function: dict[str, int] = {}
    for row in out:
        per_function[row["fonction"]] = \
            per_function.get(row["fonction"], 0) + row["n_modules"]
    width = max(len(f) for f in per_function)
    for function, n in sorted(per_function.items(), key=lambda kv: -kv[1]):
        bar = "#" * round(n / total * 60)
        print(f"  {function:<{width}} {n:>7,}  {n / total * 100:5.1f} %  {bar}")
    assert sum(per_function.values()) == total, "perte au regroupement"
    print(f"\nEcrit : {out_path}")


if __name__ == "__main__":
    build(Path("data/processed/categories.csv"),
          Path("data/processed/category_mapping.csv"))
