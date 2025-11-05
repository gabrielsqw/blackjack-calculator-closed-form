"""Demo script showing the blackjack calculator in action"""

from blackjack_calculator.calculator.calculator import BlackjackCalculator
from blackjack_calculator.house_rules import HouseRules


def main():
    print("=" * 60)
    print("Blackjack Calculator Demo - Expected Values")
    print("=" * 60)
    print()

    # Create calculator with standard house rules
    rules = HouseRules(shoe_size=6, s17=True)
    calc = BlackjackCalculator(house_rules=rules)

    print(f"House Rules: {rules}")
    print()

    # Test some classic blackjack scenarios
    test_hands = [
        ((10, 10), 5, "Strong 20 vs weak dealer"),
        ((10, 6), 10, "Hard 16 vs dealer 10 (worst hand)"),
        ((8, 8), 10, "Pair of 8s vs dealer 10"),
        ((11, 11), 6, "Pair of Aces vs dealer 6"),
        ((5, 6), 6, "11 vs dealer 6 (classic double)"),
        ((1, 6), 10, "Soft 17 vs dealer 10"),
        ((10, 1), 7, "Blackjack! vs dealer 7"),
        ((9, 7), 2, "Hard 16 vs dealer 2"),
        ((10, 2), 3, "Hard 12 vs dealer 3"),
    ]

    print("Testing without deck adjustment (infinite deck approximation):")
    print("-" * 60)

    for player_cards, dealer_card, description in test_hands:
        try:
            ev = calc.calc_specific_hand(
                player_cards, dealer_card, adjust_deck=False
            )
            print(f"{description:40s} | Player: {player_cards[0]:2d},{player_cards[1]:2d} vs {dealer_card:2d} | EV: {ev:7.4f}")
        except Exception as e:
            print(f"{description:40s} | ERROR: {e}")

    print()
    print("=" * 60)
    print()

    print("Testing WITH deck adjustment (cards removed from deck):")
    print("-" * 60)

    for player_cards, dealer_card, description in test_hands[:5]:  # Just first 5
        try:
            ev = calc.calc_specific_hand(
                player_cards, dealer_card, adjust_deck=True
            )
            print(f"{description:40s} | Player: {player_cards[0]:2d},{player_cards[1]:2d} vs {dealer_card:2d} | EV: {ev:7.4f}")
        except Exception as e:
            print(f"{description:40s} | ERROR: {e}")

    print()
    print("=" * 60)
    print("\nNotes:")
    print("- Positive EV means player has advantage")
    print("- Negative EV means house has advantage")
    print("- EV of 0.0 means neutral (push)")
    print("- These EVs assume optimal play for each decision")
    print()


if __name__ == "__main__":
    main()
