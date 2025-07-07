# Development Guide

This guide provides information for developers who want to contribute to or modify the python-homey library.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Adding New Features](#adding-new-features)
- [API Design Guidelines](#api-design-guidelines)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/python-homey.git
   cd python-homey
   ```

2. **Install dependencies:**
   ```bash
   # Install all dependencies including dev dependencies
   uv sync --extra dev
   
   # Activate the virtual environment
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

4. **Verify installation:**
   ```bash
   uv run pytest --version
   uv run black --version
   uv run mypy --version
   ```

### Environment Configuration

Create a `.env` file for local development (this file should not be committed):

```bash
# .env
HOMEY_URL=http://192.168.1.100
HOMEY_TOKEN=your-personal-access-token
DEBUG=true
```

## Project Structure

```
python-homey/
├── src/homey/              # Main package source code
│   ├── __init__.py         # Package exports and convenience functions
│   ├── client.py           # Main HomeyClient class
│   ├── auth.py             # Authentication handling
│   ├── exceptions.py       # Custom exception classes
│   ├── managers/           # Manager classes for different API endpoints
│   │   ├── __init__.py
│   │   ├── base.py         # Base manager class
│   │   ├── devices.py      # Device management
│   │   ├── zones.py        # Zone management
│   │   ├── flows.py        # Flow management
│   │   └── apps.py         # App management
│   └── models/             # Data model classes
│       ├── __init__.py
│       ├── base.py         # Base model class
│       ├── device.py       # Device model
│       ├── zone.py         # Zone model
│       ├── flow.py         # Flow model
│       └── app.py          # App model
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Test configuration and fixtures
│   ├── test_client.py      # Client tests
│   ├── test_managers/      # Manager tests
│   └── test_models/        # Model tests
├── examples/               # Usage examples
│   ├── basic_usage.py
│   ├── device_control.py
│   ├── flow_management.py
│   └── realtime_events.py
├── docs/                   # Documentation source (if using Sphinx)
├── pyproject.toml          # Project configuration
├── README.md               # Main documentation
├── DEVELOPMENT.md          # This file
└── LICENSE                 # MIT license
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow the coding standards and patterns established in the codebase:

- Use async/await for all I/O operations
- Add type hints to all function signatures
- Follow the existing naming conventions
- Add docstrings to all public methods
- Handle errors appropriately with custom exceptions

### 3. Write Tests

Write comprehensive tests for your changes:

```bash
# Run tests for your changes
uv run pytest tests/test_your_feature.py -v

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=homey --cov-report=html
```

### 4. Check Code Quality

```bash
# Format code
uv run black src/homey tests/

# Sort imports
uv run isort src/homey tests/

# Type checking
uv run mypy src/homey

# Run all quality checks
uv run pre-commit run --all-files
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `style:` for formatting changes

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Testing

### Test Structure

Tests are organized into categories:

- **Unit tests**: Test individual functions and methods in isolation
- **Integration tests**: Test interaction between components
- **End-to-end tests**: Test complete workflows (require real Homey)

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_client.py

# Run tests matching a pattern
uv run pytest -k "test_device"

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=homey

# Run only fast tests (skip slow/integration tests)
uv run pytest -m "not slow"
```

### Writing Tests

#### Unit Test Example

```python
import pytest
from unittest.mock import Mock, AsyncMock
from homey import HomeyClient
from homey.exceptions import HomeyAuthenticationError

class TestHomeyClient:
    @pytest.mark.asyncio
    async def test_authenticate_success(self):
        """Test successful authentication."""
        client = HomeyClient(base_url="http://test.local", token="test-token")
        
        with patch.object(client._auth, 'authenticate', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = True
            
            result = await client.authenticate()
            
            assert result is True
            assert client._authenticated is True
            mock_auth.assert_called_once()
```

#### Integration Test Example

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_integration(authenticated_client):
    """Test device operations with real API."""
    devices = await authenticated_client.devices.get_devices()
    assert isinstance(devices, list)
    
    if devices:
        device = devices[0]
        assert hasattr(device, 'id')
        assert hasattr(device, 'name')
```

### Test Fixtures

Common fixtures are defined in `conftest.py`:

```python
@pytest.fixture
async def authenticated_client():
    """Provide an authenticated client for testing."""
    # Implementation here
    pass

@pytest.fixture
def sample_device():
    """Provide a sample device for testing."""
    # Implementation here
    pass
```

## Code Quality

### Code Formatting

We use Black for code formatting:

```bash
# Format all code
uv run black src/homey tests/

# Check formatting without making changes
uv run black --check src/homey tests/
```

### Import Sorting

We use isort for import organization:

```bash
# Sort imports
uv run isort src/homey tests/

# Check import sorting
uv run isort --check-only src/homey tests/
```

### Type Checking

We use mypy for static type checking:

```bash
# Run type checking
uv run mypy src/homey

# Run type checking with verbose output
uv run mypy --verbose src/homey
```

### Linting

Additional linting can be added with flake8 or ruff:

```bash
# Add to pyproject.toml if desired
uv add --dev flake8
uv run flake8 src/homey
```

## Adding New Features

### 1. Manager Classes

When adding support for new Homey API endpoints, create a new manager class:

```python
# src/homey/managers/new_feature.py
from typing import List
from ..models.new_model import NewModel
from .base import BaseManager

class NewFeatureManager(BaseManager):
    """Manager for new feature API endpoints."""
    
    def __init__(self, client: "HomeyClient") -> None:
        super().__init__(client)
        self._endpoint = "/new-feature"
    
    async def get_items(self) -> List[NewModel]:
        """Get all items."""
        return await self._get_all(self._endpoint, NewModel)
    
    async def get_item(self, item_id: str) -> NewModel:
        """Get a specific item."""
        return await self._get_by_id(self._endpoint, item_id, NewModel)
```

### 2. Model Classes

Create corresponding model classes for data structures:

```python
# src/homey/models/new_model.py
from typing import Optional
from pydantic import Field
from .base import BaseModel

class NewModel(BaseModel):
    """Represents a new feature item."""
    
    id: str = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    status: Optional[str] = Field(None, description="Item status")
    
    def is_active(self) -> bool:
        """Check if the item is active."""
        return self.status == "active"
```

### 3. Integration

Add the new manager to the main client:

```python
# src/homey/client.py
from .managers import NewFeatureManager

class HomeyClient:
    def __init__(self, ...):
        # ... existing code ...
        self.new_feature = NewFeatureManager(self)
```

Update the package exports:

```python
# src/homey/__init__.py
from .models import NewModel
from .managers import NewFeatureManager

__all__ = [
    # ... existing exports ...
    "NewModel",
    "NewFeatureManager",
]
```

### 4. Tests

Add comprehensive tests for the new feature:

```python
# tests/test_managers/test_new_feature.py
import pytest
from homey.managers.new_feature import NewFeatureManager
from homey.models.new_model import NewModel

class TestNewFeatureManager:
    @pytest.mark.asyncio
    async def test_get_items(self, mock_homey_client):
        """Test getting all items."""
        manager = NewFeatureManager(mock_homey_client)
        # Test implementation
```

## API Design Guidelines

### Consistency

- Follow the established patterns in existing managers
- Use consistent naming conventions (snake_case for methods, PascalCase for classes)
- Return the same types for similar operations across managers

### Error Handling

- Use specific exception types from `homey.exceptions`
- Provide meaningful error messages
- Include relevant context in exceptions (e.g., device_id for device errors)

### Async/Await

- All I/O operations must be async
- Use proper error handling with try/catch blocks
- Don't block the event loop

### Type Hints

- Add type hints to all public methods
- Use Union types when multiple types are possible
- Use Optional for parameters that can be None

### Documentation

- Add docstrings to all public methods
- Include parameter descriptions
- Provide usage examples for complex methods

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
async def get_device(self, device_id: str) -> Device:
    """
    Get a specific device by ID.
    
    Args:
        device_id: The unique identifier of the device
        
    Returns:
        Device object with full information
        
    Raises:
        HomeyDeviceError: If the device cannot be found or accessed
        HomeyValidationError: If the device_id is invalid
        
    Example:
        ```python
        device = await client.devices.get_device("abc123")
        print(f"Device: {device.name}")
        ```
    """
```

### README Updates

When adding new features, update the README.md with:

- Brief description of the new functionality
- Code examples showing usage
- Links to detailed documentation if applicable

### Example Scripts

Create example scripts in the `examples/` directory to demonstrate new features:

```python
# examples/new_feature_example.py
"""
Example demonstrating the new feature.
"""
import asyncio
from homey import HomeyClient

async def main():
    async with HomeyClient.create(base_url="...", token="...") as client:
        items = await client.new_feature.get_items()
        print(f"Found {len(items)} items")

if __name__ == "__main__":
    asyncio.run(main())
```

## Release Process

### Version Management

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Steps

1. **Update version in pyproject.toml:**
   ```toml
   [project]
   version = "0.2.0"
   ```

2. **Update CHANGELOG.md:**
   Document all changes since the last release

3. **Run full test suite:**
   ```bash
   uv run pytest
   uv run mypy src/homey
   uv run pre-commit run --all-files
   ```

4. **Create release commit:**
   ```bash
   git add .
   git commit -m "chore: release v0.2.0"
   git tag v0.2.0
   ```

5. **Push to repository:**
   ```bash
   git push origin main
   git push origin v0.2.0
   ```

6. **Create GitHub release:**
   - Go to GitHub repository
   - Create new release from tag
   - Add release notes from CHANGELOG.md

7. **Publish to PyPI** (if configured):
   ```bash
   uv build
   uv publish
   ```

## Contributing Guidelines

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Submit a pull request

### Code Review

All changes must be reviewed before merging:

- Code follows established patterns
- Tests are comprehensive
- Documentation is updated
- No breaking changes without major version bump

### Community

- Be respectful in discussions
- Help newcomers get started
- Report bugs with detailed information
- Suggest improvements constructively

## Getting Help

- **Documentation**: Check README.md and this development guide
- **Issues**: Search existing GitHub issues or create a new one
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Community**: Join the Homey Community forum for general Homey questions

## Troubleshooting

### Common Development Issues

**Import Errors:**
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Reinstall dependencies
uv sync --extra dev
```

**Test Failures:**
```bash
# Run tests with verbose output
uv run pytest -v -s

# Run a specific failing test
uv run pytest tests/test_file.py::test_function -v
```

**Type Checking Errors:**
```bash
# Run mypy with more details
uv run mypy --show-error-codes src/homey

# Ignore specific errors if needed (add to pyproject.toml)
```

**Pre-commit Hook Failures:**
```bash
# Run hooks manually
uv run pre-commit run --all-files

# Skip hooks for a commit (not recommended)
git commit --no-verify
```

### Performance Testing

For performance-critical changes:

```bash
# Install performance testing tools
uv add --dev pytest-benchmark

# Run performance tests
uv run pytest tests/test_performance.py
```

### Memory Profiling

```bash
# Install memory profiling tools
uv add --dev memory-profiler

# Profile memory usage
uv run python -m memory_profiler examples/basic_usage.py
```

This development guide should help you get started with contributing to python-homey. If you have questions or suggestions for improving this guide, please open an issue or discussion on GitHub.