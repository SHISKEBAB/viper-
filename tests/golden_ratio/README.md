# Golden Ratio Pullback Strategy Tests

This directory contains comprehensive test suites for the Golden Ratio Pullback Strategy:

## Test Files

- `test_golden_ratio_strategy.py` - Focused test with ideal conditions
- `test_golden_ratio_comprehensive.py` - Comprehensive test suite covering multiple scenarios
- `test_integration.py` - Integration tests ensuring compatibility with VIPER framework

## Running Tests

```bash
# Run all tests
cd tests/golden_ratio
python test_integration.py && python test_golden_ratio_strategy.py && python test_golden_ratio_comprehensive.py

# Run individual tests
python test_integration.py          # Basic integration and API tests
python test_golden_ratio_strategy.py    # Focused test with perfect setup
python test_golden_ratio_comprehensive.py  # Multiple market scenarios
```

## Expected Results

- **Integration Tests**: Should pass all API and framework compatibility tests
- **Focused Test**: Should find 1-2 high-quality pullback setups
- **Comprehensive Test**: Should find setups in choppy markets, handle edge cases gracefully

All tests should complete without errors and demonstrate the strategy's robustness.