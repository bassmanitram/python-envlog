# Agent Bootstrap - envlog Project

**Generated**: 2025-11-22  
**Project**: envlog - Rust RUST_LOG-style environment variable configuration for Python logging  
**Version**: 0.1.0  
**Repository**: https://github.com/bassmanitram/python-envlog

---

## Project Overview

### Purpose
`envlog` is a Python library that provides Rust's `RUST_LOG`-style environment variable configuration for Python's standard library logging. It allows developers to configure logging hierarchies using a simple environment variable syntax (e.g., `PTHN_LOG=warn,myapp=debug`) instead of complex dictConfig or code-based configuration.

### Key Features
- Single environment variable controls all logging
- Familiar Rust `RUST_LOG` syntax
- Zero external dependencies (stdlib only)
- Module-specific log level configuration
- Hierarchical logger support
- Works with loggers created anywhere in codebase

### Target Audience
Python developers familiar with Rust's logging conventions, or anyone wanting simpler logging configuration through environment variables.

---

## Project Structure

```
envlog/
├── envlog/                    # Main package (289 lines)
│   ├── __init__.py           # Public API exports (12 lines)
│   ├── parser.py             # RUST_LOG syntax parser (138 lines)
│   └── config.py             # Logging configuration builder (139 lines)
├── tests/                     # Test suite (316 lines, 37 tests, 97% coverage)
│   ├── test_parser.py        # Parser tests (108 lines)
│   ├── test_config.py        # Config builder tests (129 lines)
│   └── test_integration.py   # End-to-end tests (79 lines)
├── .github/workflows/         # CI/CD workflows (8 workflows)
│   ├── test.yml              # Multi-platform/version testing
│   ├── lint.yml              # Code quality (black, isort, mypy)
│   ├── quality.yml           # Pre-commit, security, build validation
│   ├── examples.yml          # Example code validation
│   ├── docs.yml              # Documentation validation
│   ├── dependencies.yml      # Weekly dependency checks
│   ├── status.yml            # Daily health checks
│   └── release.yml           # PyPI release automation
├── pyproject.toml            # Project metadata and tool config
├── setup.py                  # Build configuration (minimal)
├── example.py                # Usage examples
├── README.md                 # Main documentation
├── GETTING_STARTED.md        # Quick start guide
├── CHANGELOG.md              # Version history
├── LICENSE                   # MIT License
└── .pre-commit-config.yaml   # Pre-commit hooks configuration
```

**Important**: Avoid `.venv/` directory - it's large and contains only virtual environment files.

---

## Core Architecture

### Module Breakdown

#### 1. **`envlog.parser`** (138 lines)
Parses RUST_LOG-style specifications into structured `LogSpec` objects.

**Key Components**:
- `LEVEL_MAP`: Dict mapping Rust level names to Python level names
  - `trace` → `DEBUG` (Rust's trace is more verbose, maps to Python's lowest)
  - `debug` → `DEBUG`
  - `info` → `INFO`
  - `warn`/`warning` → `WARNING`
  - `error` → `ERROR`
  - `critical` → `CRITICAL`
  - `off` → `CRITICAL`

- `LogSpec` class: Dataclass-like object holding:
  - `default_level`: Global log level (default: WARNING)
  - `module_levels`: Dict[str, str] mapping module names to levels

- `normalize_level(level: str) -> str`: Converts level strings to Python level names
- `parse_log_spec(spec: str) -> LogSpec`: Main parser function

**Syntax Supported**:
```
info                              # Default level only
myapp=debug                       # Module-specific level
warn,myapp=debug                  # Default + module override
myapp.submodule=trace             # Hierarchical modules
myapp::core=debug                 # Rust :: separator (converted to .)
warn,myapp=debug,other=error      # Multiple overrides
```

**Validation**:
- Module names must match: `^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$`
- Only one default level allowed
- All level names must be valid

#### 2. **`envlog.config`** (139 lines)
Builds `logging.config.dictConfig` configurations and manages initialization state.

**Key Components**:
- `_configured`: Global flag preventing double-initialization
- `build_dict_config(spec, log_format, date_format) -> Dict`: Generates dictConfig dict
- `init(log_spec, env_var, log_format, date_format, force)`: Main initialization function
- `reset()`: Clears `_configured` flag

**Configuration Structure**:
- Uses `StreamHandler` writing to `sys.stderr`
- Default format: `%(asctime)s [%(levelname)8s] %(name)s: %(message)s`
- Default date format: `%Y-%m-%d %H:%M:%S`
- Sets `disable_existing_loggers: False` (non-destructive)
- Creates module-specific loggers with `propagate: False`

