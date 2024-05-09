import numpy as np
import pytest

from blackjack_calculator.cards.np import NumpyCards
from blackjack_calculator.cards.numba_methods import NumbaCards


@pytest.mark.parametrize(
    ("cards_type", "deck"), [
        (NumpyCards, np.array([0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 16])),
        (NumbaCards, np.array([0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 16])),
    ]
)
def test_singleton(cards_type, deck):
    a = cards_type(deck=deck)
    b = cards_type(deck=deck)
    assert isinstance(a, cards_type)
    assert a is b
