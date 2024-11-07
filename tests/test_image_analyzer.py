import pytest
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
from fileguardian.analyzers.image import ImageAnalyzer  
import os

class TestImageAnalyzer:
    @pytest.fixture
    def setup_test_images(self, tmp_path):
        """Crée des images de test avec et sans métadonnées EXIF"""
        # Image sans EXIF
        clean_image_path = tmp_path / "clean.jpg"
        Image.new('RGB', (100, 100), color='red').save(clean_image_path)
        
        # Image avec GPS
        gps_image_path = tmp_path / "with_gps.jpeg"
        img = Image.new('RGB', (100, 100), color='blue')
        
        # Création des données EXIF avec GPS
        exif_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef: "N",
                piexif.GPSIFD.GPSLatitude: ((48, 1), (51, 1), (30, 1)),
                piexif.GPSIFD.GPSLongitudeRef: "E",
                piexif.GPSIFD.GPSLongitude: ((2, 1), (17, 1), (40, 1))
            }
        }
        exif_bytes = piexif.dump(exif_dict)
        img.save(gps_image_path, "jpeg", exif=exif_bytes)
        
        return {"clean": clean_image_path, "gps": gps_image_path}

    def test_clean_image(self, setup_test_images):
        analyzer = ImageAnalyzer()
        result = analyzer.analyze(setup_test_images["clean"])
        
        assert result["risk_level"] == 0
        assert len(result["findings"]) == 0
        assert result["metadata"] == {}

    def test_gps_image(self, setup_test_images):
        analyzer = ImageAnalyzer()
        result = analyzer.analyze(setup_test_images["gps"])
        
        assert result["risk_level"] >= 3  # GPS devrait donner un niveau de risque d'au moins 3
        assert len(result["findings"]) >= 1
        assert "GPS" in result["metadata"]
        assert "latitude" in result["metadata"]["GPS"]
        assert "longitude" in result["metadata"]["GPS"]
        
        # Vérifie les coordonnées approximatives
        assert abs(result["metadata"]["GPS"]["latitude"] - 48.858333) < 0.01
        assert abs(result["metadata"]["GPS"]["longitude"] - 2.294444) < 0.01

    def test_invalid_image(self, tmp_path):
        invalid_path = tmp_path / "invalid.jpg"
        with open(invalid_path, "w") as f:
            f.write("Not an image")
        
        analyzer = ImageAnalyzer()
        with pytest.raises(Exception):
            analyzer.analyze(invalid_path)