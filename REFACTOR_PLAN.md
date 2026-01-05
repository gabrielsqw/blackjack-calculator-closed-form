# Blackjack Calculator - Production Refactor Plan

## Executive Summary
This repository contains blackjack probability calculation code that is not production-ready. The codebase has dead code, poor structure, missing documentation, and lacks a cohesive user interface. This plan outlines a complete overhaul to create a production-ready blackjack strategy calculator.

---

## Current State Analysis

### Existing Files
1. **main.py** ❌ - PyCharm template file, completely unused
2. **BJCalculator.py** ⚠️ - Core logic with issues (debug prints, commented code, poor documentation)
3. **cards.py** ✅ - Functional but needs cleanup
4. **house_rules.py** ✅ - Well-structured, needs minor improvements
5. **requirements.txt** ⚠️ - Incomplete, no version pinning
6. **.github/workflows/pylint.yml** ⚠️ - Linting but dependencies not installed

### Critical Issues
- No README or project documentation
- No proper package structure
- No entry point or user interface
- Components don't work together as a cohesive tool
- No tests
- Debug code and print statements in production files
- Commented-out code blocks
- Missing installation/setup configuration

---

## Proposed Production Structure

```
blackjack-calculator/
├── README.md                          # Project documentation
├── LICENSE                            # Open source license
├── setup.py or pyproject.toml         # Package installation config
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Development dependencies
├── .gitignore                         # Already exists, update if needed
├── .github/
│   └── workflows/
│       ├── pylint.yml                 # Update to install dependencies
│       └── tests.yml                  # Add test workflow
├── src/
│   └── blackjack_calculator/
│       ├── __init__.py                # Package init
│       ├── core/
│       │   ├── __init__.py
│       │   ├── calculator.py          # Refactored BJCalculator
│       │   ├── house_rules.py         # Cleaned up version
│       │   └── deck.py                # Refactored cards.py
│       ├── strategy/
│       │   ├── __init__.py
│       │   ├── basic_strategy.py      # Basic strategy generator
│       │   ├── expected_value.py      # EV calculations
│       │   └── recommendations.py     # Action recommendations
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py                # CLI interface
│       └── utils/
│           ├── __init__.py
│           └── validators.py          # Input validation
├── tests/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_deck.py
│   ├── test_house_rules.py
│   └── test_strategy.py
└── examples/
    ├── basic_usage.py
    └── custom_rules.py
```

---

## Refactoring Tasks

### Phase 1: Cleanup & Organization

#### Task 1.1: Remove Dead Code
- [ ] **Delete main.py** - Completely unused PyCharm template
- [ ] **Clean BJCalculator.py**:
  - Remove commented code blocks (lines 49-59, 96-109, 150-158)
  - Remove debug print statements (lines 211, 225)
  - Remove test code from `if __name__ == "__main__"` block

#### Task 1.2: Create Proper Package Structure
- [ ] Create `src/blackjack_calculator/` directory structure
- [ ] Add `__init__.py` files to all packages
- [ ] Move and rename files:
  - `BJCalculator.py` → `src/blackjack_calculator/core/calculator.py`
  - `cards.py` → `src/blackjack_calculator/core/deck.py`
  - `house_rules.py` → `src/blackjack_calculator/core/house_rules.py`

#### Task 1.3: Update Imports
- [ ] Update all import statements to use new package structure
- [ ] Ensure relative imports work correctly
- [ ] Test imports don't break

---

### Phase 2: Code Quality Improvements

#### Task 2.1: Refactor BJCalculator/Calculator
- [ ] **Improve class design**:
  - Rename class to `ProbabilityCalculator` for clarity
  - Remove class-level mutable defaults (`master = {}`, `hard = None`, etc.)
  - Initialize all state in `__init__`
- [ ] **Add comprehensive docstrings**:
  - Class-level docstring explaining purpose
  - Method docstrings with parameters, returns, examples
  - Explain the Markov chain approach
