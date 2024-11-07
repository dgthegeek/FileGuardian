from pathlib import Path
from typing import Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import logging
from fileguardian.core.analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

class ImageAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        self.sensitive_exif_tags = {
            'GPSInfo': 3,  # Niveau de risque 3 pour les données GPS
            'Make': 1,     # Niveau de risque 1 pour la marque de l'appareil
            'Model': 1,    # Niveau de risque 1 pour le modèle
            'Software': 1, # Niveau de risque 1 pour le logiciel utilisé
            'DateTimeOriginal': 2  # Niveau de risque 2 pour la date de création
        }

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyse une image pour les métadonnées sensibles.
        """
        try:
            with Image.open(file_path) as img:
                # Vérifier si l'image a des données EXIF
                if not hasattr(img, '_getexif') or img._getexif() is None:
                    logger.info(f"No EXIF data found in {file_path}")
                    return {"risk_level": 0, "findings": [], "metadata": {}}

                exif = {
                    TAGS.get(key, key): value
                    for key, value in img._getexif().items()
                    if key in TAGS
                }

                metadata = {}
                
                # Analyse GPS si présent
                if 'GPSInfo' in exif:
                    gps_data = self._parse_gps_data(exif['GPSInfo'])
                    if gps_data:
                        metadata['GPS'] = gps_data
                        self.add_finding(
                            "L'image contient des données de localisation GPS qui peuvent compromettre la vie privée",
                            self.sensitive_exif_tags['GPSInfo']
                        )

                # Analyse autres métadonnées sensibles
                for tag, risk_level in self.sensitive_exif_tags.items():
                    if tag in exif and tag != 'GPSInfo':
                        metadata[tag] = str(exif[tag])
                        self.add_finding(
                            f"Métadonnée sensible trouvée: {tag}",
                            risk_level
                        )

                return {
                    "risk_level": self.get_risk_level(),
                    "findings": self.get_recommendations(),
                    "metadata": metadata
                }

        except Exception as e:
            logger.error(f"Error analyzing image {file_path}: {str(e)}")
            raise

    def _parse_gps_data(self, gps_info: Dict) -> Dict[str, float]:
        """
        Parse les données GPS du format EXIF en coordonnées décimales.
        """
        try:
            gps_data = {}
            for key, value in gps_info.items():
                decoded = GPSTAGS.get(key, key)
                gps_data[decoded] = value

            if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                lat = self._convert_to_degrees(gps_data['GPSLatitude'])
                lon = self._convert_to_degrees(gps_data['GPSLongitude'])
                
                if 'GPSLatitudeRef' in gps_data and gps_data['GPSLatitudeRef'] == 'S':
                    lat = -lat
                if 'GPSLongitudeRef' in gps_data and gps_data['GPSLongitudeRef'] == 'W':
                    lon = -lon

                return {
                    "latitude": lat,
                    "longitude": lon
                }
            return {}

        except Exception as e:
            logger.error(f"Error parsing GPS data: {str(e)}")
            return {}

    def _convert_to_degrees(self, value) -> float:
        """
        Convertit les coordonnées GPS du format (degrés, minutes, secondes) en degrés décimaux.
        """
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)