# Analyse du marché immobilier québécois

Analyse des ventes inscrites au Registre foncier du Québec, par région
administrative et par plage de prix : exploration, tests statistiques et
prévision du volume à un mois.

## Données

Le fichier source est `data/raw/donn_prix_vente_reqst.csv`, publié par le
Ministère des Ressources naturelles et des Forêts sur
[Données Québec](https://www.donneesquebec.ca/recherche/dataset/statistiques-du-registre-foncier-du-quebec-sur-le-marche-immobilier)
(CC-BY 4.0).

Chaque ligne est le nombre de ventes d'un mois, d'une région et d'une plage
de prix. Les ventes couvrent tous les types de propriétés. Dictionnaire
complet : [docs/dictionnaire_donnees.md](docs/dictionnaire_donnees.md).

| Code | Plage de prix |
| --- | --- |
| 1 | Moins de 250 000 $ |
| 2 | De 250 000 $ à 500 000 $ |
| 3 | Plus de 500 000 $ |

La région 10 (Nord-du-Québec) est absente : le producteur la ventile dans
les régions 02, 08 et 09.

## Structure

```
projet-marche-immobilier-quebec/
├── data/
│   ├── raw/donn_prix_vente_reqst.csv
│   └── processed/
├── notebooks/
├── src/
├── outputs/
├── docs/
└── tests/
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Utilisation

Exécuter les notebooks dans l'ordre. Chacun consomme la sortie du précédent.

| Notebook | Rôle | Produit |
| --- | --- | --- |
| `01_data_understanding` | Décrire le fichier sans le modifier | Constats |
| `02_data_cleaning` | Typer, décoder, contrôler | `data/processed/ventes_plage_prix_propre.csv` |
| `03_exploratory_data_analysis` | Distributions, régions, saisonnalité | `outputs/figures/03_*.png` |
| `04_statistical_analysis` | Tests d'hypothèses | `outputs/figures/04_*.png` |
| `05_feature_engineering` | Retards par série région × plage | `data/processed/features.csv` |
| `06_modeling` | Comparer les modèles | `outputs/models/best_model.pkl` |
| `07_prediction` | Prévoir le mois suivant | `outputs/predictions/predictions.csv` |

Le notebook `02` recoupe les totaux d'août 2026 avec la publication officielle
de quebec.ca (12 266 ventes).

## Choix méthodologiques

**Découpage chronologique.** Les jeux d'entraînement et de test sont séparés
par une date. Un découpage aléatoire laisserait le modèle voir le futur.

**Variables décalées uniquement.** Toutes les variables du notebook `05` sont
construites par `shift` à l'intérieur de chaque série (région × plage).

**Référence de persistance.** Un modèle qui ne bat pas « le mois prochain
égale le mois courant » n'apporte rien.

## Tests

```powershell
pytest
```

## Licence

MIT — voir [LICENSE](LICENSE). Les données restent sous licence CC-BY 4.0 du
Registre foncier du Québec.
