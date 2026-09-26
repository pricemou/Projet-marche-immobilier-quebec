# Project Summary — Analyse du marché immobilier québécois

Document de vérité du projet. Toute statistique ci-dessous est traçable vers un notebook, un fichier de données ou un fichier de sortie. Les interprétations sont séparées des observations. Si un chiffre n’apparaît pas dans le projet, il est marqué « Non disponible dans le projet ».

---

## 1. Vue d'ensemble

- **Nom du projet** : Analyse du marché immobilier québécois (`Projet-marche-immobilier-quebec`).
- **Domaine / secteur** : immobilier résidentiel et non résidentiel confondus ; statistiques du Registre foncier du Québec.
- **Objectif général** : explorer les ventes inscrites par région administrative et plage de prix, tester des hypothèses statistiques, puis prévoir le volume de ventes à un mois (`README.md`).
- **Problématique principale** : peut-on caractériser, tester et prévoir le nombre de ventes inscrites au Registre foncier, au grain mois × région × plage de prix ?
- **Questions auxquelles le projet cherche à répondre** (notebooks `03` et `04`) :
  1. Comment les ventes se répartissent-elles entre les trois plages de prix ?
  2. Le volume québécois suit-il une tendance ou un cycle ?
  3. La part des ventes de plus de 500 000 $ progresse-t-elle ?
  4. Quelles régions portent le marché, et où le haut de gamme est-il dominant ?
  5. Observe-t-on une saisonnalité mensuelle ?
  6. Ces écarts sont-ils statistiquement détectables (normalité, saison, égalité des plages, tendance) ?
  7. Un modèle peut-il battre une prévision de persistance (« le mois suivant = le mois courant ») ?

---

## 2. Source des données

- **Source officielle** : Ministère des Ressources naturelles et des Forêts, *Statistiques du Registre foncier du Québec sur le marché immobilier* (`docs/dictionnaire_donnees.md`, `README.md`).
- **Jeu de données** : « Nombre de vente par plage de prix », fichier `donn_prix_vente_reqst.csv`.
- **URL dans le projet** :
  - Données Québec : https://www.donneesquebec.ca/recherche/dataset/statistiques-du-registre-foncier-du-quebec-sur-le-marche-immobilier
  - Libellés / précisions : https://www.quebec.ca/habitation-territoire/information-fonciere/statistiques-marche-immobilier
- **Licence des données** : CC-BY 4.0.
- **Fichier local** : `data/raw/donn_prix_vente_reqst.csv`.
- **Période couverte** : janvier 2021 → août 2026 (68 mois distincts). Source : `notebooks/01_data_understanding.ipynb`.
- **Nombre de lignes** : 3 262 (sortie `info()` / chargement du notebook `01`).
- **Nombre de colonnes sources** : 5.
- **Principales variables sources** :

| Colonne brute | Nom d’analyse | Rôle |
| --- | --- | --- |
| `DT_DEBUT_MOIS` | `periode` | Premier jour du mois d’inscription |
| `ID_REGN_ADMIN` | `id_region` | Région administrative (01–17) |
| `CD_PLAGE_PRIX` | `code_plage_prix` | Plage de prix (1, 2, 3) |
| `CD_NATR_ACTE_JURDQ` | `code_nature_acte` | Nature d’acte (`001` = vente) |
| `NB_REQST` | `nombre_ventes` | Nombre de ventes inscrites |

- **Niveau de granularité** : une ligne = un mois × une région administrative × une plage de prix.

---

## 3. Compréhension des données

**Structure.** Un seul fichier plat. Pas de jointure entre tables. Les libellés (région, plage, nature d’acte) sont ajoutés au nettoyage via `src/referentiels.py`.

**Variable cible d’analyse / de prévision.** `nombre_ventes` (`NB_REQST`). Dans le modèle, la cible est le volume du **mois suivant** de la même série région × plage (`cible_ventes_suivantes`, notebook `05`).

**Variables catégorielles / codes.**

| Variable | Modalités observées (notebook `01`) |
| --- | --- |
| `ID_REGN_ADMIN` | 16 (la région 10 est absente) |
| `CD_PLAGE_PRIX` | 3 (`1`, `2`, `3`) |
| `CD_NATR_ACTE_JURDQ` | 1 (`001`) |

Libellés de plages, recoupés avec les totaux officiels d’août 2026 (`docs/dictionnaire_donnees.md`, notebook `02`) :

| Code | Libellé | Total août 2026 |
| --- | --- | ---: |
| 1 | Moins de 250 000 $ | 2 799 |
| 2 | De 250 000 $ à 500 000 $ | 4 496 |
| 3 | Plus de 500 000 $ | 4 971 |
|  | **Total** | **12 266** |

