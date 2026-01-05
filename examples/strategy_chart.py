"""
Strategy chart generation example.

This script demonstrates how to generate and export complete
basic strategy charts.
"""

import sys
sys.path.insert(0, '../src')

from blackjack_calculator import BlackjackAnalyzer, HouseRules


def main():
    print("=" * 70)
    print("BLACKJACK CALCULATOR - Strategy Chart Generation")
    print("=" * 70)

    # Initialize with Vegas Strip rules
    print("\nGenerating strategy charts for Vegas Strip rules...")
    print("(6 decks, S17, 3:2 blackjack, DAS, LS)")

    analyzer = BlackjackAnalyzer(rules=HouseRules.vegas_strip(), depth=1)
    analyzer.compute()

    # Print all strategy charts
    print("\n")
    analyzer.print_strategy_chart('all')

    # Export to CSV
    print("\n" + "=" * 70)
    print("Exporting to CSV files...")
    print("=" * 70)
    analyzer.export_strategies('vegas_strip_strategy')

    # Compare strategies for different rules
    print("\n" + "=" * 70)
    print("Comparing Hard Hands Strategy Across Rule Sets")
    print("=" * 70)

    print("\nGenerating strategies for comparison...")

    rule_sets = {
        'Vegas Strip (S17)': HouseRules.vegas_strip(),
        'Vegas Downtown (H17)': HouseRules.vegas_downtown(),
        'Unfavorable (H17, 6:5)': HouseRules.unfavorable(),
    }

    # Focus on a few key decisions
    key_hands = [
        (12, "Hard 12"),
        (13, "Hard 13"),
        (16, "Hard 16"),
    ]

    dealer_cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # 11 = Ace

    for hand_value, hand_name in key_hands:
        print(f"\n{hand_name} vs Dealer:")
        print("-" * 70)
        print(f"{'Dealer Up Card:':<20}", end='')
        for dc in dealer_cards:
            card_name = 'A' if dc == 11 else str(dc)
            print(f"{card_name:>4}", end='')
        print()
        print("-" * 70)

        for rule_name, rules in rule_sets.items():
            analyzer = BlackjackAnalyzer(rules=rules, depth=0)
            analyzer.compute()
            charts = analyzer.generate_strategy_chart('hard')
            hard_chart = charts['hard']

            print(f"{rule_name:<20}", end='')
            for dc in dealer_cards:
                if hand_value in hard_chart.index and dc in hard_chart.columns:
                    action = hard_chart.loc[hand_value, dc]
                    print(f"{action:>4}", end='')
                else:
                    print("  - ", end='')
            print()

    print("\n" + "=" * 70)
    print("Legend: H=Hit, S=Stand, D=Double, R=suRrender")
    print("=" * 70)


if __name__ == '__main__':
    main()
