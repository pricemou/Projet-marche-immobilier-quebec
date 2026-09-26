# Dictionnaire des données

Source : Ministère des Ressources naturelles et des Forêts,
*Statistiques du Registre foncier du Québec sur le marché immobilier*,
fichier `donn_prix_vente_reqst.csv`, [Données Québec](https://www.donneesquebec.ca/recherche/dataset/statistiques-du-registre-foncier-du-quebec-sur-le-marche-immobilier)
(licence CC-BY 4.0).

Les libellés de plages de prix et les précisions méthodologiques sont ceux
publiés sur [quebec.ca](https://www.quebec.ca/habitation-territoire/information-fonciere/statistiques-marche-immobilier).

## Grain

Une ligne = un mois × une région administrative × une plage de prix.

Couverture du fichier local : janvier 2021 à août 2026.

## Colonnes sources

| Colonne | Nom d'analyse | Description |
| --- | --- | --- |
| `DT_DEBUT_MOIS` | `periode` | Premier jour du mois d'inscription de l'acte |
| `ID_REGN_ADMIN` | `id_region` | Code de région administrative (01 à 17) |
| `CD_PLAGE_PRIX` | `code_plage_prix` | Plage de prix de la vente |
| `CD_NATR_ACTE_JURDQ` | `code_nature_acte` | Nature de l'acte juridique |
| `NB_REQST` | `nombre_ventes` | Nombre de ventes inscrites |

## Plages de prix

Recoupées avec les totaux officiels d'août 2026 (12 266 ventes).

| Code | Libellé | Total août 2026 |
| --- | --- | ---: |
| `1` | Moins de 250 000 $ | 2 799 |
| `2` | De 250 000 $ à 500 000 $ | 4 496 |
| `3` | Plus de 500 000 $ | 4 971 |

## Nature d'acte

| Code | Libellé |
| --- | --- |
| `001` | Vente |

Ce fichier ne contient que les actes de vente.

## Régions administratives

La région **10 — Nord-du-Québec** n'apparaît pas : le producteur la ventile
dans les régions 02, 08 et 09, parce que ses circonscriptions foncières
chevauchent ces trois régions.

| Code | Région |
| --- | --- |
| 01 | Bas-Saint-Laurent |
| 02 | Saguenay–Lac-Saint-Jean |
| 03 | Capitale-Nationale |
| 04 | Mauricie |
| 05 | Estrie |
| 06 | Montréal |
| 07 | Outaouais |
| 08 | Abitibi-Témiscamingue |
| 09 | Côte-Nord |
| 10 | Nord-du-Québec *(absent du fichier)* |
| 11 | Gaspésie–Îles-de-la-Madeleine |
| 12 | Chaudière-Appalaches |
| 13 | Laval |
| 14 | Lanaudière |
| 15 | Laurentides |
| 16 | Montérégie |
| 17 | Centre-du-Québec |

## Précisions du producteur

- Un acte peut créer plusieurs droits de même nature ; seul le premier droit
  de l'acte est comptabilisé.
- Les ventes regroupent tous les types de propriétés (unifamiliale, plex,
  condo, etc.).
- Les données régionales reposent sur l'association des circonscriptions
  foncières, pas sur les limites administratives strictes.