**Variable numérique.** `NB_REQST` : 929 valeurs distinctes dans le brut (notebook `01`). Pandas l’infère déjà en `int64` si on ne force pas `dtype=str`.

**Variable temporelle.** `DT_DEBUT_MOIS` au format `YYYY-MM-01`. 68 mois, 2021-01 → 2026-08.

**Relations entre datasets.** Un seul dataset source. Chaîne interne : brut → `ventes_plage_prix_propre.csv` → `features.csv` → `best_model.pkl` → `predictions.csv`.

**Précisions du producteur** (`docs/dictionnaire_donnees.md`) :

- seul le premier droit de l’acte est compté ;
- tous les types de propriétés sont mélangés ;
- les régions reposent sur les circonscriptions foncières ;
- la région 10 est ventilée dans les régions 02, 08 et 09.

---

## 4. Qualité des données

Source : `notebooks/01_data_understanding.ipynb` et `notebooks/02_data_cleaning.ipynb`.

| Contrôle | Résultat observé |
| --- | --- |
| Valeurs manquantes | 0 sur les 5 colonnes (0,0 %) |
| Doublons de lignes entières | 0 |
| Doublons sur la clé métier (4 codes) | 0 |
| Types | Tout lu en texte dans le `01` pour inspection. `NB_REQST` déjà convertible en entier. |
| Incohérences de codes | Région 10 absente (attendu). Nature d’acte constante. |
| Valeurs aberrantes | Non disponible dans le projet comme test formel d’outliers. `describe()` du `02` : min = 1, max = 4 100 ventes par ligne. |
| Ventes négatives après nettoyage | 0 (assertion du notebook `02`) |

**Problème rencontré en EDA (notebook `03`).** Après `read_csv`, pandas relisait `code_plage_prix` comme entier. La comparaison `.eq("3")` renvoyait tout faux : le graphique « part > 500 000 $ par région » affichait 0 %. **Action** : relire les codes en `str` et filtrer sur le libellé `Plus de 500 000 $`.

**Décisions de qualité (notebook `02`).**

| AVANT | ACTION | APRÈS |
| --- | --- | --- |
| Colonnes `DT_DEBUT_MOIS`, etc. | `normaliser_colonnes` + `RENOMMAGE_COLONNES` | `periode`, `id_region`, `code_plage_prix`, `code_nature_acte`, `nombre_ventes` |
| `periode` texte | `pd.to_datetime` | datetime |
| Codes `"6"`, `"06"` | `normaliser_code` (zfill) | `"06"` |
| `NB_REQST` texte / formats locaux | `vers_numerique` | entier (`Int64`) |
| Codes seuls | `decoder_referentiels` | colonnes `region`, `plage_prix`, `nature_acte` |
| Éventuels doublons de révision | `drop_duplicates(keep="last")` | 3 262 lignes conservées (aucun doublon observé) |
| Totaux août 2026 | Récolement quebec.ca | 12 266 = 2 799 + 4 496 + 4 971 |

Aucune ligne n’a été imputée pour la région 10.

---

## 5. Nettoyage des données

Opérations réellement dans `src/data_cleaning.py` et le notebook `02` :

- normalisation des noms de colonnes en `snake_case` ;
- renommage métier (`dt_debut_mois` → `periode`, `nb_reqst` → `nombre_ventes`, etc.) ;
- conversion de `periode` en date ;
- padding des codes (`id_region` largeur 2, `code_plage_prix` largeur 1, `code_nature_acte` largeur 3) ;
- conversion numérique de `nombre_ventes` (espaces insécables, virgule décimale, sentinelles `n/d`, `-`, etc.) ;
- décodage des référentiels ;
- dédoublonnage sur la clé d’unicité (aucune ligne retirée : 3 262 → 3 262) ;
- tri par clé ;
- contrôles : jeu non vide, pas de doublon résiduel, pas de période nulle, pas de vente négative, région 10 absente, libellés complets ;
- récolement août 2026 ;
- écriture de `data/processed/ventes_plage_prix_propre.csv`.

**Non effectué** (absent du projet) : fusion de datasets, filtrage de lignes métier, traitement de manquants (il n’y en avait pas).

---

## 6. Analyse exploratoire (EDA)

Source : `notebooks/03_exploratory_data_analysis.ipynb`. Graphiques prévus dans `outputs/figures/`.

### 6.1 Répartition par plage de prix

