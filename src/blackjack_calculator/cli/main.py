"""Command-line interface for blackjack calculator."""

import argparse
import sys
from typing import List, Optional
from ..core.house_rules import HouseRules
from ..analyzer import BlackjackAnalyzer


def parse_cards(cards_str: str) -> List[int]:
    """
    Parse card string into list of card values.

    Args:
        cards_str: Comma-separated cards (e.g., "10,6" or "A,5" or "K,K")

    Returns:
        List of card values (1-13)

    Raises:
        ValueError: If card format is invalid
    """
    card_mapping = {
        'A': 1, '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13
    }

    cards = []
    for card_str in cards_str.upper().replace(' ', '').split(','):
        if card_str not in card_mapping:
            raise ValueError(f"Invalid card: {card_str}")
        cards.append(card_mapping[card_str])

    return cards


def parse_dealer_card(card_str: str) -> int:
    """
    Parse dealer card string to card value.

    Args:
        card_str: Single card (e.g., "10", "A", "K")

    Returns:
        Card value (1-10)
    """
    cards = parse_cards(card_str)
    if len(cards) != 1:
        raise ValueError("Dealer card must be a single card")

    # Convert face cards to 10
    return min(cards[0], 10)


def get_rules_from_preset(preset: str) -> HouseRules:
    """Get HouseRules from preset name."""
    presets = {
        'vegas_strip': HouseRules.vegas_strip,
        'vegas_downtown': HouseRules.vegas_downtown,
        'atlantic_city': HouseRules.atlantic_city,
        'european': HouseRules.european,
        'unfavorable': HouseRules.unfavorable,
    }

    if preset not in presets:
        raise ValueError(f"Unknown preset: {preset}")

    return presets[preset]()


def interactive_mode(analyzer: BlackjackAnalyzer) -> None:
    """Run interactive recommendation mode."""
    print("\n" + "=" * 70)
    print("BLACKJACK CALCULATOR - Interactive Mode")
    print("=" * 70)
    print("\nEnter card values using: A, 2-10, J, Q, K")
    print("Examples: '10,6' or 'A,5' or 'K,K'")
    print("Type 'quit' or 'exit' to end")
    print("=" * 70 + "\n")

    while True:
        try:
            # Get player cards
            player_input = input("Your cards (comma-separated): ").strip()
            if player_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            player_cards = parse_cards(player_input)

            # Get dealer card
            dealer_input = input("Dealer's up card: ").strip()
            if dealer_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            dealer_card = parse_dealer_card(dealer_input)

            # Get recommendation
            print("\n" + "-" * 70)
            analysis = analyzer.analyze_situation(player_cards, dealer_card)
            print(analysis)
            print()

        except ValueError as e:
            print(f"Error: {e}")
            print("Please try again.\n")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Please try again.\n")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Blackjack strategy calculator using Markov chain analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with Vegas Strip rules
  %(prog)s --interactive --rules vegas_strip

  # Get recommendation for specific hand
  %(prog)s --player 10,6 --dealer 10

  # Generate complete strategy chart
  %(prog)s --chart all --output strategy.csv

  # Show dealer probabilities
  %(prog)s --dealer-probs

Available rule presets:
  vegas_strip      - Las Vegas Strip (6 decks, S17, 3:2, DAS, LS)
  vegas_downtown   - Las Vegas Downtown (6 decks, H17, 3:2, DAS, LS)
  atlantic_city    - Atlantic City (8 decks, S17, 3:2, DAS, RSA, LS)
  european         - European (6 decks, S17, 3:2, DAS, no LS)
  unfavorable      - Unfavorable rules (8 decks, H17, 6:5)
        """
    )

    # Rule configuration
    parser.add_argument(
        '--rules', '-r',
        type=str,
        default='vegas_strip',
        help='Rule preset (default: vegas_strip)'
    )

    parser.add_argument(
        '--depth', '-d',
        type=int,
        default=1,
        choices=[0, 1, 2, 3, 4, 5],
        help='Card counting depth (default: 1, higher=slower but more accurate)'
    )

    # Modes of operation
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interactive mode for getting recommendations'
    )

    parser.add_argument(
        '--player', '-p',
        type=str,
        help='Player cards (e.g., "10,6" or "A,K")'
    )

    parser.add_argument(
        '--dealer', '-D',
        type=str,
        help='Dealer up card (e.g., "10" or "A")'
    )

    parser.add_argument(
        '--chart', '-c',
        type=str,
        choices=['all', 'hard', 'soft', 'pair'],
        help='Generate strategy chart'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file prefix for chart export'
    )

    parser.add_argument(
        '--dealer-probs',
        action='store_true',
        help='Show dealer probability table for all up cards'
    )

    args = parser.parse_args()

    try:
        # Create analyzer with specified rules
        print(f"Initializing with rules: {args.rules}")
        rules = get_rules_from_preset(args.rules)
        print(f"  {rules}")

        analyzer = BlackjackAnalyzer(rules=rules, depth=args.depth)
        analyzer.compute()
        print()

        # Execute requested mode
        if args.interactive:
            interactive_mode(analyzer)

        elif args.player and args.dealer:
            # Single hand analysis
            player_cards = parse_cards(args.player)
            dealer_card = parse_dealer_card(args.dealer)

            analysis = analyzer.analyze_situation(player_cards, dealer_card)
            print(analysis)

        elif args.chart:
            # Generate strategy chart
            analyzer.print_strategy_chart(args.chart)

            if args.output:
                analyzer.export_strategies(args.output)
                print(f"\nStrategy charts exported with prefix: {args.output}")

        elif args.dealer_probs:
            # Show dealer probabilities
            analyzer.print_dealer_probabilities()

        else:
            # No mode specified, show help
            parser.print_help()
            return 1

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
