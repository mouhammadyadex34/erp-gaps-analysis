"""Nettoyage du corpus brut des fiches modules.

Chaque decision est commentee, parce qu'aucune n'est neutre.

Unite d'observation
-------------------
Une ligne = un couple (module, serie Odoo). Le meme module publie pour six
series donne six lignes. C'est un choix, pas une fatalite : il permet de
mesurer l'offre disponible pour une version donnee, ce qui est la question du
projet. Pour compter les modules distincts, on deduplique sur `technical_name`.

Doublons
--------
Un meme couple (nom technique, serie) peut apparaitre deux fois si le module
est range dans plusieurs categories. On ne le supprime pas a l'aveugle : on
garde la premiere occurrence pour les analyses par module, et on conserve la
trace des categories multiples dans `n_categories`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

# Suffixes juridiques et commerciaux a retirer pour rapprocher
# « Cybrosys Techno Solutions » de « Cybrosys Techno Solutions Pvt. Ltd. ».
LEGAL_SUFFIXES = re.compile(
    r"\b(pvt\.?|private|ltd\.?|limited|llp|llc|inc\.?|incorporated|gmbh|"
    r"s\.?a\.?r\.?l\.?|sarl|sas|s\.?a\.?|bv|b\.?v\.?|nv|oy|ab|as|aps|srl|"
    r"s\.?r\.?l\.?|co\.?|corp\.?|corporation|company|technologies|technology|"
    r"solutions|software|systems|it|group|holding)\b",
    re.IGNORECASE)


def normalize_author(name: str) -> str:
    """Forme canonique d'un nom d'editeur, pour le comptage.

    On retire ponctuation et suffixes juridiques, on abaisse la casse. C'est
    une heuristique : elle rapproche des variantes d'un meme editeur, mais elle
    peut aussi fusionner deux editeurs aux noms proches. On conserve donc
    toujours le nom d'origine a cote.
    """
    if not isinstance(name, str):
        return ""
    text = name.lower()
    # Les suffixes passent AVANT le retrait de la ponctuation : « s.a. » n'est
    # plus reconnaissable une fois les points effaces (il devient « s a »).
    # On repasse ensuite, pour les variantes ecrites sans points (« sarl »).
    text = LEGAL_SUFFIXES.sub(" ", text)
    text = re.sub(r"[.,&()/|]+", " ", text)
    text = LEGAL_SUFFIXES.sub(" ", text)
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    # Un token d'une seule lettre survivant a ce traitement est un residu de
    # sigle (« s », « a ») et non un nom.
    text = " ".join(t for t in text.split() if len(t) > 1)
    return re.sub(r"\s+", " ", text).strip()


def series_sort_key(series: str) -> float:
    """Ordonne « 9.0 » avant « 10.0 », et place « saas-19.4 » apres « 19.0 »."""
    if not isinstance(series, str):
        return -1.0
    match = re.search(r"(\d+)\.(\d+)", series)
    if not match:
        return -1.0
    major, minor = int(match.group(1)), int(match.group(2))
    return major + minor / 100 + (0.001 if series.startswith("saas") else 0.0)


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    # --- Types ---------------------------------------------------------
    for col in ("price_value", "n_downloads", "n_purchases", "n_last_month"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["is_free"] = df["is_free"].astype(str).str.lower().isin(["true", "1"])

    # --- Categories multiples -------------------------------------------
    # Avant toute deduplication : un module range dans plusieurs categories
    # est une information, pas une erreur.
    key = ["technical_name", "series"]
    df["n_categories"] = df.groupby(key)["source_category"].transform("nunique")
    df["categories_all"] = (df.groupby(key)["source_category"]
                            .transform(lambda s: " | ".join(sorted(set(s)))))

    before = len(df)
    df = df.drop_duplicates(subset=key, keep="first").reset_index(drop=True)
    print(f"Doublons (module, serie) retires : {before - len(df)} "
          f"sur {before} ({(before - len(df)) / before * 100:.1f} %)")

    # --- Editeurs -------------------------------------------------------
    df["author_clean"] = df["author"].map(normalize_author)
    # Un nom vide apres normalisation signale un editeur au nom entierement
    # compose de suffixes ; on retombe sur le nom brut plutot que de perdre
    # la ligne.
    empty = df["author_clean"] == ""
    df.loc[empty, "author_clean"] = df.loc[empty, "author"].fillna("").str.lower()

    # --- Prix -----------------------------------------------------------
    # Un module gratuit a un prix de 0, pas un prix manquant. Un module payant
    # sans montant lisible garde NaN : on ne devine pas.
    df.loc[df["is_free"], "price_value"] = 0.0
    df["price_missing"] = (~df["is_free"]) & df["price_value"].isna()

    # --- Usage ----------------------------------------------------------
    # Telechargements et achats ne sont pas la meme grandeur et ne doivent pas
    # etre additionnes. On expose les deux et un indicateur du type mesure.
    df["usage_kind"] = df.apply(
        lambda r: "downloads" if pd.notna(r["n_downloads"])
        else ("purchases" if pd.notna(r["n_purchases"]) else "none"), axis=1)

    # --- Series ---------------------------------------------------------
    df["series_order"] = df["series"].map(series_sort_key)
    df["is_saas"] = df["series_kind"].eq("saas")

    # --- Descriptions ----------------------------------------------------
    df["summary"] = df["summary"].fillna("").str.strip()
    df["summary_len"] = df["summary"].str.len()
    df["summary_missing"] = df["summary_len"].eq(0)
    # Le resume des cartes est souvent gonfle de mots-cles SEO separes par
    # « Search Keywords: ». On isole la partie redactionnelle : c'est elle qui
    # decrit le besoin, le reste decrit une strategie de referencement.
    split = df["summary"].str.split(r"(?i)\|?\s*search keywords\s*:", n=1,
                                    regex=True)
    df["summary_prose"] = split.str[0].str.strip()
    df["has_seo_keywords"] = split.str.len().gt(1)

    return df


def report(df: pd.DataFrame) -> None:
    print(f"\nLignes (module x serie) : {len(df):,}")
    print(f"Modules distincts       : {df.technical_name.nunique():,}")
    print(f"Editeurs (brut)         : {df.author.nunique():,}")
    print(f"Editeurs (normalises)   : {df.author_clean.nunique():,}")
    print(f"Series                  : {df.series.nunique()} "
          f"(dont saas : {df.is_saas.sum():,} lignes)")
    print(f"Gratuits                : {df.is_free.mean() * 100:.1f} %")
    print(f"Prix manquant (payants) : {df.price_missing.sum():,}")
    print(f"Resume vide             : {df.summary_missing.sum():,}")
    print(f"Resume avec mots-cles SEO : {df.has_seo_keywords.mean() * 100:.1f} %")
    print(f"Range dans >1 categorie : {(df.n_categories > 1).mean() * 100:.1f} %")


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw/modules_raw.csv")
    dst = Path(sys.argv[2] if len(sys.argv) > 2
               else "data/processed/modules_clean.csv")
    raw = pd.read_csv(src)
    print(f"Lu : {src} ({len(raw):,} lignes)")
    df = clean(raw)
    report(df)
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dst, index=False)
    print(f"\nEcrit : {dst}")


if __name__ == "__main__":
    main()
