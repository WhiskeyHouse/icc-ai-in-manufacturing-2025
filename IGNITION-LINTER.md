# Ignition Linter

The Ignition Linter has been moved to its own repository for better modularity and reusability.

## 📍 New Location

**Repository:** `../ignition-lint`

The linter is now available as a standalone FastMCP server with the following structure:

```
../ignition-lint/
├── src/ignition_lint/
│   ├── __init__.py
│   ├── server.py          # FastMCP server
│   └── cli.py             # Command-line interface
├── tests/
├── examples/
├── docs/
├── pyproject.toml
└── README.md
```

## 🚀 Usage

### As MCP Server (Configured)
The linter is already configured in `.cursor/mcp.json` and will run automatically when Cursor starts.

### Command Line
```bash
cd ../ignition-lint
uv run ignition-lint --project /path/to/ignition/project
```

### HTTP Server
```bash
cd ../ignition-lint  
uv run python3 -m ignition_lint.server --http --port 8008
```

## 🔧 Available Tools

- `check_linter_status()` - Verify linter availability
- `lint_ignition_project()` - Comprehensive project linting
- `lint_perspective_components()` - Lint Perspective components
- `lint_jython_scripts()` - Lint Python/Jython scripts
- `validate_component_json()` - Single component validation
- `validate_script_content()` - Single script validation

## 📚 Documentation

See the full documentation in the new repository: `../ignition-lint/README.md`
