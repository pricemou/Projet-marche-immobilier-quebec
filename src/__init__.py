"""Code partagé du projet d'analyse du marché immobilier québécois.

Expose les chemins du projet afin que les notebooks et les tests n'aient
jamais à construire de chemins relatifs à leur propre emplacement.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
MODELS_DIR = OUTPUTS_DIR / "models"
PREDICTIONS_DIR = OUTPUTS_DIR / "predictions"

VENTES_BRUTES_CSV = RAW_DIR / "donn_prix_vente_reqst.csv"
VENTES_PROPRES_CSV = PROCESSED_DIR / "ventes_plage_prix_propre.csv"
FEATURES_CSV = PROCESSED_DIR / "features.csv"

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "RAW_DIR",
    "PROCESSED_DIR",
    "OUTPUTS_DIR",
    "FIGURES_DIR",
    "MODELS_DIR",
    "PREDICTIONS_DIR",
    "VENTES_BRUTES_CSV",
    "VENTES_PROPRES_CSV",
    "FEATURES_CSV",
]
