import sys

from blackjack_calculator.house_rules import HouseRules

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class BlackjackContext:
    def __init__(self, rules: HouseRules, split_count: int = 0):
        self.rules = rules
        self.split_count = split_count

    def context_after_split(self) -> Self:
        """Returns context after splitting the hand"""
        return type(self)(rules=self.rules, split_count=self.split_count + 1)

    def can_split(self, player_cards: list[int]) -> bool:
        """Checks
        1. number of cards in hand is 2 (have not actioned)
        2. both cards have same value
        3. if cards are aces, checks if rules allow respliting if already split before
        """
        return all(
            [
                len(player_cards) == 2,
                player_cards[0] == player_cards[1],
                player_cards[0] != 1
                or self.split_count == 0
                or self.rules.resplit_aces,
                not self.rules.has_max_split
                or self.split_count < self.rules.max_split_count,
            ]
        )

    def can_double(self, player_cards: list[int]) -> bool:
        """Checks if
        1. number of cards in hand is 2 (have not actioned)
        """
        return all(
            [
                len(player_cards) == 2,
                self.rules.double_down,
                self.split_count == 0 or self.rules.double_after_split,
            ]
        )
