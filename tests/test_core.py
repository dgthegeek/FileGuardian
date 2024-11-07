import pytest
from pathlib import Path
from fileguardian.core.analyzer import BaseAnalyzer

class TestBaseAnalyzer:
    def setup_method(self):
        self.analyzer = BaseAnalyzer()

    def test_initial_risk_level(self):
        assert self.analyzer.get_risk_level() == 0

    def test_add_finding(self):
        self.analyzer.add_finding("Test finding", 3)
        assert len(self.analyzer.get_recommendations()) == 1
        assert self.analyzer.get_risk_level() == 3

    def test_analyze_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.analyzer.analyze(Path("test.txt"))

    def test_multiple_findings_highest_risk(self):
        self.analyzer.add_finding("Low risk", 1)
        self.analyzer.add_finding("High risk", 4)
        self.analyzer.add_finding("Medium risk", 2)
        assert self.analyzer.get_risk_level() == 4
        assert len(self.analyzer.get_recommendations()) == 3