- **Question** : comment les ventes se répartissent-elles entre plages ?
- **Méthode** : somme de `nombre_ventes` par `plage_prix` ; part en %.
- **Résultat** (cumul 2021-01 → 2026-08) :

| Plage | Ventes | Part |
| --- | ---: | ---: |
| Moins de 250 000 $ | 364 135 | 34,67 % |
| De 250 000 $ à 500 000 $ | 398 901 | 37,98 % |
| Plus de 500 000 $ | 287 201 | 27,35 % |
| **Total** | **1 050 237** | 100 % |

- **Graphique** : `outputs/figures/03_ventes_par_plage.png`.

### 6.2 Évolution du volume total

- **Question** : le volume québécois a-t-il une tendance ou un cycle ?
- **Méthode** : somme mensuelle + moyenne mobile 12 mois.
- **Résultat chiffré de la courbe** : Non disponible dans le projet (pas de table de totaux mensuels persistée hors graphique).
- **Graphique** : `outputs/figures/03_evolution_volume_total.png`.
- **Complément** : évolution par plage — `outputs/figures/03_evolution_par_plage.png`.

### 6.3 Parts de marché dans le temps

- **Question** : la part du > 500 000 $ progresse-t-elle ?
- **Méthode** : aires empilées des parts mensuelles.
- **Résultat numérique mois par mois** : Non disponible dans le projet sous forme de table.
- **Observation liée ailleurs** : en août 2026, le > 500 000 $ = 4 971 / 12 266 ≈ 40,5 % (notebook `02` / dictionnaire), contre 27,35 % en cumul.
- **Graphique** : `outputs/figures/03_parts_de_marche.png`.

### 6.4 Géographie

- **Question** : quelles régions portent le volume ?
- **Méthode** : somme par région.
- **Résultat** (notebook `03`) :

| Région | Ventes cumulées |
| --- | ---: |
| Montérégie | 202 908 |
| Montréal | 149 127 |
| Laurentides | 120 332 |
| Capitale-Nationale | 98 350 |
| Lanaudière | 76 644 |
| Chaudière-Appalaches | 66 763 |
| Outaouais | 61 629 |
| Estrie | 48 924 |
| Saguenay–Lac-Saint-Jean | 41 700 |
| Mauricie | 40 262 |
| Laval | 36 157 |
| Centre-du-Québec | 33 167 |
| Bas-Saint-Laurent | 30 353 |
| Abitibi-Témiscamingue | 19 899 |
| Gaspésie–Îles-de-la-Madeleine | 14 484 |
| Côte-Nord | 9 538 |

- **Graphique** : `outputs/figures/03_ventes_par_region.png`.
- **Part > 500 000 $ par région** : graphique `outputs/figures/03_part_haut_de_gamme_region.png`. Valeurs numériques par région : Non disponible dans le projet (pas de table persistée après correction du filtre).

### 6.5 Saisonnalité

- **Question** : y a-t-il un cycle mensuel ?
- **Méthode** : boxplot du volume québécois par mois civil.
- **Résultat chiffré (médianes par mois)** : Non disponible dans le projet.
- **Graphique** : `outputs/figures/03_saisonnalite_mensuelle.png`.
- **Test formel** : voir section 8 (Mann-Whitney).

---

## 7. Principaux résultats

Classement selon l’ordre d’analyse du projet (EDA → tests → modèle → prévision), sans inventer un ordre d’importance externe.

### R1 — Plage dominante en cumul

- **Résultat** : 250 000 $–500 000 $ = 398 901 ventes (37,98 %).
- **Contexte** : cumul janvier 2021 – août 2026, 1 050 237 ventes.
- **Interprétation prudente** : en stock sur 5,7 ans, le milieu de marché est le plus gros morceau ; cela ne décrit pas un mois récent isolé.
- **Source** : `notebooks/03_exploratory_data_analysis.ipynb` (et totaux bruts identiques dans le `01`).

### R2 — Volume complet et cohérent avec l’officiel

- **Résultat** : 3 262 lignes, 0 manquant, 0 doublon ; totaux août 2026 = 12 266 = publication quebec.ca.
- **Source** : notebooks `01` et `02`.

### R3 — Saison statistiquement détectable

- **Résultat** : médiane haute saison 17 045 vs basse saison 12 685 ; Mann-Whitney p = 1,848×10⁻⁵.
- **Interprétation prudente** : avril–septembre n’a pas la même distribution que octobre–mars.
- **Source** : `notebooks/04_statistical_analysis.ipynb`.

### R4 — Tendance temporelle baissière, mais faible pouvoir explicatif d’une droite