- [ ] **Improve method names**:
  - `generate_probabilites` → `calculate_probabilities` (fix typo)
  - `generate_probabilites_all` → `calculate_all_probabilities`
  - `model_run` → `run_calculation` or `compute`
- [ ] **Remove magic numbers**: Extract constants (e.g., 17, 21, ranges)
- [ ] **Type hints**: Add type annotations to all methods
- [ ] **Error handling**: Add proper exception handling and validation

#### Task 2.2: Refactor Deck Class
- [ ] Rename `Cards` → `Deck` for clarity
- [ ] Add docstrings to all methods
- [ ] Add type hints
- [ ] Consider if shuffle/deal methods are needed for probability calculation
- [ ] Clean up the card representation (1-13 vs 1-10)

#### Task 2.3: Improve HouseRules
- [ ] Add docstrings where missing
- [ ] Add type hints
- [ ] Consider adding validation for rule combinations
- [ ] Add factory methods for common rule sets (e.g., `HouseRules.vegas_strip()`)

---

### Phase 3: Fill Logic Gaps

#### Task 3.1: Create Strategy Module
**Problem**: Calculator computes dealer probabilities but doesn't tell users what to do.

- [ ] **Create `strategy/basic_strategy.py`**:
  - Generate basic strategy tables based on house rules
  - Map (player_hand, dealer_card) → action (hit/stand/double/split)
  - Account for soft vs hard hands
  - Account for pairs

- [ ] **Create `strategy/expected_value.py`**:
  - Calculate EV for each action (hit, stand, double, split, surrender)
  - Use dealer probabilities from calculator
  - Return optimal action based on maximum EV

- [ ] **Create `strategy/recommendations.py`**:
  - Unified interface: input game state, output recommendation
  - Include EV for all available actions
  - Provide explanation of recommendation

#### Task 3.2: Create Integration Layer
**Problem**: Components exist in isolation, no unified workflow.

- [ ] **Create `BlackjackAnalyzer` class** (in `__init__.py`):
  ```python
  class BlackjackAnalyzer:
      def __init__(self, rules: HouseRules):
          self.rules = rules
          self.calculator = ProbabilityCalculator(rules=rules, ...)
          self.strategy = StrategyEngine(calculator=self.calculator)

      def get_recommendation(self, player_cards, dealer_card, **kwargs):
          """Main entry point for users"""
          pass

      def generate_strategy_chart(self):
          """Generate complete basic strategy table"""
          pass

      def analyze_situation(self, ...):
          """Detailed analysis with probabilities and EVs"""
          pass
  ```

#### Task 3.3: Add Player Hand Logic
**Current Gap**: No proper representation of player hands (pairs, soft/hard, splits)

- [ ] Create `Hand` class:
  - Track cards, total value, soft/hard status
  - Identify pairs, blackjack, bust
  - Calculate valid actions based on rules

---

### Phase 4: User Interface

#### Task 4.1: Command Line Interface
- [ ] **Create `src/blackjack_calculator/cli/main.py`**:
  - Interactive mode: prompt for game state, show recommendation
  - Batch mode: generate full strategy chart
  - Options: choose house rules, output format
  - Use `argparse` or `click` for argument parsing

#### Task 4.2: API/Library Interface
- [ ] **Design clean public API** in `__init__.py`:
  ```python
  from blackjack_calculator import BlackjackAnalyzer, HouseRules

  analyzer = BlackjackAnalyzer(rules=HouseRules.vegas_strip())
  recommendation = analyzer.get_recommendation(
      player_cards=[10, 6],
      dealer_card=10
  )
  ```

---

### Phase 5: Documentation & Infrastructure

#### Task 5.1: Create Documentation
- [ ] **README.md**:
  - Project description and purpose
  - Installation instructions
  - Quick start guide with examples
  - CLI usage
  - Library usage
  - Background on methodology (Markov chains)
  - Contributing guidelines

- [ ] **API Documentation**:
  - Docstrings in code (from Phase 2)
  - Consider Sphinx for generated docs

- [ ] **Examples**:
  - `examples/basic_usage.py` - Simple recommendation
  - `examples/custom_rules.py` - Custom house rules
  - `examples/strategy_chart.py` - Generate full chart

