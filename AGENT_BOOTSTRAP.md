# envlog - Agent Bootstrap

**Purpose**: Configure Python logging via environment variables using Rust's RUST_LOG syntax
**Type**: Library
**Language**: Python 3.8+
**Repository**: https://github.com/bassmanitram/python-envlog

---

## What You Need to Know

**This is**: A zero-dependency Python library that translates Rust-style environment variable logging configuration (`PTHN_LOG=warn,myapp=debug`) into Python's standard library `logging.config.dictConfig` calls. It eliminates the need for code-based logging setup or complex JSON/YAML configuration files.

**Architecture in one sentence**: Parser (string → structured config) → Builder (structured config → dictConfig dict) → Applicator (dictConfig → logging module side effects).

**The ONE constraint that must not be violated**: The parser must remain a pure function with no side effects - all logging state modification happens only in `config.py:init()`.

---

## Mental Model

- Think of this as a **translator**: Rust syntax in, Python logging configuration out
- Three independent stages: **parse** text → **build** dictionary → **apply** to logging
- Parser stage is pure (testable in isolation), application stage has side effects (configures global logging)
- Configuration happens **once** at application startup (protected by `_configured` flag)
- Module-specific levels override default level (hierarchical: `myapp.core` inherits from `myapp`)

---

## Codebase Organization

```
envlog/
├── parser.py      # Pure functions: string parsing, level normalization, validation
├── config.py      # Side effects: dictConfig building, logging initialization, state tracking
├── __init__.py    # Public API surface: init(), reset(), parse_log_spec()
└── tests/         # Unit tests (parser, config) + integration tests (full pipeline)
```

**Navigation Guide**:

| When you need to... | Start here | Why |
|---------------------|------------|-----|
| Add new log level mapping | `parser.py` → `LEVEL_MAP` | All level translations defined here |
| Change syntax parsing | `parser.py` → `parse_log_spec()` | Regex and validation logic |
| Modify logging config structure | `config.py` → `build_dict_config()` | dictConfig dictionary construction |
| Fix initialization behavior | `config.py` → `init()` | State management and application logic |
| Understand end-to-end flow | `tests/test_integration.py` | Shows full pipeline with real logging |

**Entry points**:
- Main execution: `envlog.init()` - Reads env var or accepts string, configures logging
- Tests: `tests/` - Organized by module (parser, config, integration)
- Configuration: Environment variables only (no config files)

---

## Critical Invariants

These rules MUST be maintained:

1. **Parser purity**: `parser.py` functions have no side effects
   - **Why**: Enables testing without mocking, allows reuse in other contexts
   - **Breaks if violated**: Tests become flaky, parsing becomes order-dependent
   - **Enforced by**: Code review, tests don't mock anything in parser

2. **Single initialization per process**: `init()` configures logging once unless `force=True`
   - **Why**: Prevents accidental reconfiguration, matches logging module semantics
   - **Breaks if violated**: Logging behavior becomes unpredictable, configurations override each other
   - **Enforced by**: `_configured` module-level flag in `config.py`

3. **Zero runtime dependencies**: Only Python stdlib imports allowed
   - **Why**: Core project goal - be universally deployable
   - **Breaks if violated**: Project loses its primary value proposition
   - **Enforced by**: `pyproject.toml` has empty `dependencies = []`

---

## Non-Obvious Behaviors & Gotchas

Things that surprise people:

1. **`trace` maps to Python's `DEBUG` level**:
   - **Why it's this way**: Python has no TRACE level in stdlib, DEBUG is the lowest available
   - **Common mistake**: Expecting a separate trace level
   - **Correct approach**: Use DEBUG for most verbose logging, or extend logging module yourself

2. **Second `init()` call does nothing**:
   - **Why**: Prevents accidental reconfiguration from library code
   - **Watch out for**: Tests that call `init()` multiple times - use `reset()` between tests
   - **Correct approach**: Call `reset()` first or use `init(force=True)`

