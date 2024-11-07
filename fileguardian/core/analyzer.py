from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class BaseAnalyzer:
    def __init__(self):
        self.risk_level = 0
        self.findings = []

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """
        Méthode de base pour l'analyse d'un fichier.
        À implémenter par les classes enfants.
        """
        raise NotImplementedError("Analyzer must implement analyze method")

    def get_risk_level(self) -> int:
        """
        Retourne le niveau de risque (0-5)
        0: Pas de risque
        5: Risque critique
        """
        return self.risk_level

    def get_recommendations(self) -> List[str]:
        """
        Retourne la liste des recommandations basées sur l'analyse
        """
        return self.findings

    def add_finding(self, message: str, risk_level: int):
        """
        Ajoute une découverte et met à jour le niveau de risque
        """
        self.findings.append(message)
        self.risk_level = max(self.risk_level, risk_level)