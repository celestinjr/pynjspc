# Contributing to pynjspc

Thank you for considering contributing to pynjspc! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Write your code
4. Add tests if applicable
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/celestinjr/pynjspc.git
   cd pynjspc
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # On Windows with PowerShell
   # or
   source .venv/bin/activate  # On Unix/macOS
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Testing

Run tests with pytest:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=pynjspc
```

## Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- mypy for type checking
- flake8 for linting

You can run all of these tools:

```bash
# Format code
black pynjspc tests scripts

# Sort imports
isort pynjspc tests scripts

# Type checking
mypy pynjspc

# Linting
flake8 pynjspc tests scripts
```

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the documentation if needed
3. The PR should work for Python 3.9 and above
4. Ensure all tests pass and code style checks pass

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