- **Résultat** : Spearman ρ = −0,297, p = 0,014 ; OLS pente = −87,85 ventes par mois d’indice, R² = 0,105 ; Durbin-Watson = 0,721.
- **Interprétation prudente** : tendance monotone à la baisse détectable ; une droite n’explique qu’environ 10 % de la variance ; les résidus restent autocorrélés (saison).
- **Source** : notebook `04`.

### R5 — Les trois plages n’ont pas le même volume mensuel

- **Résultat** : Kruskal-Wallis H = 23,99, p = 6,164×10⁻⁶.
- **Source** : notebook `04`.

### R6 — Volume mensuel non normal

- **Résultat** : Shapiro-Wilk W = 0,9192, p = 0,0002988 ; asymétrie 1,283 ; aplatissement 2,629.
- **Source** : notebook `04`.

### R7 — Un modèle d’ensemble bat la persistance

- **Résultat** : forêt aléatoire MAE test = 40,483 vs persistance 91,581 (gain affiché +55,8 %).
- **Source** : `notebooks/06_modeling.ipynb`.

### R8 — Prévision opérationnelle à un mois

- **Résultat** : modèle « Forêt aléatoire », MAE test 40,5 ; 48 séries prévues à partir de 2026-07 pour 2026-08. Somme des `ventes_prevues` dans `outputs/predictions/predictions.csv` = 14 390.
- **Comparaison à la réalité d’août 2026 (12 266)** : non calculée dans le notebook `07`. Les deux chiffres existent séparément dans le projet.
- **Source** : notebook `07`, `outputs/predictions/predictions.csv`, notebook `02` pour le réalisé.

---

## 8. Analyse statistique

Source : `notebooks/04_statistical_analysis.ipynb`. Seuil α = 0,05. Série = volume québécois mensuel (somme de toutes les régions et plages), n = 68 mois, sauf mention contraire.

| Hypothèse nulle | Test | Statistique | p-valeur | Décision |
| --- | --- | --- | --- | --- |
| Le volume mensuel est normal | Shapiro-Wilk | W = 0,9192 | 0,0002988 | Rejetée |
| Avril–septembre = octobre–mars | Mann-Whitney (bilatéral) | U = 927 | 1,848×10⁻⁵ | Rejetée |
| Les 3 plages ont la même distribution de volumes mensuels québécois | Kruskal-Wallis | H = 23,99 | 6,164×10⁻⁶ | Rejetée |
| Aucune tendance monotone du volume | Spearman (rang vs temps) | ρ = −0,297 | 0,01407 | Rejetée |
| Pente OLS nulle | OLS `ventes ~ t` | coef t = −87,8463 | 0,007 (P>\|t\|) | Rejetée |

**Autres chiffres OLS (notebook `04`).** R² = 0,105 ; R² ajusté = 0,092 ; F p = 0,00695 ; constante 18 390 ; IC 95 % de la pente [−150,79 ; −24,90] ; Durbin-Watson = 0,721 ; n = 68.

**Saison (chiffres).** Médiane haute saison = 17 045 ; médiane basse saison = 12 685.

**Corrélations entre plages.** Heatmap Spearman des volumes mensuels québécois par plage : `outputs/figures/04_correlations_plages.png`. **Valeurs numériques des coefficients : Non disponible dans le projet** (graphique annoté, pas de table exportée).

**Diagnostics.** Résidus vs ajustés et droite de Henry : `outputs/figures/04_diagnostic_residus.png`. Interprétation dans le notebook : une tendance linéaire est insuffisante.

---

## 9. Feature Engineering

Source : `notebooks/05_feature_engineering.ipynb`. Grain de série : `id_region` × `code_plage_prix`. Toutes les variables explicatives sont décalées (`shift`) pour ne pas utiliser le futur. Filtre final : `dropna` sur `cible_ventes_suivantes` et `ventes_retard_12` → **2 638 observations, 35 variables explicatives**, couverture **2022-01 → 2026-07**.

