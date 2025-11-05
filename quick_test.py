"""Quick test to verify basic functionality"""

from blackjack_calculator.calculator.context import BlackjackContext
from blackjack_calculator.calculator.hand_calculator import RecursiveBlackjackHandCalculator
from blackjack_calculator.cards.np import NumpyCards
from blackjack_calculator.house_rules import HouseRules


def test_basic_functionality():
    """Test that the basic methods work without errors"""
    print("Testing basic hand calculator functionality...")
    print()

    rules = HouseRules()
    deck = NumpyCards.factory_from_house_rules(rules)
    context = BlackjackContext(rules, 0)

    # Test 1: Hand value calculation
    print("Test 1: Hand value calculation")
    calc = RecursiveBlackjackHandCalculator([10, 7], 10, deck, context)
    value, is_soft = calc._get_hand_value([10, 7])
    print(f"  Hard 17: value={value}, is_soft={is_soft}")
    assert value == 17 and not is_soft, "Failed!"

    calc = RecursiveBlackjackHandCalculator([1, 6], 10, deck, context)
    value, is_soft = calc._get_hand_value([1, 6])
    print(f"  Soft 17: value={value}, is_soft={is_soft}")
    assert value == 17 and is_soft, "Failed!"
    print("  ✓ PASSED\n")

    # Test 2: Dealer probabilities
    print("Test 2: Dealer probabilities")
    calc = RecursiveBlackjackHandCalculator([10, 10], 5, deck, context)
    probs = calc._get_dealer_probabilities()
    total_prob = sum(probs.values())
    print(f"  Dealer up card 5 probabilities:")
    for outcome, prob in probs.items():
        print(f"    {outcome}: {prob:.4f}")
    print(f"  Total probability: {total_prob:.6f}")
    assert abs(total_prob - 1.0) < 0.0001, "Probabilities don't sum to 1!"
    print("  ✓ PASSED\n")

    # Test 3: compute_stand
    print("Test 3: compute_stand()")
    calc = RecursiveBlackjackHandCalculator([10, 10], 5, deck, context)
    ev_stand = calc.compute_stand()
    print(f"  Standing on 20 vs dealer 5: EV = {ev_stand:.4f}")
    assert ev_stand > 0, "20 vs 5 should have positive EV!"
    print("  ✓ PASSED\n")

    # Test 4: compute_stand on bust
    print("Test 4: compute_stand() on busted hand")
    calc = RecursiveBlackjackHandCalculator([10, 10, 5], 5, deck, context)
    ev_stand = calc.compute_stand()
    print(f"  Standing on busted hand: EV = {ev_stand:.4f}")
    assert ev_stand == -1.0, "Busted hand should have -1 EV!"
    print("  ✓ PASSED\n")

    # Test 5: compute_double (simpler, no recursion)
    print("Test 5: compute_double()")
    calc = RecursiveBlackjackHandCalculator([5, 6], 6, deck, context)
    ev_double = calc.compute_double()
    print(f"  Doubling 11 vs 6: EV = {ev_double:.4f}")
    assert ev_double > 0, "Doubling 11 vs 6 should have positive EV!"
    print("  ✓ PASSED\n")

    # Test 6: Check that compute_hit works on a terminal case (20)
    print("Test 6: compute_hit() on 20 (should be negative due to bust risk)")
    calc = RecursiveBlackjackHandCalculator([10, 10], 10, deck, context)
    ev_hit = calc.compute_hit()
    print(f"  Hitting 20 vs 10: EV = {ev_hit:.4f}")
    assert ev_hit < 0, "Hitting 20 should be bad!"
    print("  ✓ PASSED\n")

    print("=" * 60)
    print("All basic tests PASSED! ✓")
    print("=" * 60)


if __name__ == "__main__":
    test_basic_functionality()
