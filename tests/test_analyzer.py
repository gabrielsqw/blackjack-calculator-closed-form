"""Tests for BlackjackAnalyzer class."""

import pytest
from blackjack_calculator import BlackjackAnalyzer, HouseRules


class TestBlackjackAnalyzer:
    """Test cases for BlackjackAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        analyzer = BlackjackAnalyzer(rules=HouseRules.vegas_strip(), depth=0)
        analyzer.compute()
        return analyzer

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = BlackjackAnalyzer()
        assert analyzer.rules is not None
        assert analyzer.depth == 1
        assert not analyzer._computed

    def test_compute(self):
        """Test computation."""
        analyzer = BlackjackAnalyzer(depth=0)
        analyzer.compute()
        assert analyzer._computed
        assert analyzer.ev_calculator_hard is not None
        assert analyzer.recommendation_engine is not None

    def test_get_recommendation(self, analyzer):
        """Test getting recommendation."""
        rec = analyzer.get_recommendation([10, 6], dealer_card=10)

        assert rec is not None
        assert rec.recommended_action in ['hit', 'stand', 'double', 'split', 'surrender']
        assert isinstance(rec.expected_value, float)
        assert len(rec.all_actions) > 0

    def test_recommendation_before_compute(self):
        """Test that recommendation before compute raises error."""
        analyzer = BlackjackAnalyzer()

        with pytest.raises(RuntimeError, match="Must call compute"):
            analyzer.get_recommendation([10, 6], dealer_card=10)

    def test_classic_decisions(self, analyzer):
        """Test classic blackjack decisions."""
        # Hard 16 vs 10 should surrender (if available) or hit
        rec = analyzer.get_recommendation([10, 6], dealer_card=10)
        assert rec.recommended_action in ['surrender', 'hit']

        # Hard 20 should always stand
        rec = analyzer.get_recommendation([10, 10], dealer_card=10)
        assert rec.recommended_action == 'stand'

        # Pair of 8s should split
        rec = analyzer.get_recommendation([8, 8], dealer_card=10)
        assert rec.recommended_action == 'split'

    def test_get_dealer_probabilities(self, analyzer):
        """Test getting dealer probabilities."""
        probs = analyzer.get_dealer_probabilities(10)

        assert len(probs) == 6  # 17, 18, 19, 20, 21, Bust
        assert sum(probs.values()) == pytest.approx(1.0)

    def test_generate_strategy_chart(self, analyzer):
        """Test strategy chart generation."""
        charts = analyzer.generate_strategy_chart('all')

        assert 'hard' in charts
        assert 'soft' in charts
        assert 'pair' in charts

        # Check that charts have expected structure
        assert len(charts['hard']) > 0
        assert len(charts['soft']) > 0
        assert len(charts['pair']) > 0

    def test_analyze_situation(self, analyzer):
        """Test situation analysis."""
        analysis = analyzer.analyze_situation([10, 6], dealer_card=10)

        assert isinstance(analysis, str)
        assert '16' in analysis or 'Player' in analysis
        assert 'Dealer' in analysis

    def test_different_rule_sets(self):
        """Test analyzer with different rule sets."""
        rules_sets = [
            HouseRules.vegas_strip(),
            HouseRules.vegas_downtown(),
            HouseRules.atlantic_city(),
        ]

        for rules in rules_sets:
            analyzer = BlackjackAnalyzer(rules=rules, depth=0)
            analyzer.compute()

            # Should be able to get recommendations
            rec = analyzer.get_recommendation([10, 6], dealer_card=10)
            assert rec is not None