**Initialization Flow**:
1. Check `_configured` flag (skip if set and `force=False`)
2. Read spec from `log_spec` parameter OR environment variable
3. Parse spec string into `LogSpec` object
4. Build dictConfig dictionary
5. Apply via `logging.config.dictConfig()`
6. Set `_configured = True`
7. Log configuration to 'envlog' logger at DEBUG level

#### 3. **`envlog.__init__`** (12 lines)
Public API surface. Exports only:
- `init()` - Initialize logging
- `reset()` - Reset configuration state
- `parse_log_spec()` - Parse spec (for testing/advanced use)

**Version**: 0.1.0

---

## Public API

### `envlog.init()`
```python
def init(
    log_spec: Optional[str] = None,
    env_var: str = 'PTHN_LOG',
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    force: bool = False
) -> None
```

**Purpose**: Initialize Python logging from RUST_LOG-style specification.

**Parameters**:
- `log_spec`: Explicit specification (overrides env_var)
- `env_var`: Environment variable name (default: 'PTHN_LOG')
- `log_format`: Custom log message format
- `date_format`: Custom date format
- `force`: Force reconfiguration if already configured

**Behavior**:
- First call: Configures logging
- Subsequent calls: No-op (unless `force=True`)
- Reads from environment if `log_spec` not provided
- Falls back to 'warning' if no spec found

### `envlog.reset()`
```python
def reset() -> None
```

**Purpose**: Reset configuration state without modifying actual logging config.

**Use Case**: Allow re-calling `init()` without `force=True`.

### `envlog.parse_log_spec()`
```python
def parse_log_spec(spec: str) -> LogSpec
```

**Purpose**: Parse specification string into structured object.

**Use Cases**: Testing, validation, introspection.

---

## Testing

### Test Suite Structure

**37 tests total, 97% coverage (2 uncovered lines)**

#### `tests/test_parser.py` (18 tests)
Tests for `envlog.parser` module:
- `TestNormalizeLevel`: Level name normalization (4 tests)
- `TestParseLogSpec`: Specification parsing (14 tests)
  - Valid syntax variations
  - Error conditions (invalid levels, modules, syntax)
  - Rust-style separators
  - Whitespace handling

#### `tests/test_config.py` (13 tests)
Tests for `envlog.config` module:
- `TestBuildDictConfig`: dictConfig generation (3 tests)
- `TestInit`: Initialization behavior (10 tests)
  - Environment variable reading
  - Explicit spec overrides
  - Custom env var names
  - Double-init prevention
  - Force reconfiguration
  - Reset functionality

#### `tests/test_integration.py` (6 tests)
End-to-end integration tests:
- Full logging pipeline
- Module-specific level application
- Hierarchical logger behavior
- Multiple module configurations

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=envlog --cov-report=term-missing

# Specific test file
pytest tests/test_parser.py

# Specific test
pytest tests/test_parser.py::TestParseLogSpec::test_default_level_only

# Quiet mode
pytest tests/ -q
```

### Coverage Report
Current: 97% (79 statements, 2 missed)
- Missed lines: `parser.py:49, 110` (edge cases in error messages)

---

## Development Workflow

### Setup

```bash
# Clone repository
git clone https://github.com/bassmanitram/python-envlog.git
cd python-envlog

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools

**Black** (code formatting):
```bash
black envlog/ tests/
black --check envlog/ tests/  # Check only
```
- Line length: 100
- Target: Python 3.8+

**isort** (import sorting):
```bash
isort envlog/ tests/
isort --check-only envlog/ tests/  # Check only
```
- Profile: black
- Line length: 100

**mypy** (type checking):
```bash
mypy envlog/
```
- Python version: 3.10
- Strict: No (relaxed for flexibility)
- Ignore missing imports: Yes

**flake8** (linting):
```bash
flake8 envlog/ tests/ --max-line-length=100 --extend-ignore=E203,W503
```

**bandit** (security):
```bash
bandit -r envlog/
```

**pre-commit** (all hooks):
```bash
pre-commit run --all-files
```

### Pre-commit Hooks
Located in `.pre-commit-config.yaml`:
1. trailing-whitespace
2. end-of-file-fixer
3. check-yaml, check-toml, check-json
4. check-added-large-files
5. check-merge-conflict
6. debug-statements
7. check-docstring-first
8. black
9. isort
10. flake8

