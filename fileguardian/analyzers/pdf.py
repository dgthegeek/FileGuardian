import logging
from pathlib import Path
from typing import Dict, Any
import PyPDF2

from core.analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

class PDFAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfFileReader(file)

                # Vérification de la présence de JavaScript
                if pdf_reader.getNumJSActions() > 0:
                    self.add_finding("Le fichier PDF contient du code JavaScript", 4)

                # Vérification des formulaires
                form_fields = pdf_reader.getFields()
                if form_fields:
                    self.add_finding("Le fichier PDF contient des formulaires pouvant contenir des données sensibles", 3)
                    self._extract_form_types(form_fields)

                # Vérification des fichiers embarqués
                num_embedded_files = pdf_reader.getNumEmbeddedFiles()
                if num_embedded_files > 0:
                    self.add_finding("Le fichier PDF contient des fichiers embarqués", 3)
                    self.add_finding(f"{num_embedded_files} fichiers embarqués détectés", 2)

                return {
                    "risk_level": self.get_risk_level(),
                    "findings": self.get_recommendations(),
                    "javascript_present": pdf_reader.getNumJSActions() > 0,
                    "form_fields": len(form_fields),
                    "embedded_files": num_embedded_files
                }

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du fichier PDF {file_path}: {str(e)}")
            raise

    def _extract_form_types(self, form_fields: Dict[str, PyPDF2.generic.Field]) -> None:
        """
        Extrait les types de champs de formulaire présents dans le PDF.
        """
        form_types = set()
        for field in form_fields.values():
            form_types.add(field.get('/FT', 'Unknown'))

        for form_type in form_types:
            self.add_finding(f"Type de champ de formulaire détecté : {form_type}", 2)