# GitHub Actions Workflows

This directory contains CI/CD workflows for the envlog project.

## Workflows

### test.yml
**Trigger**: Push/PR to main, develop, feature branches

Multi-platform, multi-version testing:
- **OS**: Ubuntu, Windows, macOS
- **Python**: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12
- Runs: linting (black, isort), type checking (mypy), tests with coverage

### lint.yml
**Trigger**: Push/PR to main, develop, feature branches

Code quality checks:
- black formatting
- isort import sorting
- mypy type checking
- Package metadata validation

### quality.yml
**Trigger**: Push/PR to main, develop, feature branches

Comprehensive quality checks:
- Pre-commit hooks
- Security scanning (bandit)
- Package build validation
- Installation testing

### dependencies.yml
**Trigger**: Weekly (Monday 9am UTC) + manual

Dependency management:
- Security vulnerability scanning (safety)
- Outdated dependency checks
- Test with latest dependencies

### docs.yml
**Trigger**: Push to main affecting docs

Documentation validation:
- Check documentation files exist
- Validate code examples
- Test documentation imports

### status.yml
**Trigger**: Daily (8am UTC) + manual

Daily health check:
- Full test suite
- Code quality checks
- Package health validation
- Generate status report

### release.yml
**Trigger**: Version tag push (v*)

Release automation:
- Build package
- Create GitHub release
- Publish to PyPI (trusted publishing)
- Generate changelog

## Setup Requirements

### Repository Secrets
None required for basic operation.

### PyPI Trusted Publishing
For release workflow, configure trusted publishing on PyPI:
1. Go to PyPI project settings
2. Add GitHub Actions publisher
3. Repository: bassmanitram/envlog
4. Workflow: release.yml
5. Environment: release

### Branch Protection
Recommended settings for main branch:
- Require status checks: test, lint, quality
- Require review before merge
- Dismiss stale reviews