#### Task 5.2: Package Configuration
- [ ] **Create `pyproject.toml`** (modern approach):
  ```toml
  [build-system]
  requires = ["setuptools>=45", "wheel"]
  build-backend = "setuptools.build_meta"

  [project]
  name = "blackjack-calculator"
  version = "1.0.0"
  description = "Optimal blackjack strategy calculator using Markov chains"
  dependencies = ["numpy>=1.24.0", "pandas>=2.0.0"]

  [project.scripts]
  blackjack-calc = "blackjack_calculator.cli.main:main"
  ```

- [ ] **Update requirements.txt**:
  - Pin versions: `numpy>=1.24.0,<2.0.0`
  - Pin versions: `pandas>=2.0.0,<3.0.0`

- [ ] **Create requirements-dev.txt**:
  ```
  pytest>=7.4.0
  pylint>=3.0.0
  black>=23.0.0
  mypy>=1.5.0
  ```

#### Task 5.3: Testing Infrastructure
- [ ] **Create test files**:
  - `tests/test_calculator.py` - Test probability calculations
  - `tests/test_deck.py` - Test deck operations
  - `tests/test_house_rules.py` - Test rule validation
  - `tests/test_strategy.py` - Test strategy generation

- [ ] **Add pytest configuration** in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  python_files = "test_*.py"
  ```

- [ ] **Create `.github/workflows/tests.yml`**:
  - Run pytest on push/PR
  - Test multiple Python versions
  - Generate coverage report

#### Task 5.4: Update CI/CD
- [ ] **Update `pylint.yml`**:
  - Install project dependencies before linting
  - Add `pip install -e .[dev]` or similar

- [ ] **Add code formatting**:
  - Consider Black for formatting
  - Add to CI to check formatting

---

### Phase 6: Final Polish

#### Task 6.1: Code Review Checklist
- [ ] No debug print statements
- [ ] No commented-out code
- [ ] All functions have docstrings
- [ ] All public functions have type hints
- [ ] No hardcoded magic numbers
- [ ] Consistent naming conventions (snake_case)
- [ ] Error messages are clear and helpful

#### Task 6.2: Performance Review
- [ ] Profile calculator for large depths
- [ ] Consider caching for repeated calculations
- [ ] Optimize hot paths if needed

#### Task 6.3: Validation
- [ ] Compare results against known basic strategy tables
- [ ] Verify probabilities sum to 1.0
- [ ] Test edge cases (empty deck, extreme rules)
- [ ] Validate with different house rules

---

## Implementation Order

1. **Phase 1** (Cleanup) - Remove technical debt
2. **Phase 2** (Quality) - Make existing code production-ready
3. **Phase 3** (Logic) - Fill functional gaps
4. **Phase 4** (Interface) - Make it usable
5. **Phase 5** (Infrastructure) - Make it maintainable
6. **Phase 6** (Polish) - Make it excellent

---

## Success Criteria

A successful refactor will have:

✅ **Clean codebase**: No dead code, debug statements, or commented blocks
✅ **Clear structure**: Proper package layout with logical organization
✅ **Complete functionality**: All components work together seamlessly
✅ **User-friendly**: CLI and library interfaces for easy use
✅ **Well-documented**: README, docstrings, examples
✅ **Tested**: Comprehensive test coverage
✅ **Installable**: Can be installed via pip
✅ **Maintainable**: CI/CD, linting, typing, formatting

---

## Estimated Effort

- **Phase 1**: 2-3 hours
- **Phase 2**: 4-6 hours
- **Phase 3**: 6-8 hours (most complex)
- **Phase 4**: 3-4 hours
- **Phase 5**: 4-5 hours
- **Phase 6**: 2-3 hours

**Total**: ~20-30 hours of focused development

---

## Next Steps

1. Review and approve this plan
2. Create a feature branch for the refactor
3. Execute phases sequentially
4. Test thoroughly after each phase
5. Merge when all success criteria are met
