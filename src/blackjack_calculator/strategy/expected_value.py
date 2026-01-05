"""Expected value calculations for blackjack actions."""

from typing import Dict, Optional
import pandas as pd
from ..core.hand import Hand
from ..core.house_rules import HouseRules


class ExpectedValueCalculator:
    """
    Calculate expected values for blackjack actions.

    This class uses dealer probability distributions to compute the EV
    of each possible player action (hit, stand, double, split, surrender).
    """

    def __init__(
            self,
            dealer_probabilities: pd.DataFrame,
            rules: HouseRules,
            hand_type: str = "hard"
    ):
        """
        Initialize EV calculator.

        Args:
            dealer_probabilities: DataFrame of dealer outcome probabilities
            rules: HouseRules instance
            hand_type: 'hard' or 'soft'
        """
        self.dealer_probs = dealer_probabilities
        self.rules = rules
        self.hand_type = hand_type

    def calculate_stand_ev(self, player_value: int, dealer_card: int) -> float:
        """
        Calculate expected value of standing.

        Args:
            player_value: Player's hand value (4-21)
            dealer_card: Dealer's up card (1-10)

        Returns:
            Expected value of standing (as a fraction of bet)
        """
        if player_value > 21:
            return -1.0  # Already busted

        dealer_col = min(dealer_card, 10)
        if dealer_col not in self.dealer_probs.columns:
            raise ValueError(f"Invalid dealer card: {dealer_card}")

        probs = self.dealer_probs[dealer_col]

        ev = 0.0
        # Win against dealer bust
        ev += probs.get("Bust", 0.0) * 1.0

        # Compare against dealer standings
        for dealer_final in [17, 18, 19, 20, 21]:
            prob = probs.get(dealer_final, 0.0)
            if player_value > dealer_final:
                ev += prob * 1.0  # Win
            elif player_value < dealer_final:
                ev += prob * (-1.0)  # Lose
            # Push (player_value == dealer_final) adds 0

        return ev

    def calculate_hit_ev(
            self,
            player_value: int,
            dealer_card: int,
            is_soft: bool = False,
            hit_probabilities: Optional[Dict[int, float]] = None
    ) -> float:
        """
        Calculate expected value of hitting.

        This is an approximation that considers immediate outcomes.
        For more accuracy, would need recursive calculation.

        Args:
            player_value: Current hand value
            dealer_card: Dealer's up card
            is_soft: Whether hand is soft
            hit_probabilities: Probabilities of drawing each card (1-10)

        Returns:
            Approximate expected value of hitting
        """
        if player_value >= 21:
            return -1.0 if player_value > 21 else self.calculate_stand_ev(21, dealer_card)

        # Simple approximation: assume stand after one card
        # More sophisticated version would recursively calculate
        if hit_probabilities is None:
            # Assume uniform distribution (infinite deck approximation)
            hit_probabilities = {i: 1/13 for i in range(1, 10)}
            hit_probabilities[10] = 4/13  # 10, J, Q, K

        ev = 0.0
        for card, prob in hit_probabilities.items():
            new_value = player_value + card
            if is_soft and card != 1 and new_value > 21:
                # Soft hand becomes hard
                new_value = player_value - 10 + card

            if new_value > 21:
                ev += prob * (-1.0)  # Bust
            else:
                # Assume stand with new value
                ev += prob * self.calculate_stand_ev(new_value, dealer_card)

        return ev

    def calculate_double_ev(
            self,
            player_value: int,
            dealer_card: int,
            is_soft: bool = False,
            hit_probabilities: Optional[Dict[int, float]] = None
    ) -> float:
        """
        Calculate expected value of doubling down.

        Doubling means betting double but receiving only one more card.

        Args:
            player_value: Current hand value
            dealer_card: Dealer's up card
            is_soft: Whether hand is soft
            hit_probabilities: Probabilities of drawing each card

        Returns:
            Expected value of doubling (2x bet scale)
        """
        if hit_probabilities is None:
            hit_probabilities = {i: 1/13 for i in range(1, 10)}
            hit_probabilities[10] = 4/13

        ev = 0.0
        for card, prob in hit_probabilities.items():
            new_value = player_value + card
            if is_soft and card != 1 and new_value > 21:
                new_value = player_value - 10 + card

            if new_value > 21:
                ev += prob * (-2.0)  # Bust with double bet
            else:
                # Must stand, double the result
                ev += prob * (self.calculate_stand_ev(new_value, dealer_card) * 2.0)

        return ev

    def calculate_split_ev(
            self,
            pair_rank: int,
            dealer_card: int,
            hit_probabilities: Optional[Dict[int, float]] = None
    ) -> float:
        """
        Calculate expected value of splitting.

        This is a simplified calculation assuming optimal play after split.

        Args:
            pair_rank: Rank of the pair (1-10)
            dealer_card: Dealer's up card
            hit_probabilities: Probabilities of drawing each card

        Returns:
            Expected value of splitting (per original bet)
        """
        if hit_probabilities is None:
            hit_probabilities = {i: 1/13 for i in range(1, 10)}
            hit_probabilities[10] = 4/13

        # Simplified: play each hand starting with pair_rank
        # and one additional card
        total_ev = 0.0

        for card, prob in hit_probabilities.items():
            new_value = pair_rank + card
            if pair_rank == 1:  # Aces
                # Soft hand
                new_value = 11 + card
                if new_value > 21:
                    new_value = 2 + card

            # Assume standing after one card (typical for splits)
            if new_value > 21:
                total_ev += prob * (-1.0)
            else:
                total_ev += prob * self.calculate_stand_ev(new_value, dealer_card)

        # EV for two hands (multiply by 2, since splitting creates 2 bets)
        return total_ev * 2

    def calculate_surrender_ev(self) -> float:
        """
        Calculate expected value of surrendering.

        Returns:
            Expected value of surrender (always -0.5)
        """
        return -0.5

    def calculate_insurance_ev(self, dealer_card: int) -> float:
        """
        Calculate expected value of insurance bet.

        Insurance pays 2:1 and is offered when dealer shows ace.

        Args:
            dealer_card: Dealer's up card (should be 1/ace)

        Returns:
            Expected value of insurance (as fraction of insurance bet)
        """
        if dealer_card != 1:
            return 0.0  # Insurance only offered on dealer ace

        # Check probability of dealer blackjack
        # This would need access to card composition
        # Simplified: assume 4/13 probability of ten in hole
        prob_blackjack = 4/13

        # Insurance pays 2:1
        # Win: +2 with probability prob_blackjack
        # Lose: -1 with probability (1 - prob_blackjack)
        ev = prob_blackjack * 2.0 + (1 - prob_blackjack) * (-1.0)

        return ev

    def get_best_action(
            self,
            hand: Hand,
            dealer_card: int,
            can_double: bool = True,
            can_split: bool = True,
            can_surrender: bool = True,
            hit_probabilities: Optional[Dict[int, float]] = None
    ) -> Dict[str, float]:
        """
        Calculate EV for all valid actions and return them.

        Args:
            hand: Player's hand
            dealer_card: Dealer's up card
            can_double: Whether doubling is allowed
            can_split: Whether splitting is allowed
            can_surrender: Whether surrender is allowed
            hit_probabilities: Card draw probabilities

        Returns:
            Dictionary mapping action to EV
        """
        evs = {}
        player_value = hand.get_value()
        is_soft = hand.is_soft()

        # Always can stand (unless busted)
        if not hand.is_busted():
            evs['stand'] = self.calculate_stand_ev(player_value, dealer_card)
            evs['hit'] = self.calculate_hit_ev(
                player_value, dealer_card, is_soft, hit_probabilities
            )

        # Double down (if allowed and hand permits)
        if can_double and hand.can_double() and self.rules.double_down:
            evs['double'] = self.calculate_double_ev(
                player_value, dealer_card, is_soft, hit_probabilities
            )

        # Split (if allowed and hand is pair)
        if can_split and hand.can_split():
            pair_rank = hand.get_pair_rank()
            evs['split'] = self.calculate_split_ev(
                pair_rank, dealer_card, hit_probabilities
            )

        # Surrender (if allowed)
        if can_surrender and self.rules.late_surrender and len(hand.cards) == 2:
            evs['surrender'] = self.calculate_surrender_ev()

        return evs

    def get_optimal_action(
            self,
            hand: Hand,
            dealer_card: int,
            **kwargs
    ) -> tuple[str, float]:
        """
        Get the optimal action and its EV.

        Args:
            hand: Player's hand
            dealer_card: Dealer's up card
            **kwargs: Additional arguments for get_best_action

        Returns:
            Tuple of (action_name, expected_value)
        """
        evs = self.get_best_action(hand, dealer_card, **kwargs)
        if not evs:
            return "stand", 0.0

        optimal_action = max(evs.items(), key=lambda x: x[1])
        return optimal_action