| Nom | Définition / calcul | Raison | Dans le modèle |
| --- | --- | --- | --- |
| `annee` | année de `periode` | tendance calendaire | oui |
| `mois` | mois 1–12 | intermédiaire | non (pas dans `COLONNES_EXPLICATIVES`) |
| `trimestre` | trimestre | saisonnalité discrète | oui |
| `mois_sin`, `mois_cos` | sin/cos(2π × mois / 12) | saison cyclique (déc. proche de janv.) | oui |
| `ventes_retard_1/2/3/12` | `shift` du volume dans la série | persistance et saison annuelle | oui |
| `ventes_moyenne_3/6/12` | moyenne mobile du volume **déjà décalé d’un mois** | tendance récente | oui |
| `ventes_ecart_type_12` | écart-type mobile 12 mois, décalé | volatilité récente | oui |
| `variation_mensuelle` | retard1/retard2 − 1 | dynamique court terme | oui |
| `variation_annuelle` | retard1/retard12 − 1 | glissement annuel | oui |
| `total_quebec` | somme des ventes du mois | contexte | non (fuite si non décalé) |
| `part_quebec` | ventes / total_quebec | part contemporaine | non |
| `part_quebec_retard_1` | part décalée | contexte sans fuite | oui |
| `total_quebec_retard_1` | total provincial décalé | conjoncture | oui |
| `plage_*` | dummies de `plage_prix` | niveau de plage | oui |
| `region_*` | dummies de `id_region` | niveau régional | oui |
| `cible_ventes_suivantes` | `shift(-1)` du volume | cible | cible uniquement |

2021 sert uniquement d’historique pour les retards. Août 2026 n’est pas une ligne d’entrée (pas de mois suivant pour la cible) ; il sert de cible à juillet 2026.

---

## 10. Machine Learning

Source : `notebooks/06_modeling.ipynb`. Objectif commun : régression du nombre de ventes du mois suivant, par série région × plage.

**Données modèle.** 2 638 observations, 35 explicatives, 2022-01 → 2026-07.

**Séparation.** Chronologique sur les mois uniques, coupure au 80e centile des périodes : entraînement **2 110 lignes (< 2025-09)**, test **528 lignes (≥ 2025-09)**.

**Validation.** `TimeSeriesSplit(n_splits=5)`, score `neg_mean_absolute_error`.

**Référence.** Persistance = `ventes_retard_1` (pas un estimateur sklearn entraîné).

**Prétraitement commun (pipelines).** `SimpleImputer(strategy="median")`. Ridge y ajoute `StandardScaler`.

| Modèle | Objectif | Hyperparamètres dans le code | Métriques test / CV |
| --- | --- | --- | --- |
| Persistance | référence | aucune | voir §11 |
| Ridge | linéaire pénalisée | `RidgeCV(alphas=np.logspace(-3, 3, 13))` ; alpha retenu : Non disponible dans le projet | voir §11 |
| Forêt aléatoire | non linéaire | `n_estimators=400`, `min_samples_leaf=2`, `random_state=42`, `n_jobs=-1` | voir §11 |
| Gradient boosting | non linéaire | `n_estimators=300`, `learning_rate=0.05`, `max_depth=3`, `random_state=42` | voir §11 |

Importances de variables et graphique observé vs prévu : `outputs/figures/06_importance_variables.png`, `outputs/figures/06_observe_vs_prevu.png`. **Liste chiffrée des importances : Non disponible dans le projet.**

---

## 11. Comparaison des modèles

Métriques de test sauf `mae_cv` (validation croisée temporelle sur l’entraînement). Source : tableau `round(3)` du notebook `06`.

| Modèle | MAE | RMSE | R² | MAPE (%) | MAE CV | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Forêt aléatoire | 40,483 | 71,260 | 0,951 | 17,737 | 64,994 | plus petit MAE test |
| Gradient boosting | 42,323 | 69,560 | 0,953 | 22,973 | 64,248 | plus petit MAE CV ; plus petit RMSE ; plus grand R² |
| Ridge | 72,836 | 109,662 | 0,884 | 67,049 | 104,385 | |
| Persistance (`ventes_retard_1`) | 91,581 | 179,576 | 0,689 | 34,055 | — | pas de CV |

Le code retient le modèle entraîné au **plus petit MAE test** (pas le R², pas le MAE CV).

---

## 12. Modèle retenu

- **Modèle** : Forêt aléatoire (`artefact["nom"]` dans `outputs/models/best_model.pkl` ; notebook `07` : « Modèle : Forêt aléatoire »).
- **Raison documentée** : plus petit MAE test parmi Ridge / forêt / boosting (40,483). Affichage : « MAE 40.5 contre 91.6 pour la persistance (+55.8 %) ».
- **Performances test** : MAE 40,483 ; RMSE 71,260 ; MAPE 17,737 % ; R² 0,951 ; MAE CV 64,994.
- **Limites** (notebooks `06` et `07`) : horizon d’un mois ; pas de variables exogènes ; bornes = ± MAE test ; tous types de propriétés mélangés ; le boosting a un R² et un RMSE légèrement meilleurs — le projet choisit quand même le MAE comme critère principal.

---

## 13. Prédictions

