# 🤝 Contributing to T-R Trading System

Thank you for your interest in contributing to the T-R Trading System! This document provides guidelines for contributing to the project.

## 📋 Table of Contents

- [🤝 Contributing to T-R Trading System](#-contributing-to-t-r-trading-system)
  - [📋 Table of Contents](#-table-of-contents)
  - [🎯 How to Contribute](#-how-to-contribute)
  - [📝 Commit Message Guidelines](#-commit-message-guidelines)
  - [🌿 Branch Naming Convention](#-branch-naming-convention)
  - [🔄 Pull Request Process](#-pull-request-process)
  - [🧪 Testing Requirements](#-testing-requirements)
  - [📚 Documentation Standards](#-documentation-standards)
  - [🎨 Code Style Guidelines](#-code-style-guidelines)
  - [🛡️ Security Considerations](#️-security-considerations)
  - [🏗️ Development Setup](#️-development-setup)
  - [📊 Trading System Specific Guidelines](#-trading-system-specific-guidelines)

## 🎯 How to Contribute

### Types of Contributions We Welcome:

1. **🐛 Bug Reports**: Found a bug? Please report it!
2. **✨ Feature Requests**: Have an idea for improvement? We'd love to hear it!
3. **🔧 Code Contributions**: Bug fixes, new features, performance improvements
4. **📚 Documentation**: Improve documentation, add examples, fix typos
5. **🧪 Testing**: Add tests, improve test coverage
6. **📊 Trading Strategies**: Contribute new proven trading strategies

### Getting Started:

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment** (see [Development Setup](#-development-setup))
4. **Create a new branch** for your contribution
5. **Make your changes** following our guidelines
6. **Test your changes** thoroughly
7. **Submit a pull request**

## 📝 Commit Message Guidelines

We use [Conventional Commits](https://conventionalcommits.org/) for our commit messages. This helps us automatically generate changelogs and determine version bumps.

### Format:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types:
- `feat`: A new feature (bumps MINOR version)
- `fix`: A bug fix (bumps PATCH version)
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools
- `ci`: Changes to our CI configuration files and scripts

### Scopes (for Trading System):
- `strategy`: Trading strategies (VWAP, Momentum, etc.)
- `risk`: Risk management and position sizing
- `execution`: Order execution and broker interface
- `backtest`: Backtesting engine and performance analysis
- `data`: Data processing and market data handling
- `config`: Configuration management
- `dashboard`: UI and visualization
- `monitoring`: Alerts and logging

### Examples:
```bash
feat(strategy): add bollinger bands mean reversion strategy
fix(execution): resolve order timeout issue with IB Gateway
docs(readme): update installation instructions
refactor(risk): extract position sizing logic into separate module
perf(backtest): optimize performance calculation for large datasets
test(strategy): add unit tests for VWAP strategy edge cases
```

### Breaking Changes:
For breaking changes, add `!` after the type/scope:
```bash
feat(strategy)!: change strategy interface to support multi-timeframe

BREAKING CHANGE: Strategy.generate_signal() now requires timeframe parameter
```

## 🌿 Branch Naming Convention

Use descriptive branch names that reflect the type of work:

### Format:
```
<type>/<short-description>
```

### Examples:
```bash
feat/bollinger-bands-strategy
fix/order-timeout-issue
docs/api-documentation
refactor/risk-management-module
test/strategy-unit-tests
chore/update-dependencies
```

## 🔄 Pull Request Process

### Before Submitting:

1. **🔍 Self-review your code**
2. **🧪 Run all tests** and ensure they pass
3. **📝 Update documentation** if needed
4. **🔒 Remove any sensitive data** (API keys, credentials)
5. **📊 Test with paper trading** for trading-related changes

### PR Requirements:

1. **📋 Use the PR template** provided
2. **📝 Provide clear description** of changes
3. **🔗 Link related issues** using keywords (Closes #123, Fixes #456)
4. **🧪 Include test results** or testing strategy
5. **📸 Add screenshots** for UI changes
6. **⚠️ Document breaking changes** clearly

### Review Process:

1. **✅ Automated checks** must pass (CI/CD, tests, linting)
2. **👥 Code review** by maintainers
3. **🛡️ Security review** for trading logic changes
4. **📊 Risk assessment** for changes affecting trading strategies
5. **✅ Final approval** and merge

## 🧪 Testing Requirements

### Test Coverage:
- **Minimum 80% code coverage** for new code
- **100% coverage required** for critical trading logic
- **Integration tests** for broker interface changes
- **Backtesting validation** for new strategies

### Test Types:

#### Unit Tests:
```python
def test_vwap_calculation():
    """Test VWAP calculation with known data."""
    # Test implementation
    pass

def test_risk_limits():
    """Test risk management limits enforcement."""
    # Test implementation
    pass
```

#### Integration Tests:
```python
def test_broker_connection():
    """Test connection to broker interface."""
    # Test implementation
    pass

def test_strategy_execution():
    """Test full strategy execution pipeline."""
    # Test implementation
    pass
```

#### Backtesting Tests:
```python
def test_strategy_backtest():
    """Validate strategy performance on historical data."""
    # Test implementation
    pass
```

### Running Tests:
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=trading_system

# Run specific test file
python -m pytest tests/test_strategies.py

# Run integration tests
python -m pytest tests/integration/
```

## 📚 Documentation Standards

### Code Documentation:

#### Function Documentation:
```python
def calculate_position_size(
    capital: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calculate position size based on risk management rules.
    
    Args:
        capital: Available trading capital
        risk_per_trade: Maximum risk per trade (0.0-1.0)
        entry_price: Entry price for the position
        stop_loss: Stop loss price
        
    Returns:
        Position size in number of shares
        
    Raises:
        ValueError: If risk_per_trade is not between 0 and 1
        
    Example:
        >>> calculate_position_size(10000, 0.02, 100, 95)
        40.0
    """
```

#### Class Documentation:
```python
class TradingStrategy:
    """
    Base class for all trading strategies.
    
    This class provides the interface that all trading strategies must implement.
    It includes common functionality for signal generation, risk management,
    and performance tracking.
    
    Attributes:
        name: Human-readable name of the strategy
        config: Strategy configuration parameters
        enabled: Whether the strategy is currently active
        
    Example:
        >>> strategy = VWAPStrategy(config={'deviation': 0.002})
        >>> signal = strategy.generate_signal(market_data)
    """
```

### README Updates:
- **Update README.md** for new features
- **Add examples** for new functionality
- **Update installation instructions** if needed
- **Document configuration changes**

## 🎨 Code Style Guidelines

### Python Style:
- **Follow PEP 8** guidelines
- **Use Black** for code formatting
- **Use isort** for import organization
- **Use type hints** for all functions
- **Maximum line length**: 88 characters (Black default)

### Formatting Tools:
```bash
# Format code
black .

# Sort imports
isort .

# Check style
flake8 .

# Type checking
mypy trading_system/
```

### Code Structure:
```python
"""Module docstring."""

import os
import sys
from typing import Dict, List, Optional

import pandas as pd
import numpy as np

from trading_system.base import BaseStrategy


class ExampleStrategy(BaseStrategy):
    """Strategy implementation."""
    
    def __init__(self, config: Dict) -> None:
        """Initialize strategy."""
        super().__init__(config)
        self._cached_data: Optional[pd.DataFrame] = None
        
    def generate_signal(self, data: pd.DataFrame) -> Dict:
        """Generate trading signal."""
        # Implementation
        pass
```

### Naming Conventions:
- **Classes**: PascalCase (`TradingStrategy`)
- **Functions/Variables**: snake_case (`calculate_returns`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_POSITION_SIZE`)
- **Private attributes**: Leading underscore (`_internal_data`)

## 🛡️ Security Considerations

### Critical Security Rules:

1. **🔐 Never commit credentials**
   - API keys, passwords, tokens
   - Use environment variables or config files (gitignored)

2. **💰 Financial data protection**
   - No real account credentials in code
   - Use paper trading for development

3. **🔒 Input validation**
   - Validate all external inputs
   - Sanitize configuration data

4. **📊 Trading logic security**
   - Extensive testing for money-handling code
   - Risk limits enforcement
   - Position size validation

### Example Security Implementation:
```python
def validate_trade_parameters(symbol: str, quantity: int, price: float) -> bool:
    """Validate trade parameters for security."""
    if not isinstance(symbol, str) or len(symbol) < 1:
        raise ValueError("Invalid symbol")
    
    if quantity <= 0 or quantity > MAX_QUANTITY:
        raise ValueError("Invalid quantity")
        
    if price <= 0 or price > MAX_PRICE:
        raise ValueError("Invalid price")
        
    return True
```

## 🏗️ Development Setup

### Prerequisites:
- Python 3.11+
- Git
- Interactive Brokers account (for testing)

### Setup Steps:

1. **Clone and setup**:
   ```bash
   git clone https://github.com/shkomig/T-R.git
   cd T-R
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   cd Trading_System
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Setup pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Configure environment**:
   ```bash
   cp config/trading_config.yaml.example config/trading_config.yaml
   cp config/risk_management.yaml.example config/risk_management.yaml
   # Edit configurations as needed
   ```

5. **Run tests**:
   ```bash
   python -m pytest
   ```

### Development Tools:
- **VS Code**: Recommended IDE with Python extension
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing framework

## 📊 Trading System Specific Guidelines

### Strategy Development:

1. **Inherit from BaseStrategy**:
   ```python
   class NewStrategy(BaseStrategy):
       def generate_signal(self, data: pd.DataFrame) -> TradingSignal:
           # Implementation
           pass
   ```

2. **Include comprehensive backtesting**:
   ```python
   def test_strategy_backtest():
       strategy = NewStrategy(config)
       results = backtest_engine.run(strategy, historical_data)
       assert results.sharpe_ratio > 1.0
   ```

3. **Document strategy logic**:
   - Mathematical formulation
   - Entry/exit conditions
   - Risk management rules
   - Expected market conditions

### Risk Management:

1. **Always include position sizing**
2. **Implement stop-loss logic**
3. **Validate portfolio limits**
4. **Test edge cases thoroughly**

### Performance Considerations:

1. **Optimize for real-time execution**
2. **Minimize API calls**
3. **Cache expensive calculations**
4. **Profile performance-critical code**

### Data Handling:

1. **Validate data quality**
2. **Handle missing data gracefully**
3. **Implement data freshness checks**
4. **Use appropriate data structures**

---

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## 📞 Getting Help

- **💬 Discussions**: Use GitHub Discussions for questions
- **🐛 Issues**: Create an issue for bugs or feature requests
- **📧 Direct Contact**: Reach out to maintainers for sensitive issues

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Annual contributor highlights

---

**Thank you for contributing to the T-R Trading System! Your efforts help make algorithmic trading more accessible and robust. 🚀**