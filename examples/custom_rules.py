"""
Custom rules example for blackjack calculator.

This script demonstrates how to create and use custom house rules,
including comparing different rule sets.
"""

import sys
sys.path.insert(0, '../src')

from blackjack_calculator import BlackjackAnalyzer, HouseRules


def main():
    print("=" * 70)
    print("BLACKJACK CALCULATOR - Custom Rules Example")
    print("=" * 70)

    # Example 1: Using built-in presets
    print("\n1. Comparing Built-in Rule Presets")
    print("-" * 70)

    presets = {
        'Vegas Strip': HouseRules.vegas_strip(),
        'Vegas Downtown': HouseRules.vegas_downtown(),
        'Atlantic City': HouseRules.atlantic_city(),
        'European': HouseRules.european(),
    }

    test_hand = [10, 6]  # Hard 16
    test_dealer = 10

    print(f"\nTest situation: Player {test_hand} vs Dealer {test_dealer}\n")

    for name, rules in presets.items():
        print(f"{name}:")
        print(f"  Rules: {rules}")
        analyzer = BlackjackAnalyzer(rules=rules, depth=1)
        analyzer.compute()
        rec = analyzer.get_recommendation(test_hand, test_dealer)
        print(f"  Recommendation: {rec.recommended_action.upper()} (EV: {rec.expected_value:+.4f})")
        print()

    # Example 2: Creating custom rules
    print("\n" + "=" * 70)
    print("2. Creating Custom Rules")
    print("-" * 70)

    custom_rules = HouseRules(
        shoe_size=6,
        s17=False,                    # Dealer hits soft 17
        blackjack_payout=1.2,         # 6:5 blackjack (unfavorable)
        double_after_split=False,      # Can't double after split
        late_surrender=False,          # No surrender
        resplit_aces=False
    )

    print(f"\nCustom Rules: {custom_rules}")
    print("\nAnalyzing with custom rules...")

    analyzer = BlackjackAnalyzer(rules=custom_rules, depth=1)
    analyzer.compute()

    # Test several situations
    test_situations = [
        ([10, 6], 10, "Hard 16 vs 10"),
        ([1, 7], 9, "Soft 18 vs 9"),
        ([8, 8], 10, "Pair of 8s vs 10"),
        ([11, 11], 6, "Double down situation"),
    ]

    print("\nRecommendations with custom rules:")
    print("-" * 70)
    for player_cards, dealer_card, description in test_situations:
        rec = analyzer.get_recommendation(player_cards, dealer_card)
        print(f"{description:25s}: {rec.recommended_action.upper():10s} (EV: {rec.expected_value:+.4f})")

    # Example 3: Impact of S17 vs H17
    print("\n" + "=" * 70)
    print("3. Impact of S17 vs H17 Rule")
    print("-" * 70)

    s17_rules = HouseRules(s17=True)
    h17_rules = HouseRules(s17=False)

    print("\nDealer probabilities with Ace showing:\n")

    for rules, name in [(s17_rules, "S17"), (h17_rules, "H17")]:
        analyzer = BlackjackAnalyzer(rules=rules, depth=0)
        analyzer.compute()
        probs = analyzer.get_dealer_probabilities(dealer_card=1)

        print(f"{name} Rules:")
        for outcome, prob in probs.items():
            print(f"  {outcome:>6s}: {prob:6.2%}")
        print()

    # Example 4: Effect of shoe size
    print("\n" + "=" * 70)
    print("4. Effect of Shoe Size")
    print("-" * 70)

    print("\nTesting with different shoe sizes (depth=1 for card removal effects):\n")

    for shoe_size in [4, 6, 8]:
        rules = HouseRules(shoe_size=shoe_size)
        analyzer = BlackjackAnalyzer(rules=rules, depth=1)
        analyzer.compute()
        rec = analyzer.get_recommendation([10, 6], dealer_card=10)
        print(f"{shoe_size} decks: {rec.recommended_action.upper():10s} (EV: {rec.expected_value:+.4f})")


if __name__ == '__main__':
    main()
