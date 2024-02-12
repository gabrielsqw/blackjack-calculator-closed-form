from typing import Optional, Tuple

from blackjack_calculator.cards.abstract import AbstractCards
from blackjack_calculator.cards.np import NumpyCards
from blackjack_calculator.house_rules import HouseRules


class BlackjackCalculator:
    def __init__(
            self,
            house_rules: Optional[HouseRules] = None,
            cards: Optional[AbstractCards] = None
    ):
        self.house_rules: HouseRules = house_rules or HouseRules()
        self.cards: AbstractCards = (
                cards or NumpyCards.factory_from_house_rules(self.house_rules)
        )

    def calc_specific_hand(
            self, player_cards: Tuple[int, int], dealer_card: int, adjust_deck: bool = False
    ):
        """
        Calculates details for one specific hand
        Parameters
        ----------
        player_cards
            Tuple of int indicating player cards
        dealer_card
            Dealer up card
        adjust_deck : bool
            Boolean which indicates if current cards is after or before deck is
            observed. If cards are dealt after deck observation, deck needs to be
            adjusted and adjust_deck = True, otherwise False (default is False)
        """
        cards = self.cards
        if adjust_deck:
            cards = (
                cards
                .draw_card(player_cards[0])
                .draw_card(dealer_card)
                .draw_card(player_cards[1])
            )
        