3. **Module names use dots, not double colons**:
   - **Why**: Python uses `myapp.core`, Rust uses `myapp::core`
   - **Pattern**: Parser converts `::` to `.` automatically
   - **Both syntaxes work**: `PTHN_LOG=myapp::core=debug` and `PTHN_LOG=myapp.core=debug` are equivalent

---

## Architecture Decisions

**Why parse-then-build instead of direct translation?**
- **Trade-off**: Extra data structure (`LogSpec`) in the middle adds code but enables testing parser in isolation
- **Alternative considered**: Single function that reads env var and calls `dictConfig()` directly
- **Implications**: Can test parsing without affecting global logging state, can reuse parser for other purposes (e.g., validation tool)

**Why `PTHN_LOG` instead of `RUST_LOG`?**
- **Reason**: Avoid confusion when Python and Rust apps run in same environment
- **Context**: If Python app uses `RUST_LOG`, actual Rust processes can't distinguish their own config
- **Alternative**: Could add env var name as parameter (we do: `init(env_var='...')`)

**Why dictConfig instead of programmatic logger creation?**
- **Trade-off**: dictConfig is more complex but is Python's standard approach
- **Alternative considered**: Manually call `logger.setLevel()` on each logger
- **Why dictConfig wins**: Matches how Python ecosystem expects logging configuration, handles edge cases (existing loggers, handlers, formatters)

---

## Key Patterns & Abstractions

**Pattern 1: Pure Parsing**
- **Used for**: All syntax parsing and validation
- **Structure**: Input string → regex matching → validation → immutable data structure
- **Examples in code**: `normalize_level()`, `parse_log_spec()` - no state, no I/O, pure transformation

**Pattern 2: Guarded Side Effects**
- **Used for**: Applying configuration to global logging state
- **Why not direct application**: Need to prevent accidental double-configuration
- **Structure**: Check `_configured` flag → read source → parse → build → apply → set flag

**Anti-pattern to avoid: Mixing parsing and application**
- **Don't do this**: Calling `logging.config.dictConfig()` inside `parse_log_spec()`
- **Why it fails**: Makes parsing untestable, couples syntax to logging implementation
- **Instead**: Keep parser pure, apply configuration in separate function

---

## State & Data Flow

**State management**:
- **Persistent state**: None (logs go to stderr, not persisted by library)
- **Runtime state**: Single module-level boolean `_configured` in `config.py`
- **No state here**: `parser.py` - completely stateless, all functions are pure

**Data flow**:
```
Env var or string → parse_log_spec() → LogSpec object → build_dict_config() → dict
                                                                ↓
                                                          logging.config.dictConfig()
                                                                ↓
                                                    Global logging configuration
```

**Critical paths**: The flow must preserve purity until the final `dictConfig()` call - any impurity breaks testability.

---

## Integration Points

**This project depends on** (upstream):
- **Python stdlib logging**: Core functionality, tightly coupled (irreplaceable)
- **Python stdlib re**: Regex parsing, loosely coupled (could replace with manual parsing)

**Projects that depend on this** (downstream):
- **yacba**: Uses envlog for CLI logging configuration
- **Your Python apps**: Direct dependency via `pip install envlog`

**Related projects** (siblings):
- **profile-config**: Similar philosophy (environment-based configuration) for app config
- **dataclass-args**: Complementary (CLI args) vs envlog (logging config)

---

## Configuration Philosophy

**What's configurable**: Log levels (global and per-module), log format, date format, environment variable name

**What's hardcoded**:
- Handler type (always StreamHandler to stderr)
- Level name mappings (LEVEL_MAP in parser.py)
- Basic architecture (always parse → build → apply)

**Configuration sources** (in precedence order):
1. `log_spec` parameter to `init()` - Explicit override
2. Environment variable (default `PTHN_LOG`) - Standard usage
3. Hardcoded `'warning'` - Fallback if nothing specified

