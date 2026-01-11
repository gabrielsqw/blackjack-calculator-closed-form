"""Blackjack probability calculator using Markov chains."""

import copy
from collections import Counter
from typing import Dict, List, Optional, FrozenSet, Tuple, Any
import numpy as np
import pandas as pd
from .house_rules import HouseRules
from .deck import Deck


# Constants
MIN_STAND_VALUE = 17
MAX_HAND_VALUE = 21
MIN_SOFT_VALUE = 11
CARD_RANGE = range(1, 11)
BUST_LABEL = "Bust"
TERMINAL_SCORES = [17, 18, 19, 20, 21, BUST_LABEL]


class ProbabilityCalculator:
    """
    Calculate dealer outcome probabilities using Markov chain analysis.

    This class computes the probability distribution of dealer final hands
    using dynamic programming and Markov chains. It accounts for card removal
    effects by tracking discarded cards up to a specified depth.

    The calculator builds probability matrices for both hard and soft dealer
    hands, considering the house rules (particularly S17 vs H17).

    Attributes:
        rules: HouseRules configuration
        depth: Card counting depth (0 = infinite deck, higher = more accurate)
        cards_composition: Counter of available cards in shoe
        master: Dictionary storing probability matrices for different card compositions
        hard: Final probability DataFrame for hard hands
        soft: Final probability DataFrame for soft hands
    """

    def __init__(
            self,
            rules: Optional[HouseRules] = None,
            deck: Optional[Deck] = None,
            cards_composition: Optional[Counter] = None,
            player_cards: Optional[List[int]] = None,
            dealer_card: Optional[int] = None,
            depth: int = 1
    ):
        """
        Initialize the probability calculator.

        Args:
            rules: HouseRules instance (default: standard rules)
            deck: Deck instance to use for card composition
            cards_composition: Alternative card composition as Counter
            player_cards: Player's current cards (for card removal)
            dealer_card: Dealer's up card (for card removal)
            depth: Depth of card removal analysis (0-5, default 1)

        Raises:
            ValueError: If both deck and cards_composition are provided
        """
        if deck and cards_composition:
            raise ValueError('deck and cards_composition must not be both filled')

        self.rules = rules if rules is not None else HouseRules()
        self.depth = depth
        self.master: Dict[FrozenSet, Dict[str, Any]] = {}
        self.hard: Optional[pd.DataFrame] = None
        self.soft: Optional[pd.DataFrame] = None

        # Initialize card composition
        if deck:
            self.deck = deck
            self.cards_composition = Counter(deck.cards)
        elif cards_composition:
            self.cards_composition = cards_composition
        else:
            self.deck = Deck(self.rules)
            self.cards_composition = Counter(self.deck.cards)

        # Store player/dealer cards for context
        self.player_cards = player_cards if player_cards else []
        self.dealer_card = dealer_card
        self.dealer_cardval = min(10, dealer_card) if dealer_card else None
        self.player_cardval = sum(min(i, 10) for i in self.player_cards) if player_cards else 0

        # Generate terminal strategy (infinite deck baseline)
        self.default_strat = self._generate_terminal_probabilities({0: 0})

    @staticmethod
    def calculate_probabilities(card_composition: Counter) -> Dict[int, float]:
        """
        Calculate probability of drawing each card value (1-10).

        Face cards (J, Q, K) are combined into value 10.

        Args:
            card_composition: Counter of available cards

        Returns:
            Dictionary mapping card value (1-10) to probability
        """
        total_cards = sum(card_composition.values())
        if total_cards == 0:
            return {i: 0.0 for i in range(1, 11)}

        prob = {}
        for i in range(1, 10):
            prob[i] = card_composition.get(i, 0) / total_cards

        # Combine all face cards into 10
        try:
            prob[10] = (
                card_composition.get(10, 0) +
                card_composition.get(11, 0) +
                card_composition.get(12, 0) +
                card_composition.get(13, 0)
            ) / total_cards
        except KeyError:
            prob[10] = card_composition.get(10, 0) / total_cards

        return prob

    def _generate_discarded_cards(self) -> List[FrozenSet]:
        """
        Generate all possible combinations of discarded cards up to depth.

        This creates all unique card combinations that could be removed from
        the deck, represented as frozen sets of (card_value, count) tuples.

        Returns:
            List of FrozenSets representing discarded card combinations
        """
        discarded_cards = []
        template = dict(zip(range(1, 11), [0] * 10))

        # Depth 1: single cards
        temp_cards = []
        for i in range(1, 11):
            card_dict = template.copy()
            card_dict[i] += 1
            temp_cards.append(card_dict)
        discarded_cards += temp_cards

        if self.depth == 1:
            return [frozenset(i.items()) for i in discarded_cards]

        # Depth > 1: build combinations iteratively
        prev_cards = temp_cards
        for depth_level in range(2, self.depth + 1):
            temp_cards = []
            for card_combo in prev_cards:
                # Skip if already over 21
                total_value = sum(
                    np.array(list(card_combo.values())) * np.array(range(1, 11))
                )
                if total_value > MAX_HAND_VALUE:
                    continue

                # Add each possible card to this combination
                for card_val in range(1, 11):
                    new_combo = card_combo.copy()
                    new_combo[card_val] += 1
                    # Avoid duplicates
                    if new_combo not in temp_cards:
                        temp_cards.append(new_combo)

            discarded_cards += temp_cards
            prev_cards = temp_cards

        return [frozenset(i.items()) for i in discarded_cards]

    def _calculate_probabilities_for_discarded(
            self,
            discarded_cards: FrozenSet
    ) -> Dict[int, float]:
        """
        Calculate probabilities after removing discarded cards.

        Args:
            discarded_cards: FrozenSet of (card_value, count) tuples

        Returns:
            Probability distribution for remaining cards
        """
        composition = copy.deepcopy(self.cards_composition)
        for card_val, count in dict(discarded_cards).items():
            composition[card_val] -= count
        return self.calculate_probabilities(composition)

    def _generate_terminal_probabilities(
            self,
            prob: Dict[int, float]
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate terminal probability matrices (no card removal).

        This is the base case for infinite deck assumption.

        Args:
            prob: Probability distribution of drawing each card

        Returns:
            Dictionary with 'hard' and 'soft' DataFrames
        """
        hard = pd.DataFrame(0.0, index=TERMINAL_SCORES, columns=range(2, 32))
        soft = pd.DataFrame(0.0, index=TERMINAL_SCORES, columns=range(11, 32))

        # Terminal states for hard hands
        for value in range(31, MIN_STAND_VALUE - 1, -1):
            if value > MAX_HAND_VALUE:
                hard.loc[BUST_LABEL, value] = 1.0
            else:
                hard.loc[value, value] = 1.0

        # Terminal states for soft hands (soft 27-31 = hard 17-21)
        for value in range(31, 26, -1):
            soft.loc[value - 10, value] = 1.0

        # If probabilities are zero, return terminal states
        if min(prob.values()) <= 0:
            return {"hard": hard, "soft": soft}

        # Calculate probabilities for hitting
        for value in range(MIN_STAND_VALUE - 1, 1, -1):
            hard[value] = (
                soft[value + 11] * prob[1] +
                sum(hard[value + card] * prob[card] for card in range(2, 11))
            )

            if value > 11:
                soft[value + 10] = hard[value]
            elif value > 7:
                soft[value + 10] = hard[value + 10]
            elif value == 7:
                # S17 vs H17 rule
                if self.rules.s17:
                    soft[value + 10] = hard[value + 10]
                else:
                    soft[value + 10] = hard[value]
            else:
                soft[value + 10] = sum(
                    soft[value + 10 + card] * prob[card] for card in range(1, 11)
                )

        # Special case: soft 11 (A-A)
        soft[11] = sum(soft[11 + card] * prob[card] for card in range(1, 11))

        return {"hard": hard, "soft": soft}

    def _lookup_markov_column(
            self,
            discarded: FrozenSet,
            card: int,
            col: int,
            hand_type: str
    ) -> pd.Series:
        """
        Look up a Markov chain column with card removal.

        Args:
            discarded: Currently discarded cards
            card: Additional card to remove
            col: Hand value to look up
            hand_type: 'hard' or 'soft'

        Returns:
            Probability series for this state
        """
        # Check if already at terminal state
        if hand_type == "hard" and col >= MIN_STAND_VALUE:
            return self.default_strat[hand_type][col]
        if hand_type == "soft" and col >= 27:
            return self.default_strat[hand_type][col]

        # Create new discarded set with additional card
        discarded_dict = dict(discarded.copy())
        discarded_dict[card] = discarded_dict.get(card, 0) + 1
        new_discarded = frozenset(discarded_dict.items())

        try:
            return self.master[new_discarded][hand_type][col]
        except KeyError:
            # Card combination not in master (too rare/deep)
            return pd.Series(0.0, index=TERMINAL_SCORES)

    def _generate_markov_probabilities(
            self,
            discarded: FrozenSet,
            prob: Dict[int, float]
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate Markov probability matrices with card removal.

        Args:
            discarded: FrozenSet of discarded cards
            prob: Probability distribution after card removal

        Returns:
            Dictionary with 'hard' and 'soft' DataFrames
        """
        hard = pd.DataFrame(0.0, index=TERMINAL_SCORES, columns=range(2, 32))
        soft = pd.DataFrame(0.0, index=TERMINAL_SCORES, columns=range(11, 32))

        # Terminal states
        for value in range(31, MIN_STAND_VALUE - 1, -1):
            if value > MAX_HAND_VALUE:
                hard.loc[BUST_LABEL, value] = 1.0
            else:
                hard.loc[value, value] = 1.0

        for value in range(31, 26, -1):
            soft.loc[value - 10, value] = 1.0

        if min(prob.values()) <= 0:
            return {"hard": hard, "soft": soft}

        # Calculate with card removal
        for value in range(MIN_STAND_VALUE - 1, 1, -1):
            hard[value] = (
                self._lookup_markov_column(discarded, 1, value + 11, "soft") * prob[1] +
                sum(
                    self._lookup_markov_column(discarded, card, value + card, "hard") * prob[card]
                    for card in range(2, 11)
                )
            )

            if value > 11:
                soft[value + 10] = hard[value]
            elif value > 7:
                soft[value + 10] = hard[value + 10]
            elif value == 7:
                if self.rules.s17:
                    soft[value + 10] = hard[value + 10]
                else:
                    soft[value + 10] = hard[value]
            else:
                soft[value + 10] = sum(
                    self._lookup_markov_column(discarded, card, value + 10 + card, "soft") * prob[card]
                    for card in range(1, 11)
                )

        soft[11] = sum(
            self._lookup_markov_column(discarded, card, 11 + card, "soft") * prob[card]
            for card in range(1, 11)
        )

        return {"hard": hard, "soft": soft}

    def calculate_all_probabilities(self) -> None:
        """
        Calculate all probability matrices for all card removal combinations.

        This is the main computation method that builds the complete probability
        model using dynamic programming, working from deepest card removal back
        to the base case.
        """
        if self.depth == 0:
            # Infinite deck case
            result = self._generate_terminal_probabilities(
                self.calculate_probabilities(self.cards_composition)
            )
            self.hard = result["hard"]
            self.soft = result["soft"]
            return

        # Generate all discarded card combinations
        disc = self._generate_discarded_cards()

        # Store probabilities and metadata for each combination
        for combo in disc:
            self.master[combo] = {}
            self.master[combo]["p"] = self._calculate_probabilities_for_discarded(combo)
            self.master[combo]["depth"] = sum(dict(combo).values())

        # Calculate from deepest level back to shallowest
        for depth_level in range(self.depth, 0, -1):
            if depth_level == self.depth:
                # Deepest level: use terminal probabilities
                for combo in disc:
                    if self.master[combo]["depth"] == depth_level:
                        result = self._generate_terminal_probabilities(
                            self.master[combo]["p"]
                        )
                        self.master[combo]["hard"] = result["hard"]
                        self.master[combo]["soft"] = result["soft"]
            else:
                # Shallower levels: use Markov chain with lookups
                for combo in disc:
                    if self.master[combo]["depth"] == depth_level:
                        result = self._generate_markov_probabilities(
                            combo,
                            self.master[combo]["p"]
                        )
                        self.master[combo]["hard"] = result["hard"]
                        self.master[combo]["soft"] = result["soft"]

        # Calculate base case (no cards removed)
        empty_discarded = frozenset(dict(zip(range(1, 11), [0] * 10)).items())
        result = self._generate_markov_probabilities(
            empty_discarded,
            self.calculate_probabilities(self.cards_composition)
        )
        self.hard = result["hard"]
        self.soft = result["soft"]

    def compute(self) -> None:
        """
        Run the full probability calculation.

        This is the main entry point for computing dealer probabilities.
        After calling this method, results are available in self.hard and self.soft.
        """
        self.calculate_all_probabilities()

    def get_dealer_probabilities(
            self,
            dealer_card: int,
            hand_type: str = "hard"
    ) -> Dict[str, float]:
        """
        Get dealer outcome probabilities for a specific up card.

        Args:
            dealer_card: Dealer's up card (1-10, where 10 includes J/Q/K)
            hand_type: 'hard' or 'soft' (default 'hard')

        Returns:
            Dictionary mapping outcomes (17-21, 'Bust') to probabilities

        Raises:
            ValueError: If probabilities haven't been calculated yet
        """
        if self.hard is None or self.soft is None:
            raise ValueError("Must call compute() before getting probabilities")

        dealer_value = min(dealer_card, 10)
        if hand_type == "soft" and dealer_value + 10 in self.soft.columns:
            return self.soft[dealer_value + 10].to_dict()
        elif dealer_value in self.hard.columns:
            return self.hard[dealer_value].to_dict()
        else:
            raise ValueError(f"Invalid dealer card: {dealer_card}")

    def validate_probabilities(self) -> Tuple[bool, str]:
        """
        Validate that probability matrices sum to 1.0.

        Returns:
            Tuple of (is_valid, message)
        """
        if self.hard is None or self.soft is None:
            return False, "Probabilities not yet calculated"

        hard_sums = self.hard.sum(axis=0)
        soft_sums = self.soft.sum(axis=0)

        hard_valid = np.allclose(hard_sums, 1.0, rtol=1e-5)
        soft_valid = np.allclose(soft_sums, 1.0, rtol=1e-5)

        if hard_valid and soft_valid:
            return True, "All probabilities sum to 1.0"
        else:
            return False, f"Invalid sums - Hard: {hard_sums.describe()}, Soft: {soft_sums.describe()}"
