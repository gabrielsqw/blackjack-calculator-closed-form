# Blackjack Calculator

A sophisticated blackjack strategy calculator that uses Markov chain analysis to compute optimal play decisions. This tool calculates dealer outcome probabilities, generates basic strategy charts, and provides real-time action recommendations based on configurable house rules.

## Features

- **Probability Calculation**: Uses Markov chains to compute exact dealer outcome probabilities
- **Card Removal Effects**: Accounts for card composition changes (configurable depth)
- **Strategy Generation**: Automatically generates complete basic strategy charts
- **Expected Value Analysis**: Calculates EV for all possible actions (hit, stand, double, split, surrender)
- **Multiple Rule Sets**: Pre-configured presets for Vegas, Atlantic City, European rules, and more
- **Command-Line Interface**: Interactive mode and batch processing
- **Python Library**: Clean API for integration into other applications

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/blackjack-calculator-closed-form.git
cd blackjack-calculator-closed-form

# Install in development mode
pip install -e .
```

### Requirements

- Python 3.10+
- NumPy >= 1.24.0
- Pandas >= 2.0.0

## Quick Start

### As a Python Library

```python
from blackjack_calculator import BlackjackAnalyzer, HouseRules

# Create analyzer with Vegas Strip rules
analyzer = BlackjackAnalyzer(rules=HouseRules.vegas_strip())
analyzer.compute()

# Get recommendation for a specific hand
recommendation = analyzer.get_recommendation(
    player_cards=[10, 6],  # 16
    dealer_card=10
)
print(recommendation)
# Output: RECOMMENDED: SURRENDER (EV: -0.5000)

# Show complete analysis
analysis = analyzer.analyze_situation([10, 6], dealer_card=10)
print(analysis)

# Generate and print strategy chart
analyzer.print_strategy_chart()
```

### Command-Line Interface

```bash
# Interactive mode
python -m blackjack_calculator.cli.main --interactive --rules vegas_strip

# Get recommendation for specific hand
python -m blackjack_calculator.cli.main --player 10,6 --dealer 10

# Generate complete strategy chart
python -m blackjack_calculator.cli.main --chart all

# Export strategy to CSV
python -m blackjack_calculator.cli.main --chart all --output my_strategy

# Show dealer probabilities
python -m blackjack_calculator.cli.main --dealer-probs
```

## Usage Examples

### Basic Recommendation

```python
from blackjack_calculator import BlackjackAnalyzer, HouseRules

analyzer = BlackjackAnalyzer(rules=HouseRules.vegas_strip())
analyzer.compute()

# Soft 18 vs dealer 9
rec = analyzer.get_recommendation([1, 7], dealer_card=9)
print(rec.recommended_action)  # 'hit'
print(rec.expected_value)       # Expected value
print(rec.all_actions)          # All actions and their EVs
```

### Generate Strategy Chart

```python
# Generate all strategy charts
charts = analyzer.generate_strategy_chart('all')

# Access specific chart
hard_chart = charts['hard']
soft_chart = charts['soft']
pair_chart = charts['pair']

# Print formatted charts
analyzer.print_strategy_chart('all')

# Export to CSV
analyzer.export_strategies('vegas_strip_strategy')
```

### Dealer Probabilities

```python
# Get dealer probabilities for specific up card
probs = analyzer.get_dealer_probabilities(dealer_card=10)
print(probs)
# {'17': 0.125, '18': 0.125, '19': 0.125, '20': 0.358, '21': 0.073, 'Bust': 0.194}

# Print all dealer probabilities
analyzer.print_dealer_probabilities()
```

### Custom House Rules

```python
# Create custom rules
custom_rules = HouseRules(
    shoe_size=6,
    s17=False,              # Dealer hits soft 17
    blackjack_payout=1.5,   # 3:2 blackjack
    double_after_split=True,
    late_surrender=False
)

