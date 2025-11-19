# envlog - Project Summary

## Overview

**envlog** is a Python package that brings Rust's RUST_LOG-style environment variable configuration to Python's standard library logging.

- **Author**: Martin Bartlett
- **GitHub/PyPI**: bassmanitram
- **License**: MIT
- **Version**: 0.1.0
- **Python Support**: 3.7+

## Key Features

- **Zero dependencies** - uses only Python standard library
- **Rust-inspired syntax** - familiar to Rust developers
- **Flexible configuration** - single environment variable controls all loggers
- **Standards-based** - builds on `logging.config.dictConfig`
- **Well-tested** - 97% test coverage, 37 tests
- **Type-safe** - includes type hints and py.typed marker

## Installation

```bash
pip install envlog
```

## Quick Start

```python
import logging
import envlog

# Initialize from PTHN_LOG environment variable
envlog.init()

logger = logging.getLogger('myapp')
logger.info('Hello, world!')
```

```bash
export PTHN_LOG=info
python myapp.py
```

## Environment Variable Syntax

```bash
# Default level
PTHN_LOG=info

# Module-specific levels
PTHN_LOG=myapp=debug

# Multiple modules
PTHN_LOG=warn,myapp=debug,otherlib=error

# Hierarchical modules
PTHN_LOG=myapp.core=debug,myapp.db=trace

# Complex configuration
PTHN_LOG=warn,myapp=info,myapp.db=debug,requests=error
```

## Project Structure

```
envlog/
├── envlog/                  # Package source
│   ├── __init__.py         # Package API
│   ├── parser.py           # RUST_LOG syntax parser
│   ├── config.py           # dictConfig builder
│   └── py.typed            # Type checking marker
├── tests/                   # Test suite
│   ├── test_parser.py      # Parser tests
│   ├── test_config.py      # Config builder tests
│   └── test_integration.py # End-to-end tests
├── .github/workflows/       # CI/CD workflows
│   ├── test.yml            # Multi-OS, multi-Python testing
│   ├── lint.yml            # Code quality checks
│   ├── quality.yml         # Security and quality
│   ├── dependencies.yml    # Dependency monitoring
│   ├── docs.yml            # Documentation validation
│   ├── status.yml          # Daily status checks
│   └── release.yml         # PyPI publishing
├── README.md               # User documentation
├── CHANGELOG.md            # Version history
├── pyproject.toml          # Package configuration
├── setup.py                # Build script
├── LICENSE                 # MIT license
├── .gitignore              # Git exclusions
├── .pre-commit-config.yaml # Pre-commit hooks
└── example.py              # Usage example
```

## Test Results

```
37 tests passed
97% code coverage
All linting checks passed (black, isort, mypy)
Package builds successfully
```

## GitHub Actions Workflows

All workflows match the structure from `repl-toolkit`:

1. **test.yml** - Multi-OS (Linux, Windows, macOS), multi-Python (3.7-3.12) testing
2. **lint.yml** - Code formatting and type checking (black, isort, mypy)
3. **quality.yml** - Security scanning (bandit), pre-commit hooks, package validation
4. **dependencies.yml** - Weekly dependency security checks and updates
5. **docs.yml** - Documentation validation on main branch
6. **status.yml** - Daily comprehensive project health checks
7. **release.yml** - Automated PyPI publishing on version tags

## Development Tools

- **Testing**: pytest, pytest-cov
- **Formatting**: black, isort
- **Type checking**: mypy
- **Linting**: flake8
- **Security**: bandit, safety
- **Build**: build, twine
- **Hooks**: pre-commit

## API Reference

### `envlog.init()`
Initialize logging from environment variable or explicit specification.

### `envlog.reset()`
Reset configuration state to allow re-initialization.

### `envlog.parse_log_spec()`
Parse RUST_LOG-style specification (useful for testing/advanced usage).

## Comparison with Rust

| Feature | Rust (RUST_LOG) | Python (envlog) |
|---------|-----------------|-----------------|
| Default level | `RUST_LOG=info` | `PTHN_LOG=info` |
| Module-specific | `module=debug` | Same |
| Module separator | `::` | `.` or `::` |
| Multiple modules | `warn,app=debug` | Same |
| Trace level | Separate | Maps to DEBUG |

## Next Steps

1. **Publishing**:
   ```bash
   # Build the package
   python -m build
   
   # Upload to PyPI
   twine upload dist/*
   ```

2. **GitHub Repository**:
   - Create repo at github.com/bassmanitram/envlog
   - Push code
   - Configure PyPI trusted publishing
   - Create release tags (v0.1.0)

3. **Documentation**:
   - Consider ReadTheDocs setup
   - Add more examples
   - Create comparison with other logging solutions

4. **Enhancements**:
   - Add support for custom handlers (file, syslog, etc.)
   - Add filtering by message content (like Rust regex filters)
   - Add logging output format templates
   - Consider JSON/structured logging support

## Usage Examples

See `example.py` for a complete working example.

```bash
# Run example with different configurations
PTHN_LOG=info python example.py
PTHN_LOG=debug python example.py
PTHN_LOG=warn,myapp=debug python example.py
PTHN_LOG=warn,myapp.database=debug python example.py
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests and linting pass
5. Submit a pull request

## Support

- **Issues**: https://github.com/bassmanitram/envlog/issues
- **Repository**: https://github.com/bassmanitram/envlog
- **PyPI**: https://pypi.org/project/envlog/

## Acknowledgments

Inspired by Rust's `env_logger` crate and the RUST_LOG convention, adapted for Python's logging ecosystem.
