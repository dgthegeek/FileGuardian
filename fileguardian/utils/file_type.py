from pathlib import Path
import magic
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class FileTypeDetector:
    """Détecte le type MIME et l'extension des fichiers"""
    
    def __init__(self):
        self.magic = magic.Magic(mime=True)
        
    def detect_mime_type(self, file_path: Path) -> str:
        """
        Détecte le type MIME d'un fichier
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            str: Type MIME du fichier
        """
        try:
            return self.magic.from_file(str(file_path))
        except Exception as e:
            logger.error(f"Error detecting MIME type for {file_path}: {str(e)}")
            return "application/octet-stream"

    def get_category(self, mime_type: str) -> Optional[str]:
        """
        Détermine la catégorie générale d'un fichier basé sur son type MIME
        
        Args:
            mime_type: Type MIME du fichier
            
        Returns:
            Optional[str]: Catégorie du fichier (image, pdf, office, etc.)
        """
        mime_categories = {
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/tiff'],
            'pdf': ['application/pdf'],
            'office': [
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            ],
        }
        
        for category, mime_types in mime_categories.items():
            if mime_type in mime_types:
                return category
                
        return None

    def is_supported_type(self, file_path: Path) -> bool:
        """
        Vérifie si le type de fichier est supporté
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            bool: True si le type est supporté
        """
        mime_type = self.detect_mime_type(file_path)
        return self.get_category(mime_type) is not None