"""
Blackjack Calculator - Optimal strategy calculator using Markov chains.

This package provides tools for calculating optimal blackjack strategy based on
house rules and card composition using Markov chain probability analysis.

Quick Start:
    from blackjack_calculator import BlackjackAnalyzer, HouseRules

    # Create analyzer with Vegas Strip rules
    analyzer = BlackjackAnalyzer(rules=HouseRules.vegas_strip())
    analyzer.compute()

    # Get recommendation for a hand
    rec = analyzer.get_recommendation([10, 6], dealer_card=10)
    print(rec)

    # Generate strategy chart
    analyzer.print_strategy_chart()
"""

__version__ = "1.0.0"

# Core components
from .core.house_rules import HouseRules
from .core.deck import Deck
from .core.hand import Hand, HandType
from .core.calculator import ProbabilityCalculator

# Strategy components
from .strategy.expected_value import ExpectedValueCalculator
from .strategy.basic_strategy import BasicStrategy
from .strategy.recommendations import RecommendationEngine, ActionRecommendation

# Main analyzer interface
from .analyzer import BlackjackAnalyzer

__all__ = [
    # Main interface (most users only need this)
    'BlackjackAnalyzer',

    # Core components
    'HouseRules',
    'Deck',
    'Hand',
    'HandType',
    'ProbabilityCalculator',

    # Strategy components
    'ExpectedValueCalculator',
    'BasicStrategy',
    'RecommendationEngine',
    'ActionRecommendation',
]
