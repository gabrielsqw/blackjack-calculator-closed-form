# referenced from https://github.com/1andDone/blackjack/blob/master/house_rules.py
from typing import List


class HouseRules:
    """
    HouseRules is an object where all the table rules are set.
    """

    # pylint: disable=too-many-instance-attributes,too-many-arguments
    def __init__(
        self,
        shoe_size: int = 8,
        bet_limits: List[int | float] | None = None,
        s17: bool = True,
        blackjack_payout: float = 1.5,
        max_hands: int = 4,
        double_down: bool = True,
        split_unlike_tens: bool = True,
        double_after_split: bool = True,
        resplit_aces: bool = False,
        immediate_distribute_after_split: bool = True,
        no_bj_no_action_after_split_aces: bool = True,
        insurance: bool = True,
        late_surrender: bool = True,
        dealer_shows_hole_card: bool = False,
        dealer_peeks_aces: bool = False,
        dealer_peeks_tens: bool = False,
    ):
        """
        Parameters
        ----------
        shoe_size: int
            Number of decks used during a blackjack game
        bet_limits : list
            List containing the minimum and maximum bet allowed at the table
        s17 : bool, optional
            True if dealer stands on a soft 17, false otherwise (default is True)
        blackjack_payout : float, optional
            Payout for a player receiving a natural blackjack (default is 1.5, which
            implies a 3:2 payout)
        max_hands : int, optional
            Maximum number of hands that a player can play (default is 4)
        double_down : bool, optional
            True if doubling is allowed on any first two cards, false otherwise (default
             is True)
        split_unlike_tens : bool, optional
            True if able to split unlike 10's (i.e. 'J' and 'Q'), false otherwise
            (default is True)
        double_after_split : bool, optional
            True if doubling after splits is allowed, false otherwise (default is True)
        resplit_aces : bool, optional
            True if re-splitting aces is allowed, false otherwise (default is False)
        immediate_distribute_after_split: bool
            True if both hands are dealt 1 card immediately after split, false if 2nd
            card for 2nd hand is dealt only after 1st hand is finished
        no_bj_no_action_after_split_aces: bool
            True if splitting aces will deal only one card only to each hand with no
            blackjack, False if otherwise. Personally never seen any case where this is
            not True
        insurance : bool, optional
            True if insurance bet is allowed, false otherwise (default is True)
        late_surrender : bool, optional
            True if late surrender is allowed, false otherwise (default is True)
        dealer_shows_hole_card : bool, optional
            True if the dealer shows his hole card regardless of whether or not all
            players bust, surrender, or have natural 21, false otherwise (default is
            False)
        '''
        dealer_peeks_aces, dealer_peeks_tens:
            True if dealer peeks the hidden card when the up card is an ace/ten to check
             for bj. Personally not aware of any irl dealer_peeks_tens
        '''
        """
        if bet_limits is None:
            bet_limits = [0, 1]
        if shoe_size not in [4, 6, 8]:
            raise ValueError("Shoe size must be 4, 6, or 8.")
        if len(bet_limits) != 2:
            raise ValueError("Bet limits should be a list of 2 integers.")
        if not all(isinstance(bet, int) for bet in bet_limits):
            raise TypeError("Bet limits need to be integer values.")
        if bet_limits[0] < 0:
            raise ValueError("Minimum bet at table must be an integer greater than 0.")
        if bet_limits[1] <= bet_limits[0]:
            raise ValueError("Maximum bet at table must be greater than minimum bet.")
        if blackjack_payout <= 1:
            raise ValueError("Blackjack payout must be greater than 1.")
        if max_hands not in [2, 3, 4]:
            raise ValueError("Maximum number of hands must be 2, 3, or 4.")
        if resplit_aces and max_hands == 2:
            raise ValueError(
                "Max hands must be greater than 2 if re-splitting aces is allowed."
            )
        self._shoe_size: int = shoe_size
        self._min_bet: float | int = bet_limits[0]
        self._max_bet: float | int = bet_limits[1]
        self._s17: bool = s17
        self._blackjack_payout: float = blackjack_payout
        self._max_hands: int = max_hands
        self._double_down: bool = double_down
        self._split_unlike_tens: bool = split_unlike_tens
        self._double_after_split: bool = double_after_split
        self._resplit_aces: bool = resplit_aces
        self._immediate_distribute_after_split: bool = immediate_distribute_after_split
        self._no_bj_no_action_after_split_aces: bool = no_bj_no_action_after_split_aces
        self._insurance: bool = insurance
        self._late_surrender: bool = late_surrender
        self._dealer_shows_hole_card: bool = dealer_shows_hole_card
        self._dealer_peeks_aces: bool = dealer_peeks_aces
        self._dealer_peeks_tens: bool = dealer_peeks_tens

    def __str__(self) -> str:
        # pylint: disable=consider-using-f-string
        return (
            "{shoe_size} decks,{s17} {blackjack_payout}{double_after_split}"
            "{resplit_aces}{late_surrender}"
        ).format(
            shoe_size=self._shoe_size,
            s17=" S17," if self._s17 else "H17,",
            blackjack_payout=str(self._blackjack_payout) + "x BJ,",
            double_after_split=" DAS," if self._double_after_split else "",
            resplit_aces=" RSA," if self._resplit_aces else "",
            late_surrender=" LS" if self._late_surrender else "",
        )

    @property
    def shoe_size(self) -> int:
        return self._shoe_size

    @property
    def min_bet(self) -> float | int:
        return self._min_bet

    @property
    def max_bet(self) -> float | int:
        return self._max_bet

    @property
    def s17(self) -> bool:
        return self._s17

    @property
    def blackjack_payout(self) -> float:
        return self._blackjack_payout

    @property
    def max_hands(self) -> int:
        return self._max_hands

    @property
    def double_down(self) -> bool:
        return self._double_down

    @property
    def split_unlike_tens(self) -> bool:
        return self._split_unlike_tens

    @property
    def double_after_split(self) -> bool:
        return self._double_after_split

    @property
    def resplit_aces(self) -> bool:
        return self._resplit_aces

    @property
    def immediate_distribute_after_split(self) -> bool:
        return self._immediate_distribute_after_split

    @property
    def no_bj_no_action_after_split_aces(self) -> bool:
        return self._no_bj_no_action_after_split_aces

    @property
    def insurance(self) -> bool:
        return self._insurance

    @property
    def late_surrender(self) -> bool:
        return self._late_surrender

    @property
    def dealer_shows_hole_card(self) -> bool:
        return self._dealer_shows_hole_card

    @property
    def dealer_peeks_aces(self) -> bool:
        return self._dealer_peeks_aces

    @property
    def dealer_peeks_tens(self) -> bool:
        return self._dealer_peeks_tens
