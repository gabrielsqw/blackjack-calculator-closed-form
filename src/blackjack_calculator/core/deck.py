"""Deck and shoe management for blackjack games."""

import random
from typing import List
import numpy as np
from .house_rules import HouseRules


class Deck:
    """
    Manages a shoe of cards at a blackjack table.

    This class handles card dealing, shuffling, and tracking for blackjack
    games. Cards are represented as integers 1-13 (Ace through King).

    Attributes:
        cards: List of remaining cards in the shoe
        total_cards: Total number of cards when shoe is full
        seen_cards: Array tracking count of each card value seen (1-13)
    """

    def __init__(self, rules: HouseRules = None):
        """
        Initialize a shoe of cards.

        Args:
            rules: HouseRules instance specifying shoe size (defaults to 8 decks)
        """
        if rules is None:
            rules = HouseRules()

        # Cards 2-10, J(11), Q(12), K(13), A(1) - 4 of each per deck
        self._cards: List[int] = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1] * 4 * rules.shoe_size
        self._total_cards: int = 52 * rules.shoe_size
        self._seen_cards: np.ndarray = np.array([0] * 13)

    @property
    def cards(self) -> List[int]:
        """Return the list of remaining cards in the shoe."""
        return self._cards

    @property
    def total_cards(self) -> int:
        """Return the total number of cards when shoe is full."""
        return self._total_cards

    @property
    def seen_cards(self) -> np.ndarray:
        """Return array of seen card counts (indexed 0-12 for cards 1-13)."""
        return self._seen_cards

    @seen_cards.setter
    def seen_cards(self, value: np.ndarray) -> None:
        """Set the seen cards array."""
        self._seen_cards = value

    def add_to_seen_cards(self, card: int) -> None:
        """
        Add a card to the seen cards tracker.

        Args:
            card: Card value (1-13)
        """
        self._seen_cards[card - 1] += 1

    def burn_card(self) -> int:
        """
        Remove and return the top card without marking it as seen.

        Returns:
            The burned card value

        Raises:
            IndexError: If shoe is empty
        """
        return self._cards.pop()

    def shuffle(self) -> None:
        """Shuffle the remaining cards in the shoe."""
        random.shuffle(self._cards)

    def deal_card(self, seen: bool = True) -> int:
        """
        Deal a card from the shoe.

        Args:
            seen: Whether to track this card as seen (default True)

        Returns:
            The dealt card value (1-13)

        Raises:
            IndexError: If shoe is empty
        """
        card = self._cards.pop()
        if seen:
            self.add_to_seen_cards(card=card)
        return card

    def remaining_decks(self) -> float:
        """
        Calculate the number of remaining decks in the shoe.

        Returns:
            Approximate number of decks remaining (rounded to nearest deck)
        """
        return round(len(self._cards) / 52, 0)

    def cut_card_reached(self, penetration: float) -> bool:
        """
        Check if the cut card has been reached based on penetration.

        Args:
            penetration: Deck penetration as a decimal (0.5 to 0.9)

        Returns:
            True if cut card has been reached, False otherwise

        Raises:
            ValueError: If penetration is not between 0.5 and 0.9
        """
        if penetration < 0.5 or penetration > 0.9:
            raise ValueError('Penetration must be between 0.5 and 0.9.')
        used_cards = self._total_cards - len(self._cards)
        return used_cards / self._total_cards >= penetration

    def cards_remaining(self) -> int:
        """
        Get the number of cards remaining in the shoe.

        Returns:
            Number of cards left
        """
        return len(self._cards)

    def reset(self, rules: HouseRules = None) -> None:
        """
        Reset the shoe to a fresh state.

        Args:
            rules: Optional new rules to apply (keeps existing if None)
        """
        if rules is None:
            # Just reset with same size
            shoe_size = self._total_cards // 52
            self._cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1] * 4 * shoe_size
        else:
            self._cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1] * 4 * rules.shoe_size
            self._total_cards = 52 * rules.shoe_size
        self._seen_cards = np.array([0] * 13)
