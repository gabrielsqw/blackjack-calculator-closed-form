"""Tests for Hand class."""

import pytest
from blackjack_calculator.core.hand import Hand, HandType


class TestHand:
    """Test cases for Hand class."""

    def test_empty_hand(self):
        """Test empty hand initialization."""
        hand = Hand()
        assert hand.get_value() == 0
        assert not hand.is_soft()
        assert not hand.is_pair()

    def test_hard_hand_value(self):
        """Test hard hand value calculation."""
        hand = Hand([10, 6])
        assert hand.get_value() == 16
        assert not hand.is_soft()
        assert hand.get_hand_type() == HandType.HARD

    def test_soft_hand_value(self):
        """Test soft hand value calculation."""
        hand = Hand([1, 7])  # Ace-7 = Soft 18
        assert hand.get_value() == 18
        assert hand.is_soft()
        assert hand.get_hand_type() == HandType.SOFT

    def test_blackjack(self):
        """Test blackjack detection."""
        hand = Hand([1, 10])
        assert hand.is_blackjack()
        assert hand.get_value() == 21
        assert hand.get_hand_type() == HandType.BLACKJACK

    def test_pair_detection(self):
        """Test pair detection."""
        hand = Hand([8, 8])
        assert hand.is_pair()
        assert hand.get_pair_rank() == 8
        assert hand.can_split()

    def test_face_card_pair(self):
        """Test face cards as pairs."""
        hand = Hand([11, 12])  # Jack and Queen
        assert hand.is_pair()  # Both count as 10
        assert hand.get_pair_rank() == 10

    def test_bust(self):
        """Test bust detection."""
        hand = Hand([10, 10, 5])
        assert hand.is_busted()
        assert hand.get_hand_type() == HandType.BUST
        assert hand.get_value() > 21

    def test_ace_counting(self):
        """Test ace is counted as 1 when 11 would bust."""
        hand = Hand([1, 10, 10])  # Should be 21, not 31
        assert hand.get_value() == 21
        assert not hand.is_soft()

    def test_multiple_aces(self):
        """Test multiple aces handled correctly."""
        hand = Hand([1, 1, 9])  # A-A-9 = 21
        assert hand.get_value() == 21
        assert hand.is_soft()

    def test_add_card(self):
        """Test adding cards to hand."""
        hand = Hand([10, 6])
        hand.add_card(5)
        assert hand.get_value() == 21
        assert len(hand.cards) == 3

    def test_can_double(self):
        """Test double down availability."""
        hand = Hand([10, 6])
        assert hand.can_double()

        hand.add_card(5)
        assert not hand.can_double()

    def test_split_hand(self):
        """Test splitting a pair."""
        hand = Hand([8, 8])
        hand1, hand2 = hand.split()

        assert len(hand1.cards) == 1
        assert len(hand2.cards) == 1
        assert hand1.cards[0] == 8
        assert hand2.cards[0] == 8

    def test_cannot_split_non_pair(self):
        """Test that non-pairs cannot be split."""
        hand = Hand([10, 6])
        with pytest.raises(ValueError):
            hand.split()

    def test_str_representation(self):
        """Test string representation."""
        hand = Hand([10, 6])
        str_repr = str(hand)
        assert '16' in str_repr

        blackjack = Hand([1, 10])
        assert 'Blackjack' in str(blackjack)
