# Getting Started with envlog

## Installation

```bash
pip install envlog
```

## Basic Usage

### 1. Import and Initialize

```python
import logging
import envlog

# Initialize from PTHN_LOG environment variable
envlog.init()

# Create your logger
logger = logging.getLogger(__name__)
logger.info("Application started")
```

### 2. Set Environment Variable

```bash
# In your shell
export PTHN_LOG=info
python your_app.py

# Or inline
PTHN_LOG=debug python your_app.py
```

## Common Patterns

### Pattern 1: Default Level Only

```bash
PTHN_LOG=info
```
All loggers will log at INFO level and above.

### Pattern 2: Quiet by Default, Verbose for Your App

```bash
PTHN_LOG=warn,myapp=debug
```
- Default: WARNING level
- Your app: DEBUG level

### Pattern 3: Multiple Module Control

```bash
PTHN_LOG=warn,myapp.core=info,myapp.db=debug,requests=error
```
- Default: WARNING
- myapp.core: INFO
- myapp.db: DEBUG
- requests: ERROR

### Pattern 4: Rust-Style Syntax

```bash
PTHN_LOG=myapp::database=debug
```
Use `::` separators (converted to Python's `.` internally).

## Level Mapping

| Rust Level | Python Level | Numeric |
|------------|--------------|---------|
| trace      | DEBUG        | 10      |
| debug      | DEBUG        | 10      |
| info       | INFO         | 20      |
| warn       | WARNING      | 30      |
| error      | ERROR        | 40      |
| critical   | CRITICAL     | 50      |

## Advanced Usage

### Custom Environment Variable

```python
envlog.init(env_var='MY_LOG')
```
Then use `MY_LOG=info` instead of `PTHN_LOG=info`.

### Programmatic Configuration

```python
envlog.init(log_spec='warn,myapp=debug')
```
No environment variable needed.

### Custom Format

```python
envlog.init(
    log_spec='debug',
    log_format='%(name)s: %(message)s',
    date_format='%H:%M:%S'
)
```

### Reconfiguration

```python
# First configuration
envlog.init(log_spec='info')

# Later, force reconfigure
envlog.init(log_spec='debug', force=True)

# Or reset then init
envlog.reset()
envlog.init(log_spec='debug')
```

## Tips

1. **Start with WARNING**: Set `PTHN_LOG=warn` to keep third-party libraries quiet
2. **Enable your app**: Add your modules: `PTHN_LOG=warn,myapp=debug`
3. **Debug specific modules**: `PTHN_LOG=warn,myapp.problematic_module=debug`
4. **Production**: `PTHN_LOG=error` or `PTHN_LOG=warn`
5. **Development**: `PTHN_LOG=debug` or `PTHN_LOG=info`

## Troubleshooting

### Nothing is logging

Check your log level:
```python
import logging
logger = logging.getLogger(__name__)
print(f"Effective level: {logger.getEffectiveLevel()}")
```

### Too much output

Set a higher default level:
```bash
PTHN_LOG=error  # Only errors and critical
```

### Third-party libraries too verbose

Set default high, your app low:
```bash
PTHN_LOG=error,myapp=info
```

### Can't see debug messages

Ensure you've set DEBUG level:
```bash
PTHN_LOG=debug  # or
PTHN_LOG=warn,myapp=debug  # for specific module
```

## Examples

See `example.py` in the repository for a complete working example.

## Next Steps

- Read the [README.md](README.md) for full documentation
- Check [CHANGELOG.md](CHANGELOG.md) for version history
- Report issues at https://github.com/bassmanitram/envlog/issues