Source : `notebooks/07_prediction.ipynb`, `outputs/predictions/predictions.csv`.

- **Cible prédite** : `nombre_ventes` du mois suivant, pour chaque couple région × plage.
- **Mois d’entrée** : 2026-07 (48 séries).
- **Mois prédit** : 2026-08 (`periode_predite`).
- **Variables** : les 35 explicatives stockées avec le pickle.
- **Post-traitement** : prévisions arrondies, plancher à 0 ; `borne_basse` / `borne_haute` = prévision ± MAE test (40,5), plancher 0 sur la borne basse.
- **Résultats fichier** : 48 lignes. Somme de `ventes_prevues` = **14 390**. Exemples (fichier) :
  - Montréal, > 500 000 $ : 1 208 (bornes 1 168–1 248) ;
  - Montérégie, > 500 000 $ : 1 241 (1 201–1 281) ;
  - Montérégie, 250–500 k$ : 1 118 (1 078–1 158).
- **Total prévu imprimé par le notebook `07`** : Non disponible dans le projet (sortie non persistée). Le total ci-dessus vient du CSV.
- **Comparaison prédiction / réalité** : non produite par le notebook `07`. Le réalisé d’août 2026 dans le projet est 12 266 (notebook `02`).
- **Graphique** : `outputs/figures/07_predictions.png` (barres du total prévu par plage).

---

## 14. Insights Data Science

### Insight 1

- **Observation** : en cumul, la plage 250–500 k$ est la plus volumineuse (37,98 %).
- **Donnée** : 398 901 / 1 050 237.
- **Interprétation** : le « milieu » domine l’historique 2021–2026.
- **Limite** : le mix d’un mois récent (août 2026 : 40,5 % au-dessus de 500 k$) diffère du cumul.

### Insight 2

- **Observation** : avril–septembre a une médiane de volume plus élevée qu’octobre–mars.
- **Donnée** : 17 045 vs 12 685 ; p = 1,848×10⁻⁵.
- **Interprétation** : la saisonnalité n’est pas un artefact visuel.
- **Limite** : découpage binaire (6 mois / 6 mois), pas un modèle SARIMA.

### Insight 3

- **Observation** : tendance temporelle baissière détectable, peu captée par une droite.
- **Donnée** : ρ = −0,297 ; R² OLS = 0,105 ; DW = 0,721.
- **Interprétation** : le niveau de fond a baissé depuis 2021, mais le cycle et les chocs dominent.
- **Limite** : 68 points ; pas de variable de taux d’intérêt.

### Insight 4

- **Observation** : une forêt aléatoire réduit l’erreur absolue d’environ 56 % par rapport à copier le mois précédent.
- **Donnée** : MAE 40,5 vs 91,6 ; +55,8 % affiché par le notebook.
- **Interprétation** : les retards, la saison cyclique et les dummies région/plage apportent de l’information au-delà de la persistance.
- **Limite** : MAE sur des lignes hétérogènes (Côte-Nord vs Montérégie) ; le R² élevé (0,95) reflète surtout les écarts de niveau entre séries.

### Insight 5

- **Observation** : le fichier est déjà propre (0 manquant, 0 doublon) et recoupe l’officiel.
- **Donnée** : 3 262 lignes ; août 2026 = 12 266.
- **Interprétation** : le risque principal n’est pas le nettoyage, c’est le grain (agrégat, région 10 ventilée, tous immeubles mélangés).
- **Limite** : qualité « officielle », pas qualité « une vente = un logement typé ».

---

## 15. Limites du projet

**Données.**

- Tous types de propriétés confondus.
- Premier droit de l’acte seulement.
- Région 10 absente / ventilée dans 02, 08, 09 → volumes de ces trois régions un peu gonflés.
- Circonscriptions foncières ≠ limites administratives strictes.
- Une seule nature d’acte (`001`).
- Période : janvier 2021 – août 2026 seulement ; le modèle part en 2022-01 à cause du retard 12.

**Méthode.**

- Pas de variables exogènes (taux, mises en chantier, migration, emploi).
- Tests sur le total québécois, pas série par série.
- Corrélations entre plages : graphique seulement.
- Critère de sélection = MAE test ; le boosting a un meilleur R² et RMSE.

**Modèle / prévisions.**

- Horizon d’un mois ; au-delà, les retards devraient être alimentés par des prévisions (erreur cumulée).
- Bornes = ± MAE test, non calibrées.
- Découpage 80 % chronologique : test = sept. 2025 et après.
- Prévision d’août 2026 non confrontée au réalisé dans le notebook `07`.

---

