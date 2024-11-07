import pytest
from pathlib import Path
from analyzers.pdf import PDFAnalyzer

class TestPDFAnalyzer:
    @pytest.fixture
    def setup_test_pdfs(self, tmp_path):
        """Crée des fichiers PDF de test avec différents éléments"""
        malicious_pdf_path = tmp_path / "malicious.pdf"
        with open(malicious_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n"
                   b"<<\n"
                   b"/Type /Catalog\n"
                   b"/Pages 2 0 R\n"
                   b"/Names <<\n"
                   b"/JavaScript 3 0 R\n"
                   b">>\n"
                   b">>\n"
                   b"3 0 obj\n"
                   b"<</S/JavaScript/JS(alert('Malicious code'))/Type/Action>>\n"
                   b"endobj\n")

        clean_pdf_path = tmp_path / "clean.pdf"
        with open(clean_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n"
                   b"<<\n"
                   b"/Type /Catalog\n"
                   b"/Pages 2 0 R\n"
                   b">>\n")

        return {"malicious": malicious_pdf_path, "clean": clean_pdf_path}

    def test_malicious_pdf(self, setup_test_pdfs):
        analyzer = PDFAnalyzer()
        result = analyzer.analyze(setup_test_pdfs["malicious"])

        assert result["risk_level"] >= 4  # Niveau de risque élevé pour le JavaScript
        assert len(result["findings"]) >= 1
        assert result["javascript_present"]

    def test_clean_pdf(self, setup_test_pdfs):
        analyzer = PDFAnalyzer()
        result = analyzer.analyze(setup_test_pdfs["clean"])

        assert result["risk_level"] == 0
        assert len(result["findings"]) == 0
        assert not result["javascript_present"]
        assert result["form_fields"] == 0
        assert result["embedded_files"] == 0

    def test_invalid_pdf(self, tmp_path):
        invalid_path = tmp_path / "invalid.pdf"
        with open(invalid_path, "w") as f:
            f.write("Not a PDF")

        analyzer = PDFAnalyzer()
        with pytest.raises(Exception):
            analyzer.analyze(invalid_path)