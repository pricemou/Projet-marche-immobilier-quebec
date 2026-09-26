"""Nettoyage du fichier `donn_prix_vente_reqst.csv`."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

from src.referentiels import (
    CLES_UNICITE,
    NATURES_ACTE,
    PLAGES_PRIX,
    REGIONS_ADMINISTRATIVES,
    RENOMMAGE_COLONNES,
)

_ESPACES = "\u00a0\u202f\u2009 "
_SENTINELLES = {"", "-", "--", "n/d", "nd", "n/a", "na", "s/o"}


def normaliser_nom(nom: str) -> str:
    """Transforme un libellé de colonne en identifiant `snake_case` sans accent."""
    sans_accent = unicodedata.normalize("NFKD", str(nom))
    sans_accent = "".join(c for c in sans_accent if not unicodedata.combining(c))
    sans_accent = sans_accent.replace("$", "dollar").replace("%", "pct")
    snake = re.sub(r"[^0-9a-zA-Z]+", "_", sans_accent).strip("_").lower()
    return re.sub(r"_+", "_", snake)


def normaliser_colonnes(df: pd.DataFrame) -> pd.DataFrame:
    """Renomme toutes les colonnes en `snake_case`."""
    return df.rename(columns={c: normaliser_nom(c) for c in df.columns})


def vers_numerique(serie: pd.Series) -> pd.Series:
    """Convertit une série texte en nombres.

    Retire les séparateurs de milliers, les symboles monétaires et de
    pourcentage, puis remplace la virgule décimale par un point. Les valeurs
    non convertibles deviennent `NaN`.
    """
    if pd.api.types.is_numeric_dtype(serie):
        return serie

    texte = serie.astype("string")
    for espace in _ESPACES:
        texte = texte.str.replace(espace, "", regex=False)
    texte = texte.str.replace(r"[$%]", "", regex=True)
    texte = texte.str.replace(",", ".", regex=False)
    texte = texte.mask(texte.str.lower().isin(_SENTINELLES).fillna(False))
    return pd.to_numeric(texte, errors="coerce")


def normaliser_code(serie: pd.Series, largeur: int) -> pd.Series:
    """Retire les espaces et complète un code numérique à largeur fixe."""
    texte = serie.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    return texte.str.zfill(largeur)


def supprimer_doublons(df: pd.DataFrame, cles: list[str] | None = None) -> pd.DataFrame:
    """Supprime les doublons en conservant la dernière occurrence.

    La dernière occurrence est retenue car les exports successifs révisent les
    périodes déjà publiées.
    """
    return df.drop_duplicates(subset=cles, keep="last").reset_index(drop=True)


def decoder_referentiels(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les libellés officiels à partir des codes."""
    decode = df.copy()
    if "id_region" in decode.columns:
        decode["region"] = decode["id_region"].map(REGIONS_ADMINISTRATIVES)
    if "code_plage_prix" in decode.columns:
        decode["plage_prix"] = decode["code_plage_prix"].map(PLAGES_PRIX)
    if "code_nature_acte" in decode.columns:
        decode["nature_acte"] = decode["code_nature_acte"].map(NATURES_ACTE)
    return decode


def nettoyer_ventes(df: pd.DataFrame) -> pd.DataFrame:
    """Produit la table d'analyse à partir de l'export brut du Registre foncier."""
    propre = normaliser_colonnes(df).rename(columns=RENOMMAGE_COLONNES)

    if "periode" in propre.columns:
        propre["periode"] = pd.to_datetime(propre["periode"], errors="coerce")
    if "id_region" in propre.columns:
        propre["id_region"] = normaliser_code(propre["id_region"], 2)
    if "code_plage_prix" in propre.columns:
        propre["code_plage_prix"] = normaliser_code(propre["code_plage_prix"], 1)
    if "code_nature_acte" in propre.columns:
        propre["code_nature_acte"] = normaliser_code(propre["code_nature_acte"], 3)
    if "nombre_ventes" in propre.columns:
        propre["nombre_ventes"] = vers_numerique(propre["nombre_ventes"]).astype("Int64")

    propre = decoder_referentiels(propre)

    cles = [c for c in CLES_UNICITE if c in propre.columns]
    propre = supprimer_doublons(propre, cles=cles or None)
    return propre.sort_values(cles or propre.columns.tolist()).reset_index(drop=True)
