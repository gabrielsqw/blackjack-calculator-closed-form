"""Hand representation and evaluation for blackjack."""

from typing import List, Tuple, Optional
from enum import Enum


class HandType(Enum):
    """Type of blackjack hand."""
    HARD = "hard"
    SOFT = "soft"
    PAIR = "pair"
    BLACKJACK = "blackjack"
    BUST = "bust"


class Hand:
    """
    Represents a blackjack hand with evaluation logic.

    This class manages a player's or dealer's hand, tracking cards and
    computing hand values, types, and valid actions.

    Attributes:
        cards: List of card values in the hand (1-13)
        is_dealer: True if this is a dealer hand
    """

    def __init__(self, cards: Optional[List[int]] = None, is_dealer: bool = False):
        """
        Initialize a hand.

        Args:
            cards: Initial cards (1-13, where 1=Ace, 11=J, 12=Q, 13=K)
            is_dealer: Whether this is a dealer hand
        """
        self.cards: List[int] = cards if cards else []
        self.is_dealer = is_dealer
        self._split_from_pair = False

    def add_card(self, card: int) -> None:
        """
        Add a card to the hand.

        Args:
            card: Card value (1-13)
        """
        self.cards.append(card)

    def get_value(self) -> int:
        """
        Calculate the best total value of the hand.

        Aces are counted as 11 if possible without busting, otherwise 1.

        Returns:
            Best hand value (using soft ace if beneficial)
        """
        if not self.cards:
            return 0

        # Convert face cards to 10
        values = [min(card, 10) for card in self.cards]
        total = sum(values)
        num_aces = values.count(1)

        # Try to use one ace as 11
        if num_aces > 0 and total + 10 <= 21:
            return total + 10

        return total

    def get_hard_value(self) -> int:
        """
        Get the hard value (all aces count as 1).

        Returns:
            Hard total of the hand
        """
        if not self.cards:
            return 0
        values = [min(card, 10) for card in self.cards]
        return sum(values)

    def is_soft(self) -> bool:
        """
        Check if this is a soft hand (contains an ace counted as 11).

        Returns:
            True if hand is soft, False otherwise
        """
        if not self.cards:
            return False

        values = [min(card, 10) for card in self.cards]
        total = sum(values)
        num_aces = values.count(1)

        return num_aces > 0 and total + 10 <= 21

    def is_pair(self) -> bool:
        """
        Check if this hand is a pair (first two cards same value).

        Returns:
            True if hand is a pair, False otherwise
        """
        if len(self.cards) != 2:
            return False

        # Compare card values (treating all face cards as 10)
        val1 = min(self.cards[0], 10)
        val2 = min(self.cards[1], 10)
        return val1 == val2

    def is_blackjack(self) -> bool:
        """
        Check if this is a natural blackjack (ace + ten-value on first two cards).

        Returns:
            True if natural blackjack, False otherwise
        """
        if len(self.cards) != 2 or self._split_from_pair:
            return False

        values = [min(card, 10) for card in self.cards]
        return sorted(values) == [1, 10]

    def is_busted(self) -> bool:
        """
        Check if hand is busted (value > 21).

        Returns:
            True if busted, False otherwise
        """
        return self.get_value() > 21

    def get_hand_type(self) -> HandType:
        """
        Determine the type of this hand.

        Returns:
            HandType enum value
        """
        if self.is_busted():
            return HandType.BUST
        if self.is_blackjack():
            return HandType.BLACKJACK
        if self.is_pair():
            return HandType.PAIR
        if self.is_soft():
            return HandType.SOFT
        return HandType.HARD

    def get_pair_rank(self) -> Optional[int]:
        """
        Get the rank of cards in a pair.

        Returns:
            Card rank (1-10) if pair, None otherwise
        """
        if not self.is_pair():
            return None
        return min(self.cards[0], 10)

    def can_split(self) -> bool:
        """
        Check if this hand can be split.

        Returns:
            True if hand can be split, False otherwise
        """
        return self.is_pair() and len(self.cards) == 2

    def can_double(self) -> bool:
        """
        Check if this hand can be doubled.

        Typically only allowed on first two cards.

        Returns:
            True if hand can be doubled, False otherwise
        """
        return len(self.cards) == 2

    def split(self) -> Tuple['Hand', 'Hand']:
        """
        Split this hand into two hands.

        Returns:
            Tuple of two new Hand instances

        Raises:
            ValueError: If hand cannot be split
        """
        if not self.can_split():
            raise ValueError("Cannot split this hand")

        hand1 = Hand([self.cards[0]], is_dealer=self.is_dealer)
        hand2 = Hand([self.cards[1]], is_dealer=self.is_dealer)
        hand1._split_from_pair = True
        hand2._split_from_pair = True

        return hand1, hand2

    def __str__(self) -> str:
        """Return string representation of the hand."""
        card_strs = []
        for card in self.cards:
            if card == 1:
                card_strs.append('A')
            elif card == 11:
                card_strs.append('J')
            elif card == 12:
                card_strs.append('Q')
            elif card == 13:
                card_strs.append('K')
            else:
                card_strs.append(str(card))

        hand_type = self.get_hand_type()
        value = self.get_value()

        if hand_type == HandType.BLACKJACK:
            return f"[{', '.join(card_strs)}] = Blackjack!"
        elif hand_type == HandType.BUST:
            return f"[{', '.join(card_strs)}] = Bust ({value})"
        elif hand_type == HandType.SOFT:
            hard_val = self.get_hard_value()
            return f"[{', '.join(card_strs)}] = Soft {value} (Hard {hard_val})"
        elif hand_type == HandType.PAIR:
            return f"[{', '.join(card_strs)}] = Pair of {card_strs[0]}s ({value})"
        else:
            return f"[{', '.join(card_strs)}] = {value}"

    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Hand(cards={self.cards}, value={self.get_value()}, type={self.get_hand_type().value})"
