# Guide du Développeur - FileGuardian

## 1. Concepts Clés

### 1.1 Architecture Core
- **Core Scanner**
  ```
  Input File → File Type Detection → Appropriate Analyzer → Analysis Results → Report Generation
  ```
  
  C'est le flux principal de l'application. Chaque fichier passe par ces étapes systématiquement.

### 1.2 Système de Modules
Chaque type de fichier a son propre module d'analyse qui hérite d'une classe de base :
```python
class BaseAnalyzer:
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        pass
    def get_risk_level(self) -> int:
        pass
    def get_recommendations(self) -> List[str]:
        pass

class ImageAnalyzer(BaseAnalyzer):
    # Spécifique aux images
    pass

class PDFAnalyzer(BaseAnalyzer):
    # Spécifique aux PDFs
    pass
```

## 2. Guide Technique par Type de Fichier

### 2.1 Images
**Risques à détecter :**
- GPS Location dans EXIF : Risque de privacy
- Creation Date : Risque d'information temporelle
- Device Info : Information sur l'équipement
- Thumbnails : Potentielles anciennes versions
- Software Used : Information sur les outils

**Exemple de métadonnées sensibles :**
```json
{
    "GPS": {
        "GPSLatitude": "48.8583",
        "GPSLongitude": "2.2944"
    },
    "Device": {
        "Make": "iPhone",
        "Model": "iPhone 13"
    },
    "Software": "Adobe Photoshop 2023",
    "CreateDate": "2024:01:15 10:30:15"
}
```

### 2.2 PDFs
**Éléments à analyser :**
- JavaScript : Code potentiellement malveillant
- Forms : Données sensibles
- Embedded Files : Fichiers cachés
- External Links : Liens malveillants
- Metadata : Information sensible

**Exemple de structure à risque :**
```json
{
    "javascript_present": true,
    "forms": {
        "count": 2,
        "types": ["XFA", "Acroform"]
    },
    "external_links": [
        "http://suspicious-domain.com",
        "ftp://internal-server.local"
    ]
}
```

### 2.3 Documents Office
**Points d'attention :**
- Macros VBA : Code automatisé
- External Links : Connexions externes
- Embedded Objects : Objets cachés
- Hidden Text : Texte invisible
- Revision History : Anciennes versions

**Exemple de détection :**
```json
{
    "macros": {
        "present": true,
        "autoexec": true
    },
    "external_content": [
        "http://sharepoint.internal/sensitive",
        "\\\\network-share\\docs"
    ],
    "hidden_content": true
}
```

## 3. Patterns de Développement

### 3.1 Structure du Code
```
fileguardian/
├── core/
│   ├── __init__.py
│   ├── scanner.py      # Core scanning engine
│   └── analyzer.py     # Base analyzer class
├── analyzers/
│   ├── __init__.py
│   ├── image.py
│   ├── pdf.py
│   └── office.py
├── utils/
│   ├── __init__.py
│   ├── file_type.py    # MIME type detection
│   └── reporting.py    # Report generation
└── cli.py             # Command line interface
```

### 3.2 Exemple de Flow Code
```python
class FileGuardian:
    def scan_file(self, file_path: Path) -> ScanResult:
        # 1. Détection type
        file_type = self.detect_type(file_path)
        
        # 2. Sélection analyseur
        analyzer = self.get_analyzer(file_type)
        
        # 3. Analyse
        results = analyzer.analyze(file_path)
        
        # 4. Évaluation risques
        risks = self.evaluate_risks(results)
        
        # 5. Génération rapport
        return self.generate_report(risks)
```

## 4. Bonnes Pratiques

### 4.1 Gestion des Erreurs
```python
class FileAnalysisError(Exception):
    pass

class AnalyzerNotFoundError(FileAnalysisError):
    pass

class CorruptedFileError(FileAnalysisError):
    pass

# Usage
try:
    result = analyzer.analyze(file_path)
except CorruptedFileError:
    logger.error("File is corrupted")
except AnalyzerNotFoundError:
    logger.error("No analyzer for this file type")
```

### 4.2 Logging
```python
import logging

logger = logging.getLogger(__name__)

class BaseAnalyzer:
    def analyze(self, file_path):
        logger.info(f"Starting analysis of {file_path}")
        try:
            # Analysis code
            logger.debug("Analysis details...")
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
```

## 5. Tests

### 5.1 Structure des Tests
```python
def test_image_analyzer():
    analyzer = ImageAnalyzer()
    # Test avec image GPS
    result = analyzer.analyze("tests/samples/gps_photo.jpg")
    assert "GPS" in result
    assert result["risk_level"] >= 3
    
    # Test sans données sensibles
    result = analyzer.analyze("tests/samples/clean_photo.jpg")
    assert result["risk_level"] == 0
```

### 5.2 Fichiers de Test
```
tests/
├── samples/
│   ├── images/
│   │   ├── gps_photo.jpg
│   │   └── clean_photo.jpg
│   ├── pdfs/
│   │   ├── malicious.pdf
│   │   └── clean.pdf
│   └── office/
│       ├── macro_doc.docx
│       └── clean_doc.docx
└── test_*.py
```

## 6. Workflow de Développement

1. **Ajout d'une nouvelle fonctionnalité**
   ```bash
   git checkout -b feature/nom-feature
   # Développement
   # Tests
   git commit -m "Add: description détaillée"
   ```

2. **Code Review Checklist**
   - Tests unitaires passent
   - Pas de hardcoding
   - Gestion d'erreurs appropriée
   - Documentation à jour
   - Performance optimale

3. **Commit Convention**
   ```
   Add: nouvelle fonctionnalité
   Fix: correction de bug
   Update: amélioration existante
   Doc: documentation
   Test: ajout/modification tests
   ```