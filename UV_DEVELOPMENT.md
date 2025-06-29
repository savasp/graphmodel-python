# Development with UV

This project is configured to use [uv](https://docs.astral.sh/uv/) for fast Python package management and development.

## Quick Start

1. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or on macOS with Homebrew:
   brew install uv
   ```

2. **Install the project and dependencies**:

   ```bash
   uv sync --dev
   ```

3. **Run tests**:

   ```bash
   uv run pytest
   ```

## Common Commands

### Development Setup

```bash
# Install project with all dependencies (including dev)
uv sync --dev

# Install with all optional dependencies
uv sync --all-extras --dev
```

### Running Code

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=graph_model

# Run linting
uv run ruff check .
uv run mypy graph_model

# Format code
uv run black .
uv run isort .
```

### Package Management

```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest-mock

# Remove a dependency
uv remove requests

# Update dependencies
uv lock --upgrade
```

### Building and Publishing

```bash
# Build the package
uv build

# Publish to PyPI (requires credentials)
uv publish

# Publish to Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/
```

### Using Makefile

This project includes a Makefile with common tasks:

```bash
# Show available commands
make help

# Install dependencies
make dev

# Run tests
make test

# Run linting and formatting
make lint
make format

# Build package
make build
```

## Why UV?

- **Fast**: Much faster than pip for installing and resolving dependencies
- **Modern**: Built-in support for modern Python packaging standards
- **Reliable**: Deterministic dependency resolution with lock files
- **Simple**: Single tool for dependency management, virtual environments, and building
- **Compatible**: Works with existing `pyproject.toml` and requirements.txt files

## Environment Management

UV automatically manages virtual environments for you. The project specifies Python 3.11 in `.python-version`, but you can override this:

```bash
# Use a specific Python version
uv python install 3.12
echo "3.12" > .python-version
uv sync --dev
```

## Lock File

UV generates a `uv.lock` file that should be committed to version control for reproducible builds. This ensures all developers and CI systems use the exact same dependency versions.
