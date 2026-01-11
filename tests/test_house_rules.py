"""Tests for HouseRules class."""

import pytest
from blackjack_calculator.core.house_rules import HouseRules


class TestHouseRules:
    """Test cases for HouseRules class."""

    def test_default_initialization(self):
        """Test default rule initialization."""
        rules = HouseRules()
        assert rules.shoe_size == 8
        assert rules.s17 is True
        assert rules.blackjack_payout == 1.5
        assert rules.max_hands == 4

    def test_custom_initialization(self):
        """Test custom rule initialization."""
        rules = HouseRules(
            shoe_size=6,
            s17=False,
            blackjack_payout=1.2,
            max_hands=3
        )
        assert rules.shoe_size == 6
        assert rules.s17 is False
        assert rules.blackjack_payout == 1.2
        assert rules.max_hands == 3

    def test_invalid_shoe_size(self):
        """Test that invalid shoe size raises error."""
        with pytest.raises(ValueError, match="Shoe size must be"):
            HouseRules(shoe_size=10)

    def test_invalid_blackjack_payout(self):
        """Test that invalid payout raises error."""
        with pytest.raises(ValueError, match="Blackjack payout must be"):
            HouseRules(blackjack_payout=0.5)

    def test_vegas_strip_preset(self):
        """Test Vegas Strip factory method."""
        rules = HouseRules.vegas_strip()
        assert rules.shoe_size == 6
        assert rules.s17 is True
        assert rules.blackjack_payout == 1.5
        assert rules.double_after_split is True
        assert rules.late_surrender is True

    def test_atlantic_city_preset(self):
        """Test Atlantic City factory method."""
        rules = HouseRules.atlantic_city()
        assert rules.shoe_size == 8
        assert rules.s17 is True
        assert rules.resplit_aces is True

    def test_str_representation(self):
        """Test string representation."""
        rules = HouseRules.vegas_strip()
        str_repr = str(rules)
        assert '6 decks' in str_repr
        assert 'S17' in str_repr
        assert '1.5x BJ' in str_repr
