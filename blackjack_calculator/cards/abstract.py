import sys
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from blackjack_calculator.house_rules import HouseRules

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

_T = TypeVar("_T")


class AbstractCards(Generic[_T], ABC):
    """for purposes of this repo we assume 10 agnostic"""

    def __init__(self, deck: _T):
        self._deck = deck

    @property
    @abstractmethod
    def probabilities(self) -> _T:
        """Obtain probabilities for next draw realization, some array of sized 10"""

    @abstractmethod
    def draw_card(self, card: int) -> Self:
        """returns object after drawing a card"""

    @classmethod
    @abstractmethod
    def factory_from_house_rules(cls, rules: HouseRules) -> Self:
        """returns an initial instance of object given house rules"""
