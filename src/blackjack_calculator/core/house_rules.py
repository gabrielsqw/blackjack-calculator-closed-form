"""House rules configuration for blackjack games."""

from typing import List, Optional


class HouseRules:
    """
    Configuration object for blackjack table rules.

    This class encapsulates all the configurable rules that affect
    blackjack strategy and probability calculations.

    Attributes:
        shoe_size: Number of decks used in the shoe (4, 6, or 8)
        min_bet: Minimum bet allowed at the table
        max_bet: Maximum bet allowed at the table
        s17: True if dealer stands on soft 17, False if hits
        blackjack_payout: Payout multiplier for natural blackjack (1.5 = 3:2)
        max_hands: Maximum number of hands after splitting (2, 3, or 4)
        double_down: True if doubling allowed on any first two cards
        split_unlike_tens: True if can split unlike tens (e.g., J and Q)
        double_after_split: True if doubling after split is allowed
        resplit_aces: True if re-splitting aces is allowed
        insurance: True if insurance bet is allowed
        late_surrender: True if late surrender is allowed
        dealer_shows_hole_card: True if dealer always shows hole card
        dealer_peeks_aces: True if dealer peeks for blackjack with ace showing
        dealer_peeks_tens: True if dealer peeks for blackjack with ten showing
    """

    def __init__(
            self,
            shoe_size: int = 8,
            bet_limits: Optional[List[int]] = None,
            s17: bool = True,
            blackjack_payout: float = 1.5,
            max_hands: int = 4,
            double_down: bool = True,
            split_unlike_tens: bool = True,
            double_after_split: bool = True,
            resplit_aces: bool = False,
            insurance: bool = True,
            late_surrender: bool = True,
            dealer_shows_hole_card: bool = False,
            dealer_peeks_aces: bool = False,
            dealer_peeks_tens: bool = False
    ):
        """
        Initialize house rules.

        Args:
            shoe_size: Number of decks (4, 6, or 8)
            bet_limits: [min_bet, max_bet] or None for [0, 1]
            s17: True if dealer stands on soft 17
            blackjack_payout: Payout multiplier (1.5 for 3:2, 1.2 for 6:5)
            max_hands: Maximum hands after splitting (2, 3, or 4)
            double_down: Allow doubling on any first two cards
            split_unlike_tens: Allow splitting unlike tens (J-Q, etc.)
            double_after_split: Allow doubling after splitting
            resplit_aces: Allow re-splitting aces
            insurance: Allow insurance bet
            late_surrender: Allow late surrender
            dealer_shows_hole_card: Dealer always shows hole card
            dealer_peeks_aces: Dealer peeks for BJ when showing ace
            dealer_peeks_tens: Dealer peeks for BJ when showing ten

        Raises:
            ValueError: If invalid rule combinations or values provided
            TypeError: If bet limits are not integers
        """
        if bet_limits is None:
            bet_limits = [0, 1]

        # Validation
        if shoe_size not in [4, 6, 8]:
            raise ValueError('Shoe size must be 4, 6, or 8.')
        if len(bet_limits) != 2:
            raise ValueError('Bet limits should be a list of 2 integers.')
        if not all(isinstance(bet, int) for bet in bet_limits):
            raise TypeError('Bet limits need to be integer values.')
        if bet_limits[0] < 0:
            raise ValueError('Minimum bet at table must be an integer greater than 0.')
        if bet_limits[1] <= bet_limits[0]:
            raise ValueError('Maximum bet at table must be greater than minimum bet.')
        if blackjack_payout <= 1:
            raise ValueError('Blackjack payout must be greater than 1.')
        if max_hands not in [2, 3, 4]:
            raise ValueError('Maximum number of hands must be 2, 3, or 4.')
        if resplit_aces and max_hands == 2:
            raise ValueError('Max hands must be greater than 2 if re-splitting aces is allowed.')

        self._shoe_size = shoe_size
        self._min_bet = bet_limits[0]
        self._max_bet = bet_limits[1]
        self._s17 = s17
        self._blackjack_payout = blackjack_payout
        self._max_hands = max_hands
        self._double_down = double_down
        self._split_unlike_tens = split_unlike_tens
        self._double_after_split = double_after_split
        self._resplit_aces = resplit_aces
        self._insurance = insurance
        self._late_surrender = late_surrender
        self._dealer_shows_hole_card = dealer_shows_hole_card
        self._dealer_peeks_aces = dealer_peeks_aces
        self._dealer_peeks_tens = dealer_peeks_tens

    def __str__(self) -> str:
        """Return a human-readable string representation of the rules."""
        return '{shoe_size} decks,{s17} {blackjack_payout}{double_after_split}{resplit_aces}{late_surrender}'.format(
            shoe_size=self._shoe_size,
            s17=' S17,' if self._s17 else ' H17,',
            blackjack_payout=str(self._blackjack_payout) + 'x BJ,',
            double_after_split=' DAS,' if self._double_after_split else '',
            resplit_aces=' RSA,' if self._resplit_aces else '',
            late_surrender=' LS' if self._late_surrender else ''
        )

    # Properties
    @property
    def shoe_size(self) -> int:
        """Number of decks in the shoe."""
        return self._shoe_size

    @property
    def min_bet(self) -> int:
        """Minimum bet allowed."""
        return self._min_bet

    @property
    def max_bet(self) -> int:
        """Maximum bet allowed."""
        return self._max_bet

    @property
    def s17(self) -> bool:
        """True if dealer stands on soft 17."""
        return self._s17

    @property
    def blackjack_payout(self) -> float:
        """Blackjack payout multiplier."""
        return self._blackjack_payout

    @property
    def max_hands(self) -> int:
        """Maximum number of hands after splitting."""
        return self._max_hands

    @property
    def double_down(self) -> bool:
        """True if doubling down is allowed."""
        return self._double_down

    @property
    def split_unlike_tens(self) -> bool:
        """True if splitting unlike tens is allowed."""
        return self._split_unlike_tens

    @property
    def double_after_split(self) -> bool:
        """True if doubling after split is allowed."""
        return self._double_after_split

    @property
    def resplit_aces(self) -> bool:
        """True if re-splitting aces is allowed."""
        return self._resplit_aces

    @property
    def insurance(self) -> bool:
        """True if insurance is allowed."""
        return self._insurance

    @property
    def late_surrender(self) -> bool:
        """True if late surrender is allowed."""
        return self._late_surrender

    @property
    def dealer_shows_hole_card(self) -> bool:
        """True if dealer always shows hole card."""
        return self._dealer_shows_hole_card

    @property
    def dealer_peeks_aces(self) -> bool:
        """True if dealer peeks for blackjack when showing ace."""
        return self._dealer_peeks_aces

    @property
    def dealer_peeks_tens(self) -> bool:
        """True if dealer peeks for blackjack when showing ten."""
        return self._dealer_peeks_tens

    # Factory methods for common rule sets
    @classmethod
    def vegas_strip(cls) -> 'HouseRules':
        """
        Create rules for typical Las Vegas Strip casino.

        Returns:
            HouseRules: 6 decks, S17, 3:2 BJ, DAS, no RSA, LS allowed
        """
        return cls(
            shoe_size=6,
            s17=True,
            blackjack_payout=1.5,
            double_after_split=True,
            resplit_aces=False,
            late_surrender=True
        )

    @classmethod
    def vegas_downtown(cls) -> 'HouseRules':
        """
        Create rules for typical Las Vegas downtown casino.

        Returns:
            HouseRules: 6 decks, H17, 3:2 BJ, DAS, no RSA, LS allowed
        """
        return cls(
            shoe_size=6,
            s17=False,
            blackjack_payout=1.5,
            double_after_split=True,
            resplit_aces=False,
            late_surrender=True
        )

    @classmethod
    def atlantic_city(cls) -> 'HouseRules':
        """
        Create rules for typical Atlantic City casino.

        Returns:
            HouseRules: 8 decks, S17, 3:2 BJ, DAS, RSA, LS allowed
        """
        return cls(
            shoe_size=8,
            s17=True,
            blackjack_payout=1.5,
            double_after_split=True,
            resplit_aces=True,
            late_surrender=True,
            max_hands=4
        )

    @classmethod
    def european(cls) -> 'HouseRules':
        """
        Create rules for typical European casino.

        Returns:
            HouseRules: 6 decks, S17, 3:2 BJ, DAS, no RSA, no LS
        """
        return cls(
            shoe_size=6,
            s17=True,
            blackjack_payout=1.5,
            double_after_split=True,
            resplit_aces=False,
            late_surrender=False
        )

    @classmethod
    def unfavorable(cls) -> 'HouseRules':
        """
        Create unfavorable rules (6:5 blackjack, H17).

        Returns:
            HouseRules: 8 decks, H17, 6:5 BJ, limited options
        """
        return cls(
            shoe_size=8,
            s17=False,
            blackjack_payout=1.2,
            double_after_split=False,
            resplit_aces=False,
            late_surrender=False
        )