## 16. Technologies utilisées

Présentes dans `requirements.txt` et/ou importées dans les notebooks / `src` :

- Python
- pandas
- numpy
- matplotlib
- seaborn
- scipy
- statsmodels
- scikit-learn (`Pipeline`, `RidgeCV`, `RandomForestRegressor`, `GradientBoostingRegressor`, `TimeSeriesSplit`, `SimpleImputer`, `StandardScaler`)
- joblib
- jupyter / ipykernel
- pytest

**Non utilisés dans le projet** : XGBoost, TensorFlow, PyTorch, SQL, cloud.

---

## 17. Architecture du projet

```
Projet-marche-immobilier-quebec/
├── data/raw/donn_prix_vente_reqst.csv
├── data/processed/ventes_plage_prix_propre.csv
├── data/processed/features.csv
├── notebooks/01_data_understanding.ipynb … 07_prediction.ipynb
├── src/__init__.py          # chemins du projet
├── src/referentiels.py      # régions, plages, natures
├── src/data_cleaning.py     # nettoyage testable
├── outputs/figures/         # 03_*, 04_*, 06_*, 07_*
├── outputs/models/best_model.pkl
├── outputs/predictions/predictions.csv
├── docs/dictionnaire_donnees.md
├── tests/test_data_cleaning.py
├── README.md
├── requirements.txt
└── LICENSE                  # MIT
```

Les notebooks s’enchaînent : chacun lit la sortie du précédent.

---

## 18. Fichiers importants pour une publication LinkedIn

| Fichier | Usage LinkedIn |
| --- | --- |
| `README.md` | cadrage public |
| `docs/dictionnaire_donnees.md` | source et grain |
| `notebooks/03_exploratory_data_analysis.ipynb` | EDA + chiffres de parts / régions |
| `notebooks/04_statistical_analysis.ipynb` | tests et p-valeurs |
| `notebooks/06_modeling.ipynb` | tableau de métriques |
| `notebooks/07_prediction.ipynb` | modèle retenu, limites |
| `outputs/figures/03_ventes_par_plage.png` | mix de prix |
| `outputs/figures/03_evolution_volume_total.png` | série temporelle |
| `outputs/figures/03_parts_de_marche.png` | glissement des parts |
| `outputs/figures/03_ventes_par_region.png` | géographie |
| `outputs/figures/03_part_haut_de_gamme_region.png` | haut de gamme |
| `outputs/figures/03_saisonnalite_mensuelle.png` | saison |
| `outputs/figures/04_correlations_plages.png` | corrélations |
| `outputs/figures/04_diagnostic_residus.png` | limite d’une tendance linéaire |
| `outputs/figures/06_observe_vs_prevu.png` | qualité hors échantillon |
| `outputs/figures/06_importance_variables.png` | leviers du modèle |
| `outputs/figures/07_predictions.png` | prévision par plage |
| `outputs/predictions/predictions.csv` | prévisions détaillées |
| `outputs/models/best_model.pkl` | artefact (ne pas poster le binaire) |
| `src/data_cleaning.py` | code de nettoyage |
| `tests/test_data_cleaning.py` | tests unitaires |

---

## 19. Code intéressant à montrer sur LinkedIn

### 19.1 Conversion des nombres au format québécois

Fichier : `src/data_cleaning.py`, fonction `vers_numerique`.

Montre : espaces insécables, virgule décimale, sentinelles `n/d`.

### 19.2 Récolement à une publication officielle

Fichier : `notebooks/02_data_cleaning.ipynb`, cellule `recolement`.

Montre : assertion `assert aout["nombre_ventes"].sum() == 12266` et totaux par plage.

### 19.3 Retards sans fuite temporelle, par série

Fichier : `notebooks/05_feature_engineering.ipynb`, cellule `retards`.

Montre : `groupby` + `shift` + `rolling` sur la série déjà décalée.

### 19.4 Découpage chronologique (pas aléatoire)

Fichier : `notebooks/06_modeling.ipynb`, cellule `decoupage`.

Montre : coupure sur les mois uniques (entraînement < 2025-09).

### 19.5 Référence de persistance avant les modèles

Fichier : `notebooks/06_modeling.ipynb`, fonction `evaluer` + baseline `ventes_retard_1`.

Montre : un modèle n’est retenu que s’il bat « demain = aujourd’hui ».

---

## 20. Résumé pour LinkedIn

Projet d’analyse des ventes inscrites au Registre foncier du Québec (MRNF / Données Québec), fichier `donn_prix_vente_reqst.csv` : 3 262 lignes, janvier 2021 – août 2026, grain mois × région × plage de prix.

