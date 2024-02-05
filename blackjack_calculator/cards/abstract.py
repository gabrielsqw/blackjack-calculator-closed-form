from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Self

from blackjack_calculator.house_rules import HouseRules

T_ = TypeVar("T_")


class AbstractCards(Generic[T_], ABC):
    """for purposes of this repo we assume 10 agnostic"""

    def __init__(self, deck: T_):
        self._deck = deck

    @property
    @abstractmethod
    def probabilities(self) -> T_:
        """Obtain probabilities for next draw realization, some array of sized 10"""

    @abstractmethod
    def draw_card(self, card: int) -> Self:
        """returns object after drawing a card"""

    @classmethod
    @abstractmethod
    def factory_from_house_rules(cls, rules: HouseRules) -> Self:
        """returns an initial instance of object given house rules"""
