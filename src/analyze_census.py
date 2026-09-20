"""Lecture de la matrice categorie x serie : manques combles, manques persistants.

Le piege de cette analyse est de comparer des effectifs bruts entre versions.
On ne peut pas : le nombre total de modules croit fortement d'une serie a
l'autre (le marche grandit, et les series recentes concentrent l'effort de
portage des editeurs). Une categorie peut doubler en valeur absolue tout en
perdant du terrain.

On raisonne donc en **part de l'offre d'une serie donnee**. Si la part des
modules comptables passe de 20 % en 12.0 a 10 % en 19.0, l'editeur a absorbe
une partie du besoin. Si elle reste plate, le manque est structurel.

Deux reserves, a garder dans l'interpretation :

- La serie la plus recente est encore en cours de remplissage : son profil
  n'est pas comparable a celui d'une serie mature. On la signale.
- Les series anciennes (5.0 a 8.0) portent de trop petits effectifs pour que
  les parts soient stables. On les exclut des tendances.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ALL = "__ALL__"
# En deca de ce nombre de modules, une part n'est pas interpretable.
MIN_SERIES_TOTAL = 500


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["n_modules"] = pd.to_numeric(df["n_modules"], errors="coerce")
    return df


def matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Effectifs par categorie (lignes) x serie (colonnes), agregats exclus."""
    cells = df[(df.category != ALL) & (df.series != ALL)]
    out = cells.pivot(index="category", columns="series", values="n_modules")
    order = sorted(out.columns, key=lambda s: float(s))
    return out[order]


def coherence(df: pd.DataFrame) -> pd.DataFrame:
    """Compare la somme des cellules aux agregats annonces par le site.

    Un ecart n'est pas forcement une erreur de collecte : un module peut etre
    range dans plusieurs categories, ou dans aucune des 18 de premier niveau.
    Mais l'ecart doit etre mesure et publie, pas ignore.
    """
    mat = matrix(df)
    declared = (df[(df.category == ALL) & (df.series != ALL)]
                .set_index("series")["n_modules"])
    summed = mat.sum(axis=0)
    out = pd.DataFrame({"somme_categories": summed,
                        "total_annonce": declared.reindex(summed.index)})
    out["ecart"] = out.somme_categories - out.total_annonce
    out["ecart_pct"] = (out.ecart / out.total_annonce * 100).round(1)
    return out


def shares(df: pd.DataFrame) -> pd.DataFrame:
    """Part de chaque categorie dans l'offre de sa serie, en %."""
    mat = matrix(df)
    keep = mat.columns[mat.sum(axis=0) >= MIN_SERIES_TOTAL]
    mat = mat[keep]
    return (mat / mat.sum(axis=0) * 100).round(2)


def trends(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Variation de part entre deux series, triee du plus comble au plus tenace."""
    sh = shares(df)
    if start not in sh.columns or end not in sh.columns:
        raise KeyError(f"series absentes ou trop petites : {start}, {end}")
    out = pd.DataFrame({
        f"part_{start}": sh[start],
        f"part_{end}": sh[end],
    })
    out["variation_pts"] = (out[f"part_{end}"] - out[f"part_{start}"]).round(2)
    out["variation_rel_pct"] = (
        (out[f"part_{end}"] / out[f"part_{start}"] - 1) * 100).round(1)
    return out.sort_values("variation_pts")


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1
                else "data/interim/census_category_series.csv")
    df = load(path)

    mat = matrix(df)
    print("=" * 78)
    print("EFFECTIFS  categorie x serie")
    print("=" * 78)
    print(mat.fillna(0).astype(int).to_string())

    print("\n" + "=" * 78)
    print("CONTROLE DE COHERENCE  somme des categories vs total annonce")
    print("=" * 78)
    print(coherence(df).to_string())

    sh = shares(df)
    print("\n" + "=" * 78)
    print(f"PARTS (%)  series d'au moins {MIN_SERIES_TOTAL} modules")
    print("=" * 78)
    print(sh.to_string())

    usable = list(sh.columns)
    if len(usable) >= 2:
        # On s'arrete a l'avant-derniere serie : la plus recente est encore en
        # cours de remplissage et sa structure n'est pas stabilisee.
        start, end = usable[0], usable[-2] if len(usable) > 2 else usable[-1]
        print("\n" + "=" * 78)
        print(f"TENDANCES  {start} -> {end}  (part de l'offre, en points)")
        print("=" * 78)
        print(trends(df, start, end).to_string())
        print(f"\nNote : serie {usable[-1]} exclue du calcul de tendance "
              "(encore en cours de remplissage).")


if __name__ == "__main__":
    main()
