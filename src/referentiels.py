"""Dictionnaires officiels du Registre foncier du Québec.

Source : Ministère des Ressources naturelles et des Forêts, *Statistiques du
Registre foncier du Québec sur le marché immobilier*, Données Québec.
Les libellés de plages de prix sont ceux publiés sur quebec.ca.
"""

from __future__ import annotations

# Codes à deux chiffres, identiques à ceux de Statistique Québec.
REGIONS_ADMINISTRATIVES: dict[str, str] = {
    "01": "Bas-Saint-Laurent",
    "02": "Saguenay–Lac-Saint-Jean",
    "03": "Capitale-Nationale",
    "04": "Mauricie",
    "05": "Estrie",
    "06": "Montréal",
    "07": "Outaouais",
    "08": "Abitibi-Témiscamingue",
    "09": "Côte-Nord",
    "10": "Nord-du-Québec",
    "11": "Gaspésie–Îles-de-la-Madeleine",
    "12": "Chaudière-Appalaches",
    "13": "Laval",
    "14": "Lanaudière",
    "15": "Laurentides",
    "16": "Montérégie",
    "17": "Centre-du-Québec",
}

# Confirmé en recoupant les totaux d'août 2026 du fichier avec quebec.ca.
PLAGES_PRIX: dict[str, str] = {
    "1": "Moins de 250 000 $",
    "2": "De 250 000 $ à 500 000 $",
    "3": "Plus de 500 000 $",
}

# Ce fichier ne contient que les actes de vente (code 001).
NATURES_ACTE: dict[str, str] = {
    "001": "Vente",
}

RENOMMAGE_COLONNES: dict[str, str] = {
    "dt_debut_mois": "periode",
    "id_regn_admin": "id_region",
    "cd_plage_prix": "code_plage_prix",
    "cd_natr_acte_jurdq": "code_nature_acte",
    "nb_reqst": "nombre_ventes",
}

CLES_UNICITE: tuple[str, ...] = (
    "periode",
    "id_region",
    "code_plage_prix",
    "code_nature_acte",
)

# La région 10 est ventilée dans les régions 02, 08 et 09 par le producteur.
REGION_ABSENTE = "10"
