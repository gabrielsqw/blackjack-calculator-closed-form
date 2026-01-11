"""Tests for ProbabilityCalculator class."""

import pytest
import numpy as np
from blackjack_calculator.core.calculator import ProbabilityCalculator
from blackjack_calculator.core.house_rules import HouseRules
from blackjack_calculator.core.deck import Deck
from collections import Counter


class TestProbabilityCalculator:
    """Test cases for ProbabilityCalculator class."""

    def test_initialization(self):
        """Test calculator initialization."""
        calc = ProbabilityCalculator()
        assert calc.rules is not None
        assert calc.depth == 1
        assert calc.cards_composition is not None

    def test_custom_rules(self):
        """Test initialization with custom rules."""
        rules = HouseRules.vegas_strip()
        calc = ProbabilityCalculator(rules=rules, depth=2)
        assert calc.rules == rules
        assert calc.depth == 2

    def test_calculate_probabilities(self):
        """Test probability calculation for standard deck."""
        composition = Counter([i for i in range(1, 14) for _ in range(4)])
        probs = ProbabilityCalculator.calculate_probabilities(composition)

        # Should have probabilities for cards 1-10
        assert len(probs) == 10

        # Single cards should have 1/13 probability
        for i in range(1, 10):
            assert abs(probs[i] - 1/13) < 0.001

        # Tens (10, J, Q, K) should have 4/13 probability
        assert abs(probs[10] - 4/13) < 0.001

        # All probabilities should sum to 1
        assert abs(sum(probs.values()) - 1.0) < 0.001

    def test_compute_depth_zero(self):
        """Test computation with depth 0 (infinite deck)."""
        calc = ProbabilityCalculator(depth=0)
        calc.compute()

        assert calc.hard is not None
        assert calc.soft is not None

        # Validate probabilities sum to 1
        is_valid, message = calc.validate_probabilities()
        assert is_valid, message

    def test_compute_depth_one(self):
        """Test computation with depth 1."""
        calc = ProbabilityCalculator(depth=1)
        calc.compute()

        assert calc.hard is not None
        assert calc.soft is not None

        is_valid, message = calc.validate_probabilities()
        assert is_valid, message

    def test_get_dealer_probabilities(self):
        """Test getting dealer probabilities for specific card."""
        calc = ProbabilityCalculator(depth=0)
        calc.compute()

        probs = calc.get_dealer_probabilities(10)

        # Should have outcomes for 17-21 and Bust
        assert 17 in probs
        assert 18 in probs
        assert 19 in probs
        assert 20 in probs
        assert 21 in probs
        assert 'Bust' in probs

        # Probabilities should sum to 1
        assert abs(sum(probs.values()) - 1.0) < 0.001

        # With 10 showing, dealer should have high probability of 20
        assert probs[20] > 0.3

    def test_s17_vs_h17(self):
        """Test difference between S17 and H17 rules."""
        s17_calc = ProbabilityCalculator(rules=HouseRules(s17=True), depth=0)
        s17_calc.compute()

        h17_calc = ProbabilityCalculator(rules=HouseRules(s17=False), depth=0)
        h17_calc.compute()

        # Get probabilities for dealer showing Ace
        s17_probs = s17_calc.get_dealer_probabilities(1)
        h17_probs = h17_calc.get_dealer_probabilities(1)

        # H17 should have higher bust probability
        assert h17_probs['Bust'] > s17_probs['Bust']

    def test_validate_probabilities(self):
        """Test probability validation."""
        calc = ProbabilityCalculator(depth=0)
        calc.compute()

        is_valid, message = calc.validate_probabilities()
        assert is_valid
        assert 'sum to 1.0' in message

    def test_get_probabilities_before_compute(self):
        """Test that getting probabilities before compute raises error."""
        calc = ProbabilityCalculator()

        with pytest.raises(ValueError, match="Must call compute"):
            calc.get_dealer_probabilities(10)