analyzer = BlackjackAnalyzer(rules=custom_rules, depth=2)
analyzer.compute()
```

### Rule Presets

```python
# Available presets
vegas_strip = HouseRules.vegas_strip()       # 6 decks, S17, 3:2, DAS, LS
vegas_downtown = HouseRules.vegas_downtown() # 6 decks, H17, 3:2, DAS, LS
atlantic_city = HouseRules.atlantic_city()   # 8 decks, S17, 3:2, DAS, RSA, LS
european = HouseRules.european()             # 6 decks, S17, 3:2, DAS, no LS
unfavorable = HouseRules.unfavorable()       # 8 decks, H17, 6:5
```

## How It Works

### Markov Chain Analysis

The calculator uses dynamic programming to build probability matrices for dealer outcomes:

1. **State Space**: Each dealer hand value (2-31) represents a state
2. **Transition Probabilities**: Probability of drawing each card value
3. **Terminal States**: Final outcomes (17-21, Bust)
4. **Backward Induction**: Calculate probabilities from terminal states back to initial states

### Card Removal Effects

The `depth` parameter controls how many cards of removal to consider:

- **Depth 0**: Infinite deck approximation (fastest)
- **Depth 1**: Single card removal effects
- **Depth 2-5**: Multiple card removal (more accurate, slower)

Higher depth provides more accurate probabilities for card counting scenarios.

### Expected Value Calculation

For each action, the calculator computes:

```
EV = Σ P(dealer_outcome) × Payoff(player_outcome, dealer_outcome)
```

The optimal action is the one with the highest expected value.

## CLI Reference

```bash
usage: main.py [-h] [--rules RULES] [--depth {0,1,2,3,4,5}]
               [--interactive] [--player PLAYER] [--dealer DEALER]
               [--chart {all,hard,soft,pair}] [--output OUTPUT]
               [--dealer-probs]

Options:
  --rules, -r           Rule preset (default: vegas_strip)
  --depth, -d           Card counting depth 0-5 (default: 1)
  --interactive, -i     Interactive recommendation mode
  --player, -p          Player cards (e.g., "10,6" or "A,K")
  --dealer, -D          Dealer up card (e.g., "10" or "A")
  --chart, -c           Generate strategy chart (all/hard/soft/pair)
  --output, -o          Output file prefix for CSV export
  --dealer-probs        Show dealer probability tables
```

## Project Structure

```
blackjack-calculator/
├── src/blackjack_calculator/
│   ├── __init__.py           # Public API
│   ├── analyzer.py           # Main BlackjackAnalyzer class
│   ├── core/                 # Core calculation components
│   │   ├── calculator.py     # Markov chain probability calculator
│   │   ├── deck.py           # Deck/shoe management
│   │   ├── hand.py           # Hand representation
│   │   └── house_rules.py    # Rule configuration
│   ├── strategy/             # Strategy components
│   │   ├── basic_strategy.py      # Strategy chart generation
│   │   ├── expected_value.py      # EV calculations
│   │   └── recommendations.py     # Recommendation engine
│   └── cli/                  # Command-line interface
│       └── main.py
├── tests/                    # Test suite
├── examples/                 # Usage examples
├── README.md                 # This file
└── pyproject.toml           # Package configuration
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=blackjack_calculator

# Run specific test file
pytest tests/test_calculator.py
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linter
pylint src/blackjack_calculator

# Format code
black src/

# Type checking
mypy src/
```

## Mathematical Background

This calculator implements the approach described in various blackjack literature, using:

- **Markov Chains** for dealer probability calculation
- **Dynamic Programming** for efficient computation
- **Expected Value Theory** for optimal decision-making

The S17/H17 rule significantly affects dealer probabilities:
- **S17** (Stand on Soft 17): Dealer has ~0.4% lower bust probability
- **H17** (Hit on Soft 17): More aggressive dealer play

## Performance

Typical computation times on modern hardware:

- **Depth 0**: < 0.1 seconds
- **Depth 1**: ~0.5 seconds
- **Depth 2**: ~5 seconds
- **Depth 3**: ~30 seconds
- **Depth 4+**: Minutes (impractical for real-time use)

Depth 1 provides excellent accuracy for most applications.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- Card and deck management inspired by [1andDone/blackjack](https://github.com/1andDone/blackjack)
- Markov chain approach based on academic blackjack analysis literature
- Strategy validation against published basic strategy charts

## Disclaimer

This tool is for educational and research purposes only. Gambling involves risk, and this calculator does not guarantee winning results. Always gamble responsibly and within your means.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation and examples
- Review the API documentation in code docstrings

---

**Version**: 1.0.0
**Author**: Gabriel SQW
**Repository**: https://github.com/gabrielsqw/blackjack-calculator-closed-form
