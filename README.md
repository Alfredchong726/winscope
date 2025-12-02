# Centralized Evidence Collection Tool for Windows Incident Response

A modular forensic evidence collection tool for Windows systems designed for incident response and digital forensics investigations.

## Features

- Modular evidence collection (Memory, Disk, Network, Registry, etc.)
- Graphical user interface for easy operation
- Cryptographic hashing for evidence integrity
- Comprehensive audit logging
- HTML report generation

## Requirements

- Python 3.11 or higher
- Windows 10/11
- Administrator privileges (for most collection modules)

## Development Setup

1. Clone this repository
2. Install UV: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
3. Install dependencies: `uv sync --extra dev`
4. Run the application: `uv run python src/main.py`

## Project Structure
```
centralized-evidence-tool/
├── src/
│   ├── core/           # Core application logic
│   ├── modules/        # Evidence collection modules
│   ├── ui/             # User interface components
│   ├── utils/          # Utility functions
│   ├── services/       # Core services
│   └── main.py         # Application entry point
├── tests/              # Unit and integration tests
├── docs/               # Documentation
├── resources/          # Icons, templates, etc.
└── pyproject.toml      # Project configuration
```

## Testing

Run tests with:
```bash
uv run pytest
```

Run tests with coverage:
```bash
uv run pytest --cov=src --cov-report=html
```

## Code Quality

Format code:
```bash
uv run black src tests
```

Lint code:
```bash
uv run pylint src
```

Type check:
```bash
uv run mypy src
```

## License

[Your License Here]

## Author

Chong Mun Seong
