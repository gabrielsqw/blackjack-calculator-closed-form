from typing import TypeVar

from blackjack_calculator.calculator.context import BlackjackContext
from blackjack_calculator.cards.abstract import AbstractCards

_T_Cards = TypeVar("_T_Cards", bound=AbstractCards)


class BlackjackHandCalculator:
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

    def _get_hand_value(self, cards: list[int]) -> tuple[int, bool]:
        """
        Calculate hand value and whether it's soft.

        Returns
        -------
        tuple[int, bool]
            (hand_value, is_soft) where is_soft indicates if ace is counted as 11
        """
        total = sum(min(c, 10) for c in cards)
        has_ace = 1 in cards

        if has_ace and total + 10 <= 21:
            return (total + 10, True)  # Soft hand
        return (total, False)  # Hard hand

    def _get_dealer_probabilities(self) -> dict[str, float]:
        """
        Get dealer outcome probabilities for the current dealer up card.

        Returns
        -------
        dict[str, float]
            Dictionary with keys: 'H17', 'H18', 'H19', 'H20', 'H21', 'BUST'
            and their corresponding probabilities
        """
        hard_table, _ = self.deck.construct_table()
        dealer_probs = hard_table[self.dealer_card]
        return {
            'H17': dealer_probs['H17'],
            'H18': dealer_probs['H18'],
            'H19': dealer_probs['H19'],
            'H20': dealer_probs['H20'],
            'H21': dealer_probs['H21'],
            'BUST': dealer_probs['BUST'],
        }

    def compute_stand(self) -> float:
        """
        Calculate expected value if player stands.

        Returns
        -------
        float
            Expected value of standing with current hand
        """
        hand_value, _ = self._get_hand_value(self.player_cards)

        # If player busted, they lose
        if hand_value > 21:
            return -1.0

        # Get dealer outcome probabilities
        dealer_probs = self._get_dealer_probabilities()

        # Calculate EV: win if dealer < player, push if equal, lose if dealer > player
        ev = 0.0

        # Win against dealer bust
        ev += dealer_probs['BUST']

        # Compare against dealer final hands
        dealer_outcomes = [17, 18, 19, 20, 21]
        for outcome in dealer_outcomes:
            prob = dealer_probs[f'H{outcome}']
            if hand_value > outcome:
                ev += prob  # Win
            elif hand_value == outcome:
                ev += 0  # Push (no change)
            else:
                ev -= prob  # Lose

        return ev

    def compute_hit(self) -> float:
        """
        Calculate expected value if player hits.

        Returns
        -------
        float
            Expected value of hitting with current hand
        """
        probabilities = self.deck.probabilities
        ev = 0.0

        # Try drawing each possible card
        for card in range(1, 11):
            prob = probabilities[card]
            if prob <= 0:
                continue

            # Create new hand after drawing card
            new_hand = self.player_cards + [card]
            hand_value, _ = self._get_hand_value(new_hand)

            # If busted, lose
            if hand_value > 21:
                ev += prob * (-1.0)
            else:
                # After hitting, player can choose to hit again or stand
                # Calculate best action
                new_deck = self.deck.draw_card(card)
                new_calculator = BlackjackHandCalculator(
                    new_hand, self.dealer_card, new_deck, self.context
                )

                # Best of standing or hitting again
                ev_stand = new_calculator.compute_stand()
                ev_hit = new_calculator.compute_hit()
                ev += prob * max(ev_stand, ev_hit)

        return ev

    def compute_double(self) -> float:
        """
        Calculate expected value if player doubles down.

        Returns
        -------
        float
            Expected value of doubling (2x bet, one card only, then must stand)
        """
        probabilities = self.deck.probabilities
        ev = 0.0

        # Try drawing each possible card
        for card in range(1, 11):
            prob = probabilities[card]
            if prob <= 0:
                continue

            # Create new hand after drawing card
            new_hand = self.player_cards + [card]
            hand_value, _ = self._get_hand_value(new_hand)

            # After doubling, must stand
            new_deck = self.deck.draw_card(card)
            new_calculator = BlackjackHandCalculator(
                new_hand, self.dealer_card, new_deck, self.context
            )

            # Must stand after double, and bet is 2x
            ev_stand = new_calculator.compute_stand()
            ev += prob * (2.0 * ev_stand)

        return ev

    def compute_split(self) -> float:
        """
        Calculate expected value if player splits.

        Returns
        -------
        float
            Expected value of splitting the pair
        """
        if len(self.player_cards) != 2 or self.player_cards[0] != self.player_cards[1]:
            return float('-inf')  # Can't split non-pairs

        split_card = self.player_cards[0]
        new_context = self.context.context_after_split()

        # Special case: splitting aces (usually restricted)
        if split_card == 1 and self.context.rules.no_bj_no_action_after_split_aces:
            # Each ace gets one card and must stand
            probabilities = self.deck.probabilities
            ev_total = 0.0

            for card1 in range(1, 11):
                prob1 = probabilities[card1]
                if prob1 <= 0:
                    continue

                deck_after_first = self.deck.draw_card(card1)

                for card2 in range(1, 11):
                    prob2 = deck_after_first.probabilities[card2]
                    if prob2 <= 0:
                        continue

                    # Calculate EV for both hands
                    hand1 = [split_card, card1]
                    hand2 = [split_card, card2]

                    deck_after_both = deck_after_first.draw_card(card2)

                    calc1 = BlackjackHandCalculator(
                        hand1, self.dealer_card, deck_after_both, new_context
                    )
                    calc2 = BlackjackHandCalculator(
                        hand2, self.dealer_card, deck_after_both, new_context
                    )

                    ev1 = calc1.compute_stand()
                    ev2 = calc2.compute_stand()

                    ev_total += prob1 * prob2 * (ev1 + ev2)

            return ev_total

        # Regular split: each hand can be played normally
        probabilities = self.deck.probabilities
        ev_total = 0.0

        for card1 in range(1, 11):
            prob1 = probabilities[card1]
            if prob1 <= 0:
                continue

            deck_after_first = self.deck.draw_card(card1)

            for card2 in range(1, 11):
                prob2 = deck_after_first.probabilities[card2]
                if prob2 <= 0:
                    continue

                # Calculate best EV for both hands
                hand1 = [split_card, card1]
                hand2 = [split_card, card2]

                deck_after_both = deck_after_first.draw_card(card2)

                calc1 = BlackjackHandCalculator(
                    hand1, self.dealer_card, deck_after_both, new_context
                )
                calc2 = BlackjackHandCalculator(
                    hand2, self.dealer_card, deck_after_both, new_context
                )

                # Best action for each hand
                ev1 = max(
                    calc1.compute_stand(),
                    calc1.compute_hit(),
                    calc1.compute_double() if new_context.can_double(hand1) else float('-inf'),
                )
                ev2 = max(
                    calc2.compute_stand(),
                    calc2.compute_hit(),
                    calc2.compute_double() if new_context.can_double(hand2) else float('-inf'),
                )

                ev_total += prob1 * prob2 * (ev1 + ev2)

        return ev_total

    def compute_ev(self) -> float:
        """
        Calculate best expected value across all possible actions.

        Returns
        -------
        float
            Best expected value for current hand
        """
        ev_stand = self.compute_stand()
        ev_hit = self.compute_hit()

        actions = [ev_stand, ev_hit]

        if self.context.can_double(self.player_cards):
            actions.append(self.compute_double())

        if self.context.can_split(self.player_cards):
            actions.append(self.compute_split())

        return max(actions)
