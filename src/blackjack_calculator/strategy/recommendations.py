"""High-level recommendation engine for blackjack decisions."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..core.hand import Hand
from ..core.house_rules import HouseRules
from .expected_value import ExpectedValueCalculator


@dataclass
class ActionRecommendation:
    """
    Recommendation for a blackjack decision.

    Attributes:
        recommended_action: The optimal action to take
        expected_value: EV of the recommended action
        all_actions: Dictionary of all valid actions and their EVs
        explanation: Human-readable explanation
        dealer_card: Dealer's up card
        player_hand: String representation of player hand
    """
    recommended_action: str
    expected_value: float
    all_actions: Dict[str, float]
    explanation: str
    dealer_card: int
    player_hand: str

    def __str__(self) -> str:
        """Return formatted recommendation."""
        lines = [
            f"Player Hand: {self.player_hand}",
            f"Dealer Up Card: {self._format_card(self.dealer_card)}",
            f"",
            f"RECOMMENDED: {self.recommended_action.upper()} (EV: {self.expected_value:.4f})",
            f"",
            "All Actions:",
        ]

        # Sort actions by EV
        sorted_actions = sorted(
            self.all_actions.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for action, ev in sorted_actions:
            marker = "→ " if action == self.recommended_action else "  "
            lines.append(f"{marker}{action:12s}: {ev:+.4f}")

        lines.append(f"\n{self.explanation}")

        return "\n".join(lines)

    @staticmethod
    def _format_card(card: int) -> str:
        """Format card value for display."""
        if card == 1:
            return "Ace"
        elif card == 11:
            return "Jack"
        elif card == 12:
            return "Queen"
        elif card == 13:
            return "King"
        else:
            return str(card)


class RecommendationEngine:
    """
    High-level engine for generating blackjack recommendations.

    This class provides a simple interface for getting action recommendations
    based on game state, combining probability calculation with EV analysis.
    """

    def __init__(
            self,
            ev_calculator: ExpectedValueCalculator,
            rules: HouseRules
    ):
        """
        Initialize recommendation engine.

        Args:
            ev_calculator: Expected value calculator
            rules: House rules
        """
        self.ev_calc = ev_calculator
        self.rules = rules

    def get_recommendation(
            self,
            player_cards: List[int],
            dealer_card: int,
            can_double: bool = True,
            can_split: bool = True,
            can_surrender: bool = True,
            hit_probabilities: Optional[Dict[int, float]] = None
    ) -> ActionRecommendation:
        """
        Get action recommendation for a game situation.

        Args:
            player_cards: List of player's cards (1-13)
            dealer_card: Dealer's up card (1-10)
            can_double: Whether doubling is allowed
            can_split: Whether splitting is allowed
            can_surrender: Whether surrender is allowed
            hit_probabilities: Optional card draw probabilities

        Returns:
            ActionRecommendation with optimal action and analysis
        """
        hand = Hand(player_cards, is_dealer=False)

        # Get all action EVs
        action_evs = self.ev_calc.get_best_action(
            hand,
            dealer_card,
            can_double=can_double,
            can_split=can_split,
            can_surrender=can_surrender,
            hit_probabilities=hit_probabilities
        )

        if not action_evs:
            # Fallback
            return ActionRecommendation(
                recommended_action="stand",
                expected_value=0.0,
                all_actions={"stand": 0.0},
                explanation="No valid actions available.",
                dealer_card=dealer_card,
                player_hand=str(hand)
            )

        # Find best action
        best_action, best_ev = max(action_evs.items(), key=lambda x: x[1])

        # Generate explanation
        explanation = self._generate_explanation(
            hand,
            dealer_card,
            best_action,
            best_ev,
            action_evs
        )

        return ActionRecommendation(
            recommended_action=best_action,
            expected_value=best_ev,
            all_actions=action_evs,
            explanation=explanation,
            dealer_card=dealer_card,
            player_hand=str(hand)
        )

    def _generate_explanation(
            self,
            hand: Hand,
            dealer_card: int,
            action: str,
            ev: float,
            all_evs: Dict[str, float]
    ) -> str:
        """
        Generate human-readable explanation for recommendation.

        Args:
            hand: Player's hand
            dealer_card: Dealer's up card
            action: Recommended action
            ev: Expected value of recommended action
            all_evs: All action EVs

        Returns:
            Explanation string
        """
        dealer_str = "Ace" if dealer_card == 1 else str(dealer_card)
        hand_value = hand.get_value()

        explanations = {
            'hit': f"Hit to improve your {hand_value}. Standing has lower EV against dealer's {dealer_str}.",
            'stand': f"Stand with {hand_value}. Hitting risks busting or worse outcomes.",
            'double': f"Double down - favorable situation. Expected value of {ev:.3f} units per original bet.",
            'split': f"Split your pair. Each hand has better EV than playing together.",
            'surrender': f"Surrender is optimal. This is a very unfavorable situation (EV: {ev:.3f})."
        }

        base_explanation = explanations.get(action, f"Take action: {action}")

        # Add context about EV
        if ev > 0.5:
            base_explanation += " Highly favorable situation."
        elif ev > 0:
            base_explanation += " Slightly favorable situation."
        elif ev > -0.2:
            base_explanation += " Close to even odds."
        elif ev > -0.5:
            base_explanation += " Slightly unfavorable, but best available option."
        else:
            base_explanation += " Unfavorable situation, minimize losses."

        # Mention close alternatives
        sorted_evs = sorted(all_evs.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_evs) > 1:
            second_best = sorted_evs[1]
            ev_diff = ev - second_best[1]
            if 0 < ev_diff < 0.05:
                base_explanation += f" Note: {second_best[0]} is close (EV: {second_best[1]:.3f})."

        return base_explanation

    def compare_scenarios(
            self,
            player_cards: List[int],
            dealer_cards: List[int]
    ) -> Dict[int, ActionRecommendation]:
        """
        Compare recommendations against multiple dealer up cards.

        Args:
            player_cards: Player's hand
            dealer_cards: List of dealer up cards to compare

        Returns:
            Dictionary mapping dealer card to recommendation
        """
        recommendations = {}
        for dealer_card in dealer_cards:
            rec = self.get_recommendation(player_cards, dealer_card)
            recommendations[dealer_card] = rec

        return recommendations

    def get_quick_advice(
            self,
            player_cards: List[int],
            dealer_card: int
    ) -> str:
        """
        Get quick one-line advice.

        Args:
            player_cards: Player's cards
            dealer_card: Dealer's up card

        Returns:
            One-line recommendation string
        """
        rec = self.get_recommendation(player_cards, dealer_card)
        return f"{rec.recommended_action.upper()} (EV: {rec.expected_value:+.3f})"

    def analyze_hand_progression(
            self,
            initial_cards: List[int],
            dealer_card: int,
            potential_hits: List[int]
    ) -> List[Tuple[List[int], ActionRecommendation]]:
        """
        Analyze what happens if player hits and receives specific cards.

        Args:
            initial_cards: Starting hand
            dealer_card: Dealer's up card
            potential_hits: Cards player might receive

        Returns:
            List of (new_hand, recommendation) tuples
        """
        results = []
        for hit_card in potential_hits:
            new_cards = initial_cards + [hit_card]
            rec = self.get_recommendation(
                new_cards,
                dealer_card,
                can_double=False,  # Already hit once
                can_split=False,
                can_surrender=False
            )
            results.append((new_cards, rec))

        return results
