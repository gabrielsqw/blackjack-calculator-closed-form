"""Tests for BlackjackHandCalculator"""
import numpy as np

from blackjack_calculator.calculator.context import BlackjackContext
from blackjack_calculator.calculator.hand_calculator import BlackjackHandCalculator
from blackjack_calculator.cards.np import NumpyCards
from blackjack_calculator.house_rules import HouseRules


def test_hand_value_calculation():
    """Test basic hand value calculation"""
    rules = HouseRules()
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Test hard 17
    calc = BlackjackHandCalculator([10, 7], 10, deck, context)
    value, is_soft = calc._get_hand_value([10, 7])
    assert value == 17
    assert not is_soft

    # Test soft 17
    calc = BlackjackHandCalculator([1, 6], 10, deck, context)
    value, is_soft = calc._get_hand_value([1, 6])
    assert value == 17
    assert is_soft

    # Test blackjack
    calc = BlackjackHandCalculator([1, 10], 10, deck, context)
    value, is_soft = calc._get_hand_value([1, 10])
    assert value == 21
    assert is_soft

    # Test hard hand with ace
    calc = BlackjackHandCalculator([1, 5, 10], 10, deck, context)
    value, is_soft = calc._get_hand_value([1, 5, 10])
    assert value == 16
    assert not is_soft


def test_compute_stand_basic():
    """Test standing EV calculation"""
    rules = HouseRules()
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Test standing on 20 (should be positive EV)
    calc = BlackjackHandCalculator([10, 10], 5, deck, context)
    ev_stand = calc.compute_stand()
    assert ev_stand > 0, "Standing on 20 vs 5 should have positive EV"

    # Test standing on busted hand
    calc = BlackjackHandCalculator([10, 10, 5], 5, deck, context)
    ev_stand = calc.compute_stand()
    assert ev_stand == -1.0, "Busted hand should have -1 EV"

    # Test standing on 17 (should be slightly negative vs dealer 10)
    calc = BlackjackHandCalculator([10, 7], 10, deck, context)
    ev_stand = calc.compute_stand()
    assert ev_stand < 0, "Standing on 17 vs 10 should have negative EV"


def test_compute_stand_dealer_outcomes():
    """Test that standing correctly compares to dealer outcomes"""
    rules = HouseRules()
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Standing on 21 should beat everything except dealer 21
    calc = BlackjackHandCalculator([10, 10, 1], 5, deck, context)
    ev_stand = calc.compute_stand()
    assert ev_stand > 0.5, "21 vs weak dealer should have high positive EV"


def test_compute_hit_vs_stand():
    """Test that hitting makes sense vs standing for certain hands"""
    rules = HouseRules()
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Hitting on 16 vs 10 should be better than standing
    calc = BlackjackHandCalculator([10, 6], 10, deck, context)
    ev_stand = calc.compute_stand()
    ev_hit = calc.compute_hit()
    assert ev_hit > ev_stand, "Should hit 16 vs 10"

    # Standing on 20 should be better than hitting
    calc = BlackjackHandCalculator([10, 10], 10, deck, context)
    ev_stand = calc.compute_stand()
    ev_hit = calc.compute_hit()
    assert ev_stand > ev_hit, "Should stand on 20"


def test_compute_double():
    """Test doubling down calculation"""
    rules = HouseRules()
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Test doubling on 11 vs 6 (classic double situation)
    calc = BlackjackHandCalculator([5, 6], 6, deck, context)
    ev_double = calc.compute_double()
    ev_hit = calc.compute_hit()

    # Doubling on 11 vs 6 should generally be favorable
    assert ev_double > 0, "Doubling 11 vs 6 should have positive EV"


def test_compute_split_pairs():
    """Test splitting pairs"""
    rules = HouseRules()
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Test splitting 8s vs 10 (should be better than hitting 16)
    calc = BlackjackHandCalculator([8, 8], 10, deck, context)
    ev_split = calc.compute_split()
    ev_hit = calc.compute_hit()

    # Splitting 8s should generally be better than hitting 16
    assert ev_split > ev_hit, "Should split 8s vs 10"

    # Test that non-pairs return -inf
    calc = BlackjackHandCalculator([10, 9], 5, deck, context)
    ev_split = calc.compute_split()
    assert ev_split == float('-inf'), "Cannot split non-pairs"


def test_compute_split_aces():
    """Test splitting aces with special rules"""
    rules = HouseRules(no_bj_no_action_after_split_aces=True)
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Test splitting aces
    calc = BlackjackHandCalculator([1, 1], 6, deck, context)
    ev_split = calc.compute_split()
    ev_hit = calc.compute_hit()

    # Splitting aces should generally be very favorable
    assert ev_split > 0, "Splitting aces vs 6 should have positive EV"


def test_context_after_split():
    """Test that context properly tracks splits"""
    rules = HouseRules(max_split_count=2, has_max_split=True)
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # First split should be allowed
    assert context.can_split([8, 8])

    # After one split
    context_after = context.context_after_split()
    assert context_after.split_count == 1
    assert context_after.can_split([8, 8])

    # After two splits (should hit max)
    context_after2 = context_after.context_after_split()
    assert context_after2.split_count == 2
    assert not context_after2.can_split([8, 8])


def test_double_after_split():
    """Test double after split rules"""
    # With DAS allowed
    rules_das = HouseRules(double_after_split=True)
    context_das = BlackjackContext(rules_das, 1)
    assert context_das.can_double([5, 6])

    # Without DAS
    rules_no_das = HouseRules(double_after_split=False)
    context_no_das = BlackjackContext(rules_no_das, 1)
    assert not context_no_das.can_double([5, 6])


def test_basic_strategy_examples():
    """Test some well-known basic strategy decisions"""
    rules = HouseRules()
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Always hit 12 vs 2 or 3
    calc = BlackjackHandCalculator([10, 2], 2, deck, context)
    ev_hit = calc.compute_hit()
    ev_stand = calc.compute_stand()
    assert ev_hit > ev_stand, "Should hit 12 vs 2"

    # Always stand on hard 17 or higher
    calc = BlackjackHandCalculator([10, 7], 10, deck, context)
    ev_hit = calc.compute_hit()
    ev_stand = calc.compute_stand()
    assert ev_stand > ev_hit, "Should stand on hard 17"

    # Double 11 vs anything but Ace
    calc = BlackjackHandCalculator([5, 6], 9, deck, context)
    ev_double = calc.compute_double()
    ev_hit = calc.compute_hit()
    assert ev_double > ev_hit, "Should double 11 vs 9"


if __name__ == "__main__":
    print("Running hand calculator tests...")

    test_hand_value_calculation()
    print("✓ Hand value calculation")

    test_compute_stand_basic()
    print("✓ Basic stand computation")

    test_compute_stand_dealer_outcomes()
    print("✓ Stand vs dealer outcomes")

    test_compute_hit_vs_stand()
    print("✓ Hit vs stand decisions")

    test_compute_double()
    print("✓ Double down computation")

    test_compute_split_pairs()
    print("✓ Split pairs")

    test_compute_split_aces()
    print("✓ Split aces")

    test_context_after_split()
    print("✓ Context after split")

    test_double_after_split()
    print("✓ Double after split rules")

    test_basic_strategy_examples()
    print("✓ Basic strategy examples")

    print("\nAll tests passed! ✓")
