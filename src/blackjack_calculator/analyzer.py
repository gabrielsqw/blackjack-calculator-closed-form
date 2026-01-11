"""Main blackjack analyzer interface - ties all components together."""

from typing import Dict, List, Optional
import pandas as pd
from .core.house_rules import HouseRules
from .core.deck import Deck
from .core.hand import Hand
from .core.calculator import ProbabilityCalculator
from .strategy.expected_value import ExpectedValueCalculator
from .strategy.basic_strategy import BasicStrategy
from .strategy.recommendations import RecommendationEngine, ActionRecommendation


class BlackjackAnalyzer:
    """
    Main interface for blackjack analysis and recommendations.

    This class integrates all components of the blackjack calculator:
    - Probability calculation using Markov chains
    - Expected value analysis
    - Basic strategy generation
    - Action recommendations

    Usage:
        analyzer = BlackjackAnalyzer(rules=HouseRules.vegas_strip())
        analyzer.compute()  # Calculate probabilities
        rec = analyzer.get_recommendation([10, 6], dealer_card=10)
        print(rec)
    """

    def __init__(
            self,
            rules: Optional[HouseRules] = None,
            depth: int = 1,
            deck: Optional[Deck] = None
    ):
        """
        Initialize the blackjack analyzer.

        Args:
            rules: HouseRules instance (default: standard 8-deck rules)
            depth: Card counting depth for probability calculation (0-5)
            deck: Optional Deck instance for custom card composition
        """
        self.rules = rules if rules is not None else HouseRules()
        self.depth = depth
        self.deck = deck if deck is not None else Deck(self.rules)

        # Core calculator
        self.calculator = ProbabilityCalculator(
            rules=self.rules,
            deck=self.deck,
            depth=depth
        )

        # Strategy components (initialized after computation)
        self.ev_calculator_hard: Optional[ExpectedValueCalculator] = None
        self.ev_calculator_soft: Optional[ExpectedValueCalculator] = None
        self.basic_strategy_hard: Optional[BasicStrategy] = None
        self.basic_strategy_soft: Optional[BasicStrategy] = None
        self.recommendation_engine: Optional[RecommendationEngine] = None

        self._computed = False

    def compute(self) -> None:
        """
        Run probability calculations and initialize strategy components.

        This must be called before using recommendation features.
        """
        print("Computing dealer probabilities...")
        self.calculator.compute()

        # Validate results
        is_valid, message = self.calculator.validate_probabilities()
        if not is_valid:
            print(f"Warning: {message}")
        else:
            print("✓ Probability calculation complete and validated")

        # Initialize EV calculators
        self.ev_calculator_hard = ExpectedValueCalculator(
            self.calculator.hard,
            self.rules,
            hand_type="hard"
        )
        self.ev_calculator_soft = ExpectedValueCalculator(
            self.calculator.soft,
            self.rules,
            hand_type="soft"
        )

        # Initialize strategy generators
        self.basic_strategy_hard = BasicStrategy(
            self.ev_calculator_hard,
            self.rules
        )
        self.basic_strategy_soft = BasicStrategy(
            self.ev_calculator_soft,
            self.rules
        )

        # Initialize recommendation engine (uses hard by default)
        self.recommendation_engine = RecommendationEngine(
            self.ev_calculator_hard,
            self.rules
        )

        self._computed = True
        print("✓ Strategy components initialized")

    def get_recommendation(
            self,
            player_cards: List[int],
            dealer_card: int,
            can_double: bool = True,
            can_split: bool = True,
            can_surrender: bool = True
    ) -> ActionRecommendation:
        """
        Get action recommendation for a specific game situation.

        Args:
            player_cards: List of player's cards (e.g., [10, 6])
            dealer_card: Dealer's up card (1-10, where 1 = Ace)
            can_double: Whether doubling is allowed (default True)
            can_split: Whether splitting is allowed (default True)
            can_surrender: Whether surrender is allowed (default True)

        Returns:
            ActionRecommendation with optimal action and analysis

        Raises:
            RuntimeError: If compute() hasn't been called yet
        """
        self._ensure_computed()

        return self.recommendation_engine.get_recommendation(
            player_cards,
            dealer_card,
            can_double=can_double,
            can_split=can_split,
            can_surrender=can_surrender
        )

    def generate_strategy_chart(
            self,
            chart_type: str = 'all'
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate complete basic strategy chart(s).

        Args:
            chart_type: 'hard', 'soft', 'pair', or 'all'

        Returns:
            Dictionary of strategy DataFrames

        Raises:
            RuntimeError: If compute() hasn't been called yet
        """
        self._ensure_computed()

        if chart_type == 'all':
            return {
                'hard': self.basic_strategy_hard.generate_hard_strategy(),
                'soft': self.basic_strategy_soft.generate_soft_strategy(),
                'pair': self.basic_strategy_hard.generate_pair_strategy()
            }
        elif chart_type == 'hard':
            return {'hard': self.basic_strategy_hard.generate_hard_strategy()}
        elif chart_type == 'soft':
            return {'soft': self.basic_strategy_soft.generate_soft_strategy()}
        elif chart_type == 'pair':
            return {'pair': self.basic_strategy_hard.generate_pair_strategy()}
        else:
            raise ValueError(f"Invalid chart_type: {chart_type}")

    def print_strategy_chart(self, chart_type: str = 'all') -> None:
        """
        Print formatted basic strategy chart(s).

        Args:
            chart_type: 'hard', 'soft', 'pair', or 'all'

        Raises:
            RuntimeError: If compute() hasn't been called yet
        """
        self._ensure_computed()

        charts = self.generate_strategy_chart(chart_type)

        if 'hard' in charts:
            print("\n" + "=" * 60)
            print("HARD HANDS STRATEGY")
            print("=" * 60)
            print("Player Total vs Dealer Up Card (2-10, A)")
            print(charts['hard'].to_string())

        if 'soft' in charts:
            print("\n" + "=" * 60)
            print("SOFT HANDS STRATEGY")
            print("=" * 60)
            print("Soft Total vs Dealer Up Card (2-10, A)")
            print(charts['soft'].to_string())

        if 'pair' in charts:
            print("\n" + "=" * 60)
            print("PAIRS STRATEGY")
            print("=" * 60)
            print("Pair vs Dealer Up Card (2-10, A)")
            # Format pair index
            pair_df = charts['pair'].copy()
            pair_df.index = [f"{self._format_card(r)}-{self._format_card(r)}" for r in pair_df.index]
            print(pair_df.to_string())

        print("\n" + "=" * 60)
        print("LEGEND: H=Hit | S=Stand | D=Double | P=sPlit | R=suRrender")
        print("=" * 60)

    def get_dealer_probabilities(
            self,
            dealer_card: int
    ) -> Dict[str, float]:
        """
        Get probability distribution of dealer outcomes.

        Args:
            dealer_card: Dealer's up card (1-10)

        Returns:
            Dictionary mapping outcomes (17-21, 'Bust') to probabilities

        Raises:
            RuntimeError: If compute() hasn't been called yet
        """
        self._ensure_computed()
        return self.calculator.get_dealer_probabilities(dealer_card)

    def print_dealer_probabilities(self, dealer_card: Optional[int] = None) -> None:
        """
        Print dealer outcome probabilities.

        Args:
            dealer_card: Specific dealer card, or None for all cards
        """
        self._ensure_computed()

        if dealer_card is not None:
            probs = self.get_dealer_probabilities(dealer_card)
            card_name = "Ace" if dealer_card == 1 else str(dealer_card)
            print(f"\nDealer Probabilities (Up Card: {card_name})")
            print("-" * 40)
            for outcome, prob in probs.items():
                print(f"{outcome:>6s}: {prob:6.2%}")
        else:
            print("\nDealer Probabilities (All Up Cards)")
            print("=" * 60)
            for dc in list(range(2, 11)) + [1]:
                probs = self.get_dealer_probabilities(dc)
                card_name = "Ace" if dc == 1 else str(dc)
                print(f"\nUp Card: {card_name}")
                print("-" * 40)
                for outcome, prob in probs.items():
                    print(f"{outcome:>6s}: {prob:6.2%}")

    def analyze_situation(
            self,
            player_cards: List[int],
            dealer_card: int
    ) -> str:
        """
        Provide detailed analysis of a game situation.

        Args:
            player_cards: Player's cards
            dealer_card: Dealer's up card

        Returns:
            Formatted analysis string
        """
        self._ensure_computed()

        hand = Hand(player_cards)
        rec = self.get_recommendation(player_cards, dealer_card)
        dealer_probs = self.get_dealer_probabilities(dealer_card)

        dealer_name = "Ace" if dealer_card == 1 else str(dealer_card)

        lines = [
            "=" * 70,
            "BLACKJACK SITUATION ANALYSIS",
            "=" * 70,
            "",
            f"Player Hand: {hand}",
            f"Dealer Up Card: {dealer_name}",
            "",
            "DEALER OUTCOME PROBABILITIES:",
            "-" * 40,
        ]

        for outcome, prob in dealer_probs.items():
            lines.append(f"  {outcome:>6s}: {prob:6.2%}")

        lines.extend([
            "",
            "RECOMMENDED ACTION:",
            "-" * 40,
            str(rec),
            "",
            "=" * 70
        ])

        return "\n".join(lines)

    def export_strategies(self, filename_prefix: str = 'basic_strategy') -> None:
        """
        Export all strategy charts to CSV files.

        Args:
            filename_prefix: Prefix for output files
        """
        self._ensure_computed()

        charts = self.generate_strategy_chart('all')

        for chart_name, chart_df in charts.items():
            filename = f"{filename_prefix}_{chart_name}.csv"
            chart_df.to_csv(filename)
            print(f"Exported {chart_name} strategy to {filename}")

    def _ensure_computed(self) -> None:
        """Raise error if compute() hasn't been called."""
        if not self._computed:
            raise RuntimeError(
                "Must call compute() before using analysis features. "
                "Example: analyzer.compute()"
            )

    @staticmethod
    def _format_card(card: int) -> str:
        """Format card value for display."""
        if card == 1:
            return "A"
        elif card >= 11:
            face_cards = {11: "J", 12: "Q", 13: "K"}
            return face_cards.get(card, str(card))
        else:
            return str(card)

    def __repr__(self) -> str:
        """Return string representation."""
        status = "computed" if self._computed else "not computed"
        return f"BlackjackAnalyzer(rules={self.rules}, depth={self.depth}, status={status})"