### Building Package

```bash
# Build distributions
python -m build

# Check package metadata
twine check dist/*

# Install locally
pip install dist/envlog-0.1.0-py3-none-any.whl
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. **test.yml** (Multi-platform testing)
- **Trigger**: Push/PR to main, develop, feature branches
- **Matrix**: 
  - OS: Ubuntu, Windows, macOS
  - Python: 3.8, 3.9, 3.10, 3.11, 3.12
- **Steps**: Install deps, run pytest with coverage
- **Total combinations**: 15 (3 OS × 5 Python versions)

#### 2. **lint.yml** (Code quality)
- **Trigger**: Push/PR to main, develop, feature branches
- **Python**: 3.10 on Ubuntu
- **Steps**: black, isort, mypy, package metadata check

#### 3. **quality.yml** (Comprehensive quality)
- **Trigger**: Push/PR to main, develop, feature branches
- **Steps**: 
  - Pre-commit hooks
  - Bandit security scan (report artifact)
  - Package build validation
  - Installation test

#### 4. **examples.yml** (Example validation)
- **Trigger**: Push/PR to main, develop, feature branches
- **Matrix**: Python 3.8, 3.10, 3.12
- **Tests**:
  - Basic usage: `PTHN_LOG=debug; envlog.init()`
  - Logger configuration: Module-specific levels
- **Important**: Uses `envlog.init()` (NOT `envlog.configure()`)

#### 5. **docs.yml** (Documentation validation)
- **Trigger**: Push to main (paths: README.md, CHANGELOG.md, envlog/**)
- **Steps**:
  - Check required files exist
  - Test README examples
  - Validate documentation links

#### 6. **dependencies.yml** (Dependency management)
- **Trigger**: Weekly (Monday 9am UTC) + manual
- **Steps**:
  - Safety security vulnerability check
  - List outdated dependencies
  - Test with latest dependencies

#### 7. **status.yml** (Daily health check)
- **Trigger**: Daily (8am UTC) + manual
- **Steps**:
  - Full test suite
  - Code quality checks
  - Package health validation
  - Generate status report (artifact)

#### 8. **release.yml** (PyPI publishing)
- **Trigger**: Version tag push (v*)
- **Environment**: release
- **Steps**:
  - Extract version from tag
  - Generate changelog from commits
  - Build package
  - Create GitHub release
  - Publish to PyPI (trusted publishing)
- **Requirements**: Configure PyPI trusted publishing

### Running CI Checks Locally

```bash
# Simulate lint workflow
black --check envlog/ tests/
isort --check-only envlog/ tests/
mypy envlog/
python -m build
twine check dist/*

# Simulate test workflow
pytest tests/ --cov=envlog --cov-report=term-missing

# Simulate quality workflow
pre-commit run --all-files
bandit -r envlog/
pip install dist/*.whl
python -c "import envlog; print('Package installed successfully')"

# Simulate examples workflow
python -c "
import logging
import envlog
import os
os.environ['PTHN_LOG'] = 'debug'
envlog.init()
logger = logging.getLogger('test')
logger.debug('Debug message')
print('✓ Basic usage works')
"
```

---

## Dependencies

### Runtime Dependencies
**None** - Pure stdlib implementation

### Development Dependencies
From `pyproject.toml`:
```toml
test = [
    "pytest>=6.0",
    "pytest-cov>=3.0.0",
]
dev = [
    "black>=22.0.0",
    "isort>=5.0.0",
    "flake8>=4.0.0",
    "mypy>=0.991",
    "build>=0.8.0",
    "twine>=4.0.0",
    "pre-commit>=3.0.0",
    "bandit>=1.7.0",
    "safety>=2.0.0",
]
```

### Python Version Support
- **Minimum**: Python 3.8
- **Tested**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Platforms**: Linux, Windows, macOS

---

## Common Use Cases

### 1. Basic Application Logging
```python
import logging
import envlog

envlog.init()
logger = logging.getLogger(__name__)
logger.info("Application started")
```
```bash
PTHN_LOG=info python app.py
```

### 2. Quiet Third-Party Libraries
```python
import logging
import envlog

envlog.init()  # Reads PTHN_LOG
logger = logging.getLogger("myapp")
logger.debug("My app debug message")
```
```bash
PTHN_LOG=warn,myapp=debug python app.py
```
Only your app's debug messages show; third-party libraries at WARNING.

### 3. Module-Specific Debugging
```python
import logging
import envlog

envlog.init()
core_logger = logging.getLogger("myapp.core")
db_logger = logging.getLogger("myapp.database")
```
```bash
PTHN_LOG=warn,myapp.database=debug python app.py
```
Only database module logs debug messages.

### 4. Production Configuration
```python
envlog.init(log_spec='error')  # Override environment
```
All logs at ERROR level or above, regardless of environment variable.

### 5. Testing with Different Configs
```python
def test_logging_info():
    envlog.reset()
    envlog.init(log_spec='info')
    # Test with info level

def test_logging_debug():
    envlog.reset()
    envlog.init(log_spec='debug')
    # Test with debug level
```

---

## Troubleshooting Guide

### Issue: Nothing is logging
**Cause**: Log level too high or handlers not configured
**Solution**:
```python
import logging
logger = logging.getLogger(__name__)
print(f"Effective level: {logger.getEffectiveLevel()}")  # Check level
envlog.init(log_spec='debug', force=True)  # Force reconfigure
```

### Issue: Too much output from libraries
**Cause**: Default level too low
**Solution**:
```bash
PTHN_LOG=error,myapp=info  # High default, low for your app
```

### Issue: Can't reconfigure logging
**Cause**: `init()` already called without `force=True`
**Solution**:
```python
envlog.reset()      # Option 1: Reset then init
envlog.init(...)

envlog.init(force=True, ...)  # Option 2: Force reconfigure
```

### Issue: Module-specific config not working
**Cause**: Module name mismatch or logger not created
**Solution**:
```python
# Ensure module name matches
import logging
logger = logging.getLogger("myapp.database")  # Exact match required
print(logger.name)  # Verify name
```

### Issue: Tests interfering with each other
**Cause**: Global logging configuration persists
**Solution**:
```python
import pytest
from envlog import reset

@pytest.fixture(autouse=True)
def reset_logging():
    reset()
    yield
    reset()
```

---

## Design Decisions & Rationale

### Why environment variables?
- 12-factor app methodology
- No code changes for different environments
- Familiar to operations/DevOps teams
- Works with containers, CI/CD, systemd

### Why RUST_LOG syntax?
- Proven design from Rust ecosystem
- Concise and readable
- Hierarchical module support
- Balance of simplicity and power

### Why `PTHN_LOG` instead of `RUST_LOG`?
- Avoid confusion with actual Rust applications
- Clear Python-specific identifier
- Follows similar naming pattern

### Why `trace` maps to `DEBUG`?
- Python has no TRACE level in stdlib
- Rust's trace is more verbose than debug
- DEBUG is Python's lowest standard level
- Users wanting trace behavior get Python's most verbose option

### Why default to `WARNING`?
- Python logging default
- Prevents overwhelming output
- Encourages explicit configuration
- Matches stdlib behavior

### Why `disable_existing_loggers: False`?
- Non-destructive configuration
- Works with libraries that configure logging before app startup
- Allows incremental adoption
- Safer default behavior

### Why `force` parameter?
- Prevent accidental double-initialization
- Allow explicit reconfiguration when needed
- Help catch configuration mistakes
- Support testing scenarios

---

## Project Conventions

### Code Style
- Line length: 100 characters
- String quotes: Double quotes preferred by black
- Import order: stdlib → third-party → local (isort)
- Type hints: Encouraged but not required (relaxed mypy)

### Naming Conventions
- Functions/methods: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: Leading underscore `_private`
- Module names: Lowercase, no underscores

### Docstring Format
- Module docstrings: Overview and syntax examples
- Function docstrings: Args, Returns, Raises, Examples
- Class docstrings: Purpose and attributes
- Format: Google style (informal)

### Test Organization
- Test files: `test_<module>.py`
- Test classes: `Test<FunctionOrClass>`
- Test functions: `test_<behavior>`
- Fixtures: Minimal, prefer direct instantiation

### Commit Messages
- Present tense: "Fix bug" not "Fixed bug"
- Lowercase: "fix flake8 args" not "Fix Flake8 Args"
- Concise: < 72 characters preferred
- No issue refs (small project)

### Version Strategy
- Semantic versioning: MAJOR.MINOR.PATCH
- Current: 0.1.0 (Beta)
- Tag format: `v0.1.0`
- CHANGELOG.md updated per release

---

## Files of Note

### Configuration Files
- **`pyproject.toml`**: Single source of truth for project metadata, dependencies, and tool configuration
- **`.pre-commit-config.yaml`**: Pre-commit hook definitions
- **`.gitignore`**: Excludes .venv, dist, build, __pycache__, *.egg-info, coverage reports

### Documentation Files
- **`README.md`**: Comprehensive user documentation with examples
- **`GETTING_STARTED.md`**: Quick start guide for new users
- **`CHANGELOG.md`**: Version history (currently minimal)
- **`.github/README_ACTIONS.md`**: GitHub Actions workflow documentation

### Build Files
- **`setup.py`**: Minimal shim for editable installs (115 lines)
- **`pyproject.toml`**: Modern build configuration (PEP 621)
- **`envlog/py.typed`**: PEP 561 type hint marker (empty file)

### Example Files
- **`example.py`**: Runnable example demonstrating all features (1318 bytes)

---

## Key Insights for Future Development

### Architecture Strengths
1. **Clean separation**: Parser and config builder are independent
2. **Testable**: Pure functions, no I/O in core logic
3. **Extensible**: Easy to add new log levels or syntax
4. **Minimal surface area**: Only 3 public functions

### Potential Extension Points
1. **Custom handlers**: Currently hardcoded to StreamHandler
2. **Config file support**: Could read from JSON/YAML/TOML
3. **Hot reload**: Watch environment for changes
4. **Logging to files**: Currently stderr only
5. **Advanced filtering**: More than just level control
6. **Multiple handlers**: Currently single handler per logger

### Testing Gaps (Future Improvements)
1. Windows path handling (tested via CI but not explicitly)
2. Unicode in module names
3. Very long module hierarchies (10+ levels)
4. Concurrent initialization from multiple threads
5. Integration with logging.basicConfig()

### Known Limitations
1. No log rotation (use external tools)
2. No structured logging (use external formatters)
3. Single handler architecture
4. No runtime reconfiguration without `force=True`
5. Environment variables only (no config files)

### Maintenance Notes
1. **Coverage target**: 95%+ (currently 97%)
2. **Test count**: Keep < 50 (currently 37)
3. **Code size**: Keep < 500 lines (currently 289)
4. **Dependencies**: Maintain zero runtime dependencies
5. **Python support**: Follow NEP 29 (24 months after release)

---

## Quick Reference Commands

```bash
# Development setup
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,test]"
pre-commit install

# Run tests
pytest tests/ -v
pytest tests/ --cov=envlog --cov-report=html

# Code quality
black envlog/ tests/
isort envlog/ tests/
mypy envlog/
flake8 envlog/ tests/ --max-line-length=100 --extend-ignore=E203,W503
bandit -r envlog/
pre-commit run --all-files

# Build and check
python -m build
twine check dist/*
pip install dist/*.whl

# Example usage
PTHN_LOG=debug python example.py
PTHN_LOG=warn,myapp=debug python example.py

# Git workflow
git status
git log --oneline -10
git diff

# Find files (avoid .venv)
find . -name "*.py" | grep -v ".venv" | grep -v "__pycache__"
```

---

## Important Git Information

- **Branch**: main
- **Remote**: origin (https://github.com/bassmanitram/python-envlog.git)
- **Last tag**: v0.1.0
- **Recent commits**:
  - Fix flake8 args
  - fix pre-commit
  - Readme cleanup
  - Fix examples
  - GH Actions homogenization
  - Fix badges and URLs

---

## Contact & Resources

- **Author**: Martin Bartlett (martin.j.bartlett@gmail.com)
- **License**: MIT
- **Repository**: https://github.com/bassmanitram/python-envlog
- **Issues**: https://github.com/bassmanitram/python-envlog/issues
- **PyPI**: https://pypi.org/project/envlog/ (when published)

---

## Summary for AI Agents

This is a **small, focused Python library** (289 lines of code) that provides environment variable-based logging configuration using Rust's RUST_LOG syntax. The codebase is **well-tested** (37 tests, 97% coverage), **well-documented**, and follows **modern Python practices**.

**When working on this project**:
1. Run tests after every change: `pytest tests/`
2. Use pre-commit hooks: `pre-commit run --all-files`
3. Maintain 95%+ coverage
4. Keep code simple and stdlib-only
5. Update documentation for API changes
6. Avoid `.venv/` directory in searches

**Core files to understand**:
- `envlog/parser.py` - Syntax parsing
- `envlog/config.py` - Configuration building
- `tests/` - Comprehensive test coverage

**Architecture**: Parser → Config Builder → stdlib logging.config.dictConfig

This document should provide sufficient context to work on the project in future sessions without needing to re-explore the codebase.