**The trap**: Calling `init()` after creating loggers - they may not pick up the configuration if they've already cached their level. Solution: Call `init()` first thing in your app's entry point.

---

## Testing Strategy

**What we test**:
- **Parser correctness**: All syntax variations, error cases, level normalization
- **Config building**: dictConfig structure, handler setup, logger hierarchy
- **Integration**: Full pipeline from env var to actual logging output

**What we don't test**:
- **Python's logging module internals**: Assume stdlib works correctly
- **Performance**: Parsing is fast enough, not a bottleneck

**Test organization**: Tests mirror code structure (test_parser.py, test_config.py) plus integration tests. See `tests/test_integration.py` for full pipeline examples.

**Mocking strategy**: No mocks for parser (pure functions), minimal mocking for config (only when simulating specific logging module edge cases)

---

## Common Problems & Diagnostic Paths

**Symptom**: Logging output doesn't appear
- **Most likely cause**: Log level is set too high (e.g., WARNING when you're logging INFO)
- **Check**: Print `logging.getLogger('yourmodule').getEffectiveLevel()` - should be 10 for DEBUG, 20 for INFO, 30 for WARNING
- **Fix**: Lower the level - `PTHN_LOG=debug` or `PTHN_LOG=info,yourmodule=debug`

**Symptom**: Configuration doesn't apply when I call `init()` twice
- **Likely cause**: `_configured` flag prevents second configuration
- **Diagnostic**: Check if `init()` is being called from multiple places (library code and your code)
- **Solution approach**: Call `reset()` first, or use `init(force=True)`, or only call `init()` once at app startup

**Symptom**: Module-specific config not working (e.g., `PTHN_LOG=warn,myapp=debug` but myapp still at WARN)
- **Why it happens**: Logger name doesn't match - maybe logger is "myapp.module" but you specified "myapp"
- **Diagnostic**: Print `logging.getLogger(__name__).name` to see actual logger name
- **Prevention**: Use hierarchical names - `myapp=debug` applies to `myapp` and all children like `myapp.core`, `myapp.util`

---

## Modification Patterns

**To add new log level mapping** (e.g., support "verbose"):
1. Add entry to `LEVEL_MAP` in `parser.py` - maps your name to Python level name
2. Add test case in `tests/test_parser.py::TestNormalizeLevel` - verify mapping works
3. Document in README.md - users need to know it's supported

**To change configuration behavior** (e.g., log to file instead of stderr):
1. Modify `config.py::build_dict_config()` - change handler configuration
2. Update tests in `tests/test_config.py` - verify new handler is created
3. Update tests in `tests/test_integration.py` - verify logging output goes to new destination
4. **Consider**: This might break "zero dependencies" invariant if you need file rotation libraries

**To support new syntax** (e.g., allow level ranges like "debug..warn"):
1. Modify regex in `parser.py::parse_log_spec()` - parse the new syntax
2. Add validation logic - ensure the range is valid
3. Update `LogSpec` dataclass if needed - store the range information
4. Add comprehensive tests in `tests/test_parser.py` - cover all edge cases
5. Update README.md examples - show users how to use it

---

## When to Update This Document

Update this bootstrap when:
- [x] Core architecture changes (e.g., add file handler support, multi-stage parsing)
- [x] New critical invariant added (e.g., thread-safety requirement)
- [x] Major dependency added/removed (currently zero, would be major change)
- [x] Integration points change (e.g., new project depends on this)
- [x] Testing strategy shifts (e.g., add property-based testing)

Don't update for:
- ❌ Feature additions like new level mappings (pure extension, no architectural change)
- ❌ Bug fixes in parser or config builder
- ❌ Refactoring that preserves interfaces
- ❌ Test additions
- ❌ Documentation/README updates

---

**Last Updated**: 2025-12-03
**Last Architectural Change**: Initial architecture established (v0.1.0)
