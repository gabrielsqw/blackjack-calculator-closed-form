"""Basic strategy table generation for blackjack."""

from typing import Dict, List, Optional
import pandas as pd
from ..core.house_rules import HouseRules
from ..core.hand import Hand
from .expected_value import ExpectedValueCalculator


class BasicStrategy:
    """
    Generate and represent basic strategy for blackjack.

    Basic strategy is the mathematically optimal way to play every hand
    based on the player's cards and dealer's up card.
    """

    def __init__(
            self,
            ev_calculator: ExpectedValueCalculator,
            rules: HouseRules
    ):
        """
        Initialize basic strategy generator.

        Args:
            ev_calculator: Expected value calculator with dealer probabilities
            rules: House rules configuration
        """
        self.ev_calc = ev_calculator
        self.rules = rules
        self.hard_strategy: Optional[pd.DataFrame] = None
        self.soft_strategy: Optional[pd.DataFrame] = None
        self.pair_strategy: Optional[pd.DataFrame] = None

    def generate_hard_strategy(self) -> pd.DataFrame:
        """
        Generate basic strategy for hard hands.

        Returns:
            DataFrame with player totals (rows) vs dealer up card (columns)
        """
        # Player hard totals: 5-20 (21 is always stand, <5 impossible with 2 cards)
        player_totals = range(5, 21)
        dealer_cards = range(2, 12)  # 2-10, and 11 for Ace

        strategy = pd.DataFrame(index=player_totals, columns=dealer_cards, dtype=str)

        for player_value in player_totals:
            for dealer_card in dealer_cards:
                # Convert 11 to 1 for ace
                actual_dealer = 1 if dealer_card == 11 else dealer_card

                # Create a dummy hard hand
                # Use cards that sum to player_value (e.g., 10 + (value-10))
                if player_value >= 12:
                    hand = Hand([10, player_value - 10], is_dealer=False)
                else:
                    hand = Hand([player_value - 2, 2], is_dealer=False)

                # Get best action
                evs = self.ev_calc.get_best_action(
                    hand,
                    actual_dealer,
                    can_double=len(hand.cards) == 2,
                    can_split=False,  # Hard hands can't split
                    can_surrender=len(hand.cards) == 2
                )

                if evs:
                    best_action = max(evs.items(), key=lambda x: x[1])[0]
                    strategy.loc[player_value, dealer_card] = self._action_abbreviation(best_action)
                else:
                    strategy.loc[player_value, dealer_card] = 'S'  # Default stand

        self.hard_strategy = strategy
        return strategy

    def generate_soft_strategy(self) -> pd.DataFrame:
        """
        Generate basic strategy for soft hands.

        Returns:
            DataFrame with soft totals (rows) vs dealer up card (columns)
        """
        # Soft hands: A-2 through A-9 (A-10 is blackjack, A-A is pair)
        # Represented as soft 13 through soft 20
        soft_totals = range(13, 21)  # Soft 13 (A-2) to Soft 20 (A-9)
        dealer_cards = range(2, 12)

        strategy = pd.DataFrame(index=soft_totals, columns=dealer_cards, dtype=str)

        for soft_value in soft_totals:
            for dealer_card in dealer_cards:
                actual_dealer = 1 if dealer_card == 11 else dealer_card

                # Create soft hand: Ace (1) + other card
                other_card = soft_value - 11  # e.g., soft 13 = A + 2
                hand = Hand([1, other_card], is_dealer=False)

                evs = self.ev_calc.get_best_action(
                    hand,
                    actual_dealer,
                    can_double=len(hand.cards) == 2,
                    can_split=False,
                    can_surrender=len(hand.cards) == 2
                )

                if evs:
                    best_action = max(evs.items(), key=lambda x: x[1])[0]
                    strategy.loc[soft_value, dealer_card] = self._action_abbreviation(best_action)
                else:
                    strategy.loc[soft_value, dealer_card] = 'S'

        self.soft_strategy = strategy
        return strategy

    def generate_pair_strategy(self) -> pd.DataFrame:
        """
        Generate basic strategy for pairs.

        Returns:
            DataFrame with pair ranks (rows) vs dealer up card (columns)
        """
        # Pairs: 2-2 through A-A
        pair_ranks = list(range(2, 11)) + [1]  # 2-10, then Ace
        dealer_cards = range(2, 12)

        strategy = pd.DataFrame(index=pair_ranks, columns=dealer_cards, dtype=str)

        for pair_rank in pair_ranks:
            for dealer_card in dealer_cards:
                actual_dealer = 1 if dealer_card == 11 else dealer_card

                # Create pair hand
                hand = Hand([pair_rank, pair_rank], is_dealer=False)

                evs = self.ev_calc.get_best_action(
                    hand,
                    actual_dealer,
                    can_double=True,
                    can_split=True,
                    can_surrender=True
                )

                if evs:
                    best_action = max(evs.items(), key=lambda x: x[1])[0]
                    strategy.loc[pair_rank, dealer_card] = self._action_abbreviation(best_action)
                else:
                    strategy.loc[pair_rank, dealer_card] = 'S'

        self.pair_strategy = strategy
        return strategy

    def generate_all_strategies(self) -> Dict[str, pd.DataFrame]:
        """
        Generate all basic strategy tables.

        Returns:
            Dictionary with 'hard', 'soft', and 'pair' DataFrames
        """
        return {
            'hard': self.generate_hard_strategy(),
            'soft': self.generate_soft_strategy(),
            'pair': self.generate_pair_strategy()
        }

    def get_action(
            self,
            hand: Hand,
            dealer_card: int
    ) -> str:
        """
        Get the basic strategy action for a specific situation.

        Args:
            hand: Player's hand
            dealer_card: Dealer's up card (1-10)

        Returns:
            Action abbreviation (H/S/D/P/R)
        """
        # Ensure strategies are generated
        if self.hard_strategy is None:
            self.generate_all_strategies()

        # Convert dealer ace to column 11
        dealer_col = 11 if dealer_card == 1 else dealer_card

        if hand.is_pair() and len(hand.cards) == 2:
            pair_rank = hand.get_pair_rank()
            return self.pair_strategy.loc[pair_rank, dealer_col]
        elif hand.is_soft():
            soft_value = hand.get_value()
            if soft_value in self.soft_strategy.index:
                return self.soft_strategy.loc[soft_value, dealer_col]
            else:
                return 'S'  # Soft 21, always stand
        else:
            hard_value = hand.get_value()
            if hard_value in self.hard_strategy.index:
                return self.hard_strategy.loc[hard_value, dealer_col]
            elif hard_value >= 21:
                return 'S'  # 21 or busted
            else:
                return 'H'  # Low totals, hit

    @staticmethod
    def _action_abbreviation(action: str) -> str:
        """
        Convert action name to abbreviation.

        Args:
            action: Full action name

        Returns:
            Single letter abbreviation
        """
        mapping = {
            'hit': 'H',
            'stand': 'S',
            'double': 'D',
            'split': 'P',
            'surrender': 'R'
        }
        return mapping.get(action, 'S')

    @staticmethod
    def _format_pair_index(pair_rank: int) -> str:
        """
        Format pair rank for display.

        Args:
            pair_rank: Card rank (1-10)

        Returns:
            Formatted string (e.g., 'A-A', '10-10')
        """
        if pair_rank == 1:
            return 'A-A'
        else:
            return f'{pair_rank}-{pair_rank}'

    def print_strategy(self, strategy_type: str = 'all') -> None:
        """
        Print formatted strategy table(s).

        Args:
            strategy_type: 'hard', 'soft', 'pair', or 'all'
        """
        if strategy_type in ['hard', 'all']:
            if self.hard_strategy is not None:
                print("\n=== HARD HANDS ===")
                print("Player Total vs Dealer Up Card")
                print(self.hard_strategy.to_string())

        if strategy_type in ['soft', 'all']:
            if self.soft_strategy is not None:
                print("\n=== SOFT HANDS ===")
                print("Soft Total vs Dealer Up Card")
                print(self.soft_strategy.to_string())

        if strategy_type in ['pair', 'all']:
            if self.pair_strategy is not None:
                print("\n=== PAIRS ===")
                print("Pair vs Dealer Up Card")
                # Rename index for better display
                display_df = self.pair_strategy.copy()
                display_df.index = [self._format_pair_index(r) for r in display_df.index]
                print(display_df.to_string())

        print("\nLegend: H=Hit, S=Stand, D=Double, P=sPlit, R=suRrender")

    def export_to_csv(self, filename_prefix: str = 'basic_strategy') -> None:
        """
        Export strategy tables to CSV files.

        Args:
            filename_prefix: Prefix for output files
        """
        if self.hard_strategy is not None:
            self.hard_strategy.to_csv(f'{filename_prefix}_hard.csv')
        if self.soft_strategy is not None:
            self.soft_strategy.to_csv(f'{filename_prefix}_soft.csv')
        if self.pair_strategy is not None:
            pair_df = self.pair_strategy.copy()
            pair_df.index = [self._format_pair_index(r) for r in pair_df.index]
            pair_df.to_csv(f'{filename_prefix}_pairs.csv')