Le jeu est complet (0 manquant, 0 doublon) et recoupe les totaux officiels d’août 2026 (12 266 ventes).

En cumul, la plage 250–500 k$ pèse 38 % des 1,05 million de ventes ; Montérégie, Montréal et Laurentides portent le volume.

Des tests non paramétriques confirment une saison (médianes 17 045 vs 12 685), des plages inégales, une non-normalité, et une tendance baissière faible (ρ = −0,30 ; R² OLS = 0,11).

Une forêt aléatoire prévoit le mois suivant (2 638 observations, split temporel, test dès 2025-09) avec un MAE de 40,5 ventes, contre 91,6 pour la persistance (+55,8 %).

La prévision opérationnelle porte sur août 2026 (48 séries) ; le notebook ne compare pas ce total au réalisé. Limites : un mois d’horizon, pas d’exogènes, tous immeubles mélangés, région 10 ventilée.

---

## 21. Idées de contenu visuel

1. **Problématique** — question : peut-on prévoir le volume à 1 mois, région × plage ? Mentionner le Registre foncier.
2. **Données** — 3 262 lignes, 68 mois, 16 régions, 3 plages ; source Données Québec / MRNF ; CC-BY 4.0.
3. **Pipeline** — 01 compréhension → 02 nettoyage → 03 EDA → 04 tests → 05 features → 06 modèles → 07 prévision.
4. **Nettoyage** — 3 262 → 3 262 ; récolement 12 266 = 2 799 + 4 496 + 4 971 ; région 10 documentée, non imputée.
5. **EDA** — barres des 3 plages (364 135 / 398 901 / 287 201) ; top régions (Montérégie 202 908, Montréal 149 127, Laurentides 120 332).
6. **Résultats / stats** — tableau des 4 tests avec p-valeurs ; médianes saisonnières 17 045 vs 12 685.
7. **Machine Learning** — tableau MAE / RMSE / R² / MAPE des 4 approches ; split 2 110 / 528 ; coupure 2025-09.
8. **Prédictions** — forêt, MAE 40,5 ; 48 séries ; mois prédit 2026-08 ; extraits Montréal / Montérégie du CSV.
9. **Insights** — cumul milieu de marché vs août 2026 à 40,5 % au-dessus de 500 k$ ; gain +55,8 % vs persistance.
10. **Limites** — horizon 1 mois ; pas de taux ; types mélangés ; bornes = ± MAE ; région 10.

---

## 22. Éléments à vérifier avant publication

- [ ] chiffres vérifiés (totaux plages, régions, tests, MAE, 14 390)
- [ ] source des données indiquée (MRNF, Données Québec, CC-BY 4.0)
- [ ] graphiques lisibles (titres, axes, unités en nombre de ventes)
- [ ] unités indiquées (ventes inscrites, pas des prix)
- [ ] période indiquée (2021-01–2026-08 pour l’EDA ; 2022-01–2026-07 pour le ML)
- [ ] métriques vérifiées (MAE forêt 40,483 ; persistance 91,581 ; gain +55,8 %)
- [ ] aucune affirmation non supportée (ne pas dire « le luxe domine le Québec » : faux en cumul)
- [ ] limites mentionnées (exogènes, grain, région 10, horizon)
- [ ] lien GitHub disponible — **Non disponible dans le projet**
- [ ] ne pas présenter 14 390 comme « validé » contre 12 266 : le `07` ne fait pas cette comparaison
- [ ] citer que les ventes = tous types de propriétés

---

## 23. Informations manquantes

- Lien vers un dépôt GitHub / GitLab.
- Valeurs numériques de la matrice de corrélation Spearman (graphique seulement).
- Médianes ou moyennes du boxplot mensuel (saisonnalité visuelle sans table).
- Série mensuelle des totaux québécois en CSV (seulement graphiques).
- Parts > 500 000 $ par région en tableau (graphique seulement).
- Importances chiffrées des variables du modèle (graphique seulement).
- Alpha Ridge retenu par `RidgeCV`.
- Total prévu imprimé par le notebook `07` (calculable depuis le CSV : 14 390).
- Comparaison formelle prévisions août 2026 vs réalisé 12 266.
- Test d’outliers / winsorisation.
- Identification du mois et de la région du max 4 100 ventes.
- Métriques de test ventilées par région ou par plage.
- XGBoost ou autres librairies non listées.
- Auteur, affiliation, date de publication du projet au-delà de la licence MIT 2026.
- Jeux complémentaires du même portail (hypothèques, transferts, difficultés financières) : non utilisés.
