# Abstract Pattern Refactoring

## Overview

Successfully refactored `BlackjackHandCalculator` to follow the Abstract Base Class (ABC) pattern, separating interface from implementation.

## Changes Made

### 1. Abstract Base Class: `BlackjackHandCalculator`

**Location:** `blackjack_calculator/calculator/hand_calculator.py`

Converted the class to an ABC with:
- **Abstract methods** (must be implemented by subclasses):
  - `compute_stand()` - Calculate EV for standing
  - `compute_hit()` - Calculate EV for hitting
  - `compute_double()` - Calculate EV for doubling down
  - `compute_split()` - Calculate EV for splitting pairs

- **Concrete helper methods** (shared by all implementations):
  - `_get_hand_value()` - Calculate hand value and softness
  - `_get_dealer_probabilities()` - Get dealer outcome probabilities
  - `compute_ev()` - Calculate best EV across all actions

### 2. Concrete Implementation: `RecursiveBlackjackHandCalculator`

**Location:** `blackjack_calculator/calculator/hand_calculator.py`

Implements all abstract methods with recursive calculation logic:
- Recursively explores all possible card draws
- Chooses optimal actions at each decision point
- Handles deck composition changes
- Respects context (split count, house rules, etc.)

### 3. Updated References

**Files Updated:**
- `blackjack_calculator/calculator/calculator.py` - Uses `RecursiveBlackjackHandCalculator`
- `tests/unit_tests/test_hand_calculator.py` - Tests `RecursiveBlackjackHandCalculator`
- `quick_test.py` - Tests `RecursiveBlackjackHandCalculator`

## Benefits

### 1. **Extensibility**
Easy to add new calculation strategies:
```python
class MemoizedBlackjackHandCalculator(BlackjackHandCalculator):
    """Uses memoization to cache results"""
    def __init__(self, ...):
        super().__init__(...)
        self._cache = {}

    def compute_hit(self) -> float:
        key = (tuple(self.player_cards), self.dealer_card, ...)
        if key in self._cache:
            return self._cache[key]
        # ... compute and cache result

class TabularBlackjackHandCalculator(BlackjackHandCalculator):
    """Pre-computed lookup table approach"""
    # Fast lookups for common scenarios

class NeuralBlackjackHandCalculator(BlackjackHandCalculator):
    """Neural network approximation"""
    # For faster approximate calculations
```

### 2. **Separation of Concerns**
- Interface (abstract class) defines **what** needs to be computed
- Implementation (concrete class) defines **how** to compute it
- Shared logic (helper methods) stays in base class

### 3. **Testability**
- Can test abstract interface separately
- Can test concrete implementations independently
- Can create mock implementations for testing

### 4. **Maintainability**
- Clear contract for what methods must be implemented
- Easy to understand the responsibilities
- Changes to calculation logic don't affect interface

### 5. **Type Safety**
- Type checkers can verify implementations are complete
- IDEs provide better autocomplete and warnings
- Catches missing method implementations at import time

## Test Results

### Quick Test (all passed ✓)
```
Test 1: Hand value calculation             ✓ PASSED
Test 2: Dealer probabilities                ✓ PASSED
Test 3: compute_stand()                     ✓ PASSED
Test 4: compute_stand() on busted hand      ✓ PASSED
Test 5: compute_double()                    ✓ PASSED
Test 6: compute_hit() on 20                 ✓ PASSED
```

### Sample Results
- Standing on 20 vs dealer 5: **EV = 0.6704** (67% advantage)
- Doubling 11 vs 6: **EV = 0.6691** (excellent opportunity)
- Hitting 20 vs 10: **EV = -0.8546** (terrible decision)

All results identical to pre-refactoring, confirming no functional changes.

## Future Enhancements

### Potential New Implementations

1. **CachedBlackjackHandCalculator**
   - Memoization for repeated calculations
   - Useful for generating full strategy tables

2. **ApproximateBlackjackHandCalculator**
   - Fast approximations for real-time use
   - Trade accuracy for speed

3. **ParallelBlackjackHandCalculator**
   - Distribute calculations across multiple cores
   - Useful for exhaustive analysis

4. **HybridBlackjackHandCalculator**
   - Lookup table for common scenarios
   - Recursive calculation for rare cases
   - Best of both worlds

## Architecture Diagram

```
┌─────────────────────────────────────┐
│   BlackjackHandCalculator (ABC)    │
├─────────────────────────────────────┤
│ + __init__(cards, dealer, deck)    │
│ + _get_hand_value()        (helper)│
│ + _get_dealer_probabilities() (helper)│
│ + compute_ev()              (concrete)│
│ - compute_stand()          (abstract)│
│ - compute_hit()            (abstract)│
│ - compute_double()         (abstract)│
│ - compute_split()          (abstract)│
└─────────────────────────────────────┘
                 △
                 │ inherits
                 │
┌─────────────────────────────────────┐
│ RecursiveBlackjackHandCalculator   │
├─────────────────────────────────────┤
│ + compute_stand()     (implements) │
│ + compute_hit()       (implements) │
│ + compute_double()    (implements) │
│ + compute_split()     (implements) │
└─────────────────────────────────────┘
```

## Usage Example

### Before (still works)
```python
from blackjack_calculator.calculator.calculator import BlackjackCalculator

calc = BlackjackCalculator()
ev = calc.calc_specific_hand((10, 6), 10)
```

### After (with explicit implementation)
```python
from blackjack_calculator.calculator.hand_calculator import RecursiveBlackjackHandCalculator
from blackjack_calculator.calculator.context import BlackjackContext
from blackjack_calculator.cards.np import NumpyCards
from blackjack_calculator.house_rules import HouseRules

rules = HouseRules()
deck = NumpyCards.factory_from_house_rules(rules)
context = BlackjackContext(rules, 0)

calc = RecursiveBlackjackHandCalculator([10, 6], 10, deck, context)
ev = calc.compute_ev()
```

## Commit Information

**Branch:** `claude/from-major-refactor-011CUq5zfUxq8JRWkEC6mAVY`
**Commit:** `52441ce`
**Status:** Pushed to remote ✓

## Files Changed

- `blackjack_calculator/calculator/hand_calculator.py` (+112 lines, -59 lines)
- `blackjack_calculator/calculator/calculator.py` (import change)
- `tests/unit_tests/test_hand_calculator.py` (import change)
- `quick_test.py` (import change)

---

*Refactoring completed: 2025-11-05*
