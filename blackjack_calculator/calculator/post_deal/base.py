from typing import TypeVar

from blackjack_calculator.calculator.post_deal.context import BlackjackContext
from blackjack_calculator.cards.abstract import AbstractCards

_T_Cards = TypeVar("_T_Cards", bound=AbstractCards)


class AbstractBlackjackPostDealCalculator:
    def __init__(
        self,
        player_cards: list[int],
        dealer_card: int,
        deck: _T_Cards,
        context: BlackjackContext,
    ) -> None:
        self.player_cards = player_cards
        self.dealer_card = dealer_card
        self.deck = deck
        self.context = context

    def compute_ev(self) -> float:
        pass
