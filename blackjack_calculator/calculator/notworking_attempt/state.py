import numpy as np

from blackjack_calculator.house_rules import HouseRules


class BlackjackState:
    """Object to control the state of the game given house rules"""

    def __init__(self, rules: HouseRules, state: np.ndarray):
        """state is an array with values at positions:
        0: number of hands
        1: first card value"""
        self._rules = rules
        self._state = state

    def perform_split(self) -> np.ndarray:
        n = np.zeros(self._state.size, self._state.dtype)
        n[0] = 1
        return self._state + n

    def can_split(self) -> bool:
