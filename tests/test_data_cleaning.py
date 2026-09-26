import pandas as pd
import pytest

from src.data_cleaning import (
    decoder_referentiels,
    nettoyer_ventes,
    normaliser_code,
    normaliser_colonnes,
    normaliser_nom,
    supprimer_doublons,
    vers_numerique,
)


@pytest.mark.parametrize(
    ("libelle", "attendu"),
    [
        ("DT_DEBUT_MOIS", "dt_debut_mois"),
        ("ID_REGN_ADMIN", "id_regn_admin"),
        ("CD_PLAGE_PRIX", "cd_plage_prix"),
        ("NB_REQST", "nb_reqst"),
        ("Prix médian", "prix_median"),
        ("  Région   administrative ", "region_administrative"),
    ],
)
def test_normaliser_nom(libelle, attendu):
    assert normaliser_nom(libelle) == attendu


def test_normaliser_colonnes_preserve_les_valeurs():
    df = pd.DataFrame({"NB_REQST": [1], "CD_PLAGE_PRIX": [2]})

    resultat = normaliser_colonnes(df)

    assert list(resultat.columns) == ["nb_reqst", "cd_plage_prix"]
    assert resultat.iloc[0].tolist() == [1, 2]


def test_vers_numerique_gere_les_formats_locaux():
    serie = pd.Series(["1 234", "2\u00a0500,50", "$3,75", "12 %", "-", ""])

    resultat = vers_numerique(serie)

    assert resultat.iloc[0] == 1234
    assert resultat.iloc[1] == 2500.50
    assert resultat.iloc[2] == 3.75
    assert resultat.iloc[3] == 12
    assert resultat.isna().tolist() == [False, False, False, False, True, True]


def test_vers_numerique_laisse_passer_une_serie_deja_numerique():
    serie = pd.Series([1.5, 2.5])

    assert vers_numerique(serie) is serie


def test_normaliser_code_complete_et_nettoie():
    serie = pd.Series(["1", "01", "6.0", " 7 "])

    assert normaliser_code(serie, 2).tolist() == ["01", "01", "06", "07"]


def test_supprimer_doublons_conserve_la_derniere_revision():
    df = pd.DataFrame(
        {
            "periode": ["2024-01", "2024-01", "2024-02"],
            "nombre_ventes": [100, 105, 120],
        }
    )

    resultat = supprimer_doublons(df, cles=["periode"])

    assert resultat["periode"].tolist() == ["2024-01", "2024-02"]
    assert resultat["nombre_ventes"].tolist() == [105, 120]


def test_decoder_referentiels_ajoute_les_libelles():
    df = pd.DataFrame(
        {
            "id_region": ["06"],
            "code_plage_prix": ["3"],
            "code_nature_acte": ["001"],
        }
    )

    resultat = decoder_referentiels(df)

    assert resultat["region"].iloc[0] == "Montréal"
    assert resultat["plage_prix"].iloc[0] == "Plus de 500 000 $"
    assert resultat["nature_acte"].iloc[0] == "Vente"


def test_nettoyer_ventes_de_bout_en_bout():
    df = pd.DataFrame(
        {
            "DT_DEBUT_MOIS": ["2026-08-01", "2026-08-01", "2026-07-01"],
            "ID_REGN_ADMIN": ["6", "06", "06"],
            "CD_PLAGE_PRIX": ["3", "3", "1"],
            "CD_NATR_ACTE_JURDQ": ["001", "001", "001"],
            "NB_REQST": ["1 114", "1114", "112"],
        }
    )

    resultat = nettoyer_ventes(df)

    assert list(resultat.columns) == [
        "periode",
        "id_region",
        "code_plage_prix",
        "code_nature_acte",
        "nombre_ventes",
        "region",
        "plage_prix",
        "nature_acte",
    ]
    assert len(resultat) == 2
    aout = resultat.loc[resultat["periode"] == "2026-08-01"].iloc[0]
    assert aout["id_region"] == "06"
    assert aout["region"] == "Montréal"
    assert aout["plage_prix"] == "Plus de 500 000 $"
    assert aout["nombre_ventes"] == 1114
