from pathlib import Path
from typing import Dict, Any, List
from abc import ABC, abstractmethod
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class AnalysisResult:
    def __init__(self):
        self.metadata: Dict[str, Any] = {}
        self.risks: List[Dict[str, Any]] = []
        self.risk_level: int = 0  # 0-5, 0 = no risk, 5 = critical
        self.recommendations: List[str] = []

    def add_risk(self, risk_type: str, description: str, severity: int):
        self.risks.append({
            "type": risk_type,
            "description": description,
            "severity": severity
        })
        self.risk_level = max(self.risk_level, severity)

    def add_metadata(self, key: str, value: Any):
        self.metadata[key] = value

    def add_recommendation(self, recommendation: str):
        self.recommendations.append(recommendation)

class FileAnalysisError(Exception):
    """Base exception for file analysis errors"""
    pass

class AnalyzerNotFoundError(FileAnalysisError):
    """Raised when no analyzer is found for a file type"""
    pass

class CorruptedFileError(FileAnalysisError):
    """Raised when a file is corrupted or cannot be processed"""
    pass

class BaseAnalyzer(ABC):
    """Classe de base pour tous les analyseurs de fichiers"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def analyze(self, file_path: Path) -> AnalysisResult:
        """
        Analyse un fichier et retourne les résultats
        
        Args:
            file_path: Chemin vers le fichier à analyser
            
        Returns:
            AnalysisResult contenant les métadonnées et les risques détectés
            
        Raises:
            CorruptedFileError: Si le fichier est corrompu
            FileAnalysisError: Pour les autres erreurs d'analyse
        """
        pass

    @abstractmethod
    def can_handle(self, mime_type: str) -> bool:
        """
        Vérifie si l'analyseur peut traiter ce type de fichier
        
        Args:
            mime_type: Type MIME du fichier
            
        Returns:
            bool: True si l'analyseur peut traiter ce type
        """
        pass

    def validate_file(self, file_path: Path) -> bool:
        """
        Valide basiquement un fichier avant analyse
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            bool: True si le fichier est valide
            
        Raises:
            CorruptedFileError: Si le fichier est invalide
        """
        if not file_path.exists():
            raise FileAnalysisError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise FileAnalysisError(f"Not a file: {file_path}")
            
        if file_path.stat().st_size == 0:
            raise CorruptedFileError(f"Empty file: {file_path}")
            
        return True