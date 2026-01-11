"""
Basic usage example for blackjack calculator.

This script demonstrates the most common use cases:
- Getting recommendations for specific hands
- Analyzing game situations
- Checking dealer probabilities
"""

import sys
sys.path.insert(0, '../src')

from blackjack_calculator import BlackjackAnalyzer, HouseRules


def main():
    print("=" * 70)
    print("BLACKJACK CALCULATOR - Basic Usage Example")
    print("=" * 70)

    # Initialize analyzer with Vegas Strip rules
    print("\n1. Initializing analyzer with Vegas Strip rules...")
    analyzer = BlackjackAnalyzer(rules=HouseRules.vegas_strip())
    analyzer.compute()

    # Example 1: Classic decision - 16 vs 10
    print("\n" + "=" * 70)
    print("Example 1: Hard 16 vs Dealer 10")
    print("=" * 70)
    rec = analyzer.get_recommendation([10, 6], dealer_card=10)
    print(rec)

    # Example 2: Soft hand decision
    print("\n" + "=" * 70)
    print("Example 2: Soft 18 (A-7) vs Dealer 9")
    print("=" * 70)
    rec = analyzer.get_recommendation([1, 7], dealer_card=9)
    print(rec)

    # Example 3: Pair decision
    print("\n" + "=" * 70)
    print("Example 3: Pair of 8s vs Dealer 10")
    print("=" * 70)
    rec = analyzer.get_recommendation([8, 8], dealer_card=10)
    print(rec)

    # Example 4: Dealer probabilities
    print("\n" + "=" * 70)
    print("Example 4: Dealer Probabilities with 10 showing")
    print("=" * 70)
    probs = analyzer.get_dealer_probabilities(dealer_card=10)
    for outcome, prob in probs.items():
        print(f"  {outcome:>6s}: {prob:6.2%}")

    # Example 5: Full situation analysis
    print("\n" + "=" * 70)
    print("Example 5: Complete Situation Analysis")
    print("=" * 70)
    analysis = analyzer.analyze_situation([10, 2], dealer_card=5)
    print(analysis)


if __name__ == '__main__':
    main()
