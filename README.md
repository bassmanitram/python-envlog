# envlog

Rust RUST_LOG-style environment variable configuration for Python's standard library logging.

## Features

- **Simple**: One environment variable configures all loggers
- **Familiar**: Uses Rust's RUST_LOG syntax
- **Standard**: Builds on Python's `logging.config.dictConfig`
- **Zero dependencies**: Only uses Python standard library
- **Flexible**: Works with loggers created anywhere in your codebase

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

# Now use logging normally
logger = logging.getLogger('myapp')
logger.info('Hello, world!')
```

```bash
# Set log level via environment
export PTHN_LOG=info
python myapp.py
```

## Syntax

The log specification syntax follows Rust's RUST_LOG conventions:

```bash
# Set default level
PTHN_LOG=info

# Set module-specific levels
PTHN_LOG=myapp=debug

# Set default + module overrides
PTHN_LOG=warn,myapp=debug,otherlib=error

# Hierarchical modules (use . or :: separator)
PTHN_LOG=myapp.core=debug
PTHN_LOG=myapp::db=trace

# Complex example
PTHN_LOG=warn,myapp=info,myapp.db=debug,requests=error
```

### Log Levels

Supports all standard levels (case-insensitive):

- `trace` → Python's `DEBUG` (Rust's trace is more verbose, maps to Python's lowest)
- `debug` → `DEBUG`
- `info` → `INFO`
- `warn` / `warning` → `WARNING`
- `error` → `ERROR`
- `critical` → `CRITICAL`

## Usage Examples

### Basic Usage

```python
import envlog

# Read from PTHN_LOG environment variable
envlog.init()

# Or specify configuration directly
envlog.init(log_spec='warn,myapp=debug')

# Or use custom environment variable name
envlog.init(env_var='MY_LOG')
```

### Module-Specific Configuration

```python
import logging
import envlog

envlog.init(log_spec='warn,myapp.core=debug,myapp.db=trace')

# Different modules get different log levels
core_logger = logging.getLogger('myapp.core')
core_logger.debug('Detailed debugging')  # Shows (DEBUG level)

db_logger = logging.getLogger('myapp.db')
db_logger.debug('Database query')  # Shows (TRACE->DEBUG level)

other_logger = logging.getLogger('requests')
other_logger.info('HTTP request')  # Hidden (WARN level)
```

### Custom Formatting

```python
envlog.init(
    log_spec='debug',
    log_format='%(levelname)s %(name)s: %(message)s',
    date_format='%H:%M:%S'
)
```

### Force Reconfiguration

```python
# First configuration
envlog.init(log_spec='info')

# Later, reconfigure (requires force=True)
envlog.init(log_spec='debug', force=True)

# Or use reset() then init()
envlog.reset()
envlog.init(log_spec='debug')
```

## API Reference

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

Initialize logging from a RUST_LOG-style specification.

**Parameters:**
- `log_spec`: Explicit log specification (overrides env_var if provided)
- `env_var`: Environment variable name to read (default: 'PTHN_LOG')
- `log_format`: Custom log message format
- `date_format`: Custom date format
- `force`: Force reconfiguration even if already configured

### `envlog.reset()`

```python
def reset() -> None
```

Reset the configuration state, allowing `init()` to be called again without `force=True`.

### `envlog.parse_log_spec()`

```python
def parse_log_spec(spec: str) -> LogSpec
```

Parse a RUST_LOG-style specification into a `LogSpec` object. Useful for testing or advanced usage.

## Comparison with RUST_LOG

| Feature | Rust RUST_LOG | envlog |
|---------|---------------|--------|
| Default level | `RUST_LOG=info` | `PTHN_LOG=info` |
| Module-specific | `RUST_LOG=myapp=debug` | `PTHN_LOG=myapp=debug` |
| Module separator | `::` (e.g., `myapp::core`) | `.` or `::` (e.g., `myapp.core`) |
| Multiple modules | `RUST_LOG=warn,app=debug,lib=error` | Same |
| Trace level | Separate from debug | Maps to DEBUG |

## How It Works

1. Parses RUST_LOG-style specification
2. Converts to Python logging level names
3. Generates a `logging.config.dictConfig` configuration
4. Applies configuration to Python's standard library logging

The logging configuration uses:
- Console handler writing to stderr
- Standard formatter with timestamp, level, logger name, and message
- Non-destructive configuration (doesn't disable existing loggers)

## Development

```bash
# Clone repository
git clone https://github.com/bassmanitram/envlog.git
cd envlog

# Install in development mode
pip install -e ".[dev,test]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=envlog --cov-report=html
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or pull request.

## Acknowledgments

Inspired by Rust's `env_logger` crate and the RUST_LOG convention.
