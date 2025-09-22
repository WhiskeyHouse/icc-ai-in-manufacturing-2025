# Documentation Hub

Comprehensive documentation for the AI in Manufacturing 2025 platform, organized by purpose and audience.

## Quick Navigation

| I need to... | Go here |
|--------------|---------|
| **Set up my development environment** | [`development/GETTING-STARTED.md`](development/GETTING-STARTED.md) |
| **Configure secrets and authentication** | [`setup/SECRETS-QUICKSTART.md`](setup/SECRETS-QUICKSTART.md) |
| **Fix a port conflict or other issue** | [`troubleshooting/`](troubleshooting/) |
| **Understand the API** | [`api/`](api/) |
| **Run a demo presentation** | [`demos/`](demos/) |

## Documentation Structure

### 🚀 Setup & Configuration
**Location**: [`setup/`](setup/)

Essential guides for getting the platform running:
- [`SECRETS-QUICKSTART.md`](setup/SECRETS-QUICKSTART.md) - Authentication setup and GitHub tokens
- [`IGNITION-DOCKER-SETUP.md`](setup/IGNITION-DOCKER-SETUP.md) - Ignition development environment
- [`IGNITION-DEPLOYMENT-MODES.md`](setup/IGNITION-DEPLOYMENT-MODES.md) - Different deployment configurations

### 🔧 Development Resources
**Location**: [`development/`](development/)

Guides for contributors and developers:
- [`GETTING-STARTED.md`](development/GETTING-STARTED.md) - Complete development setup guide
- [`IGNITION-LINTER.md`](development/IGNITION-LINTER.md) - Code quality and linting tools
- [`WHK-TESTING-FRAMEWORK.md`](development/WHK-TESTING-FRAMEWORK.md) - Testing strategies and tools
- [`PLAYWRIGHT-MCP-SETUP.md`](development/PLAYWRIGHT-MCP-SETUP.md) - Browser automation setup
- [`PLAYWRIGHT-IGNITION-AUTH.md`](development/PLAYWRIGHT-IGNITION-AUTH.md) - Authentication in tests
- [`AGENTS.md`](development/AGENTS.md) - AI agent configurations
- [`INTERACTIVE-DEMO-KEYS.md`](development/INTERACTIVE-DEMO-KEYS.md) - Demo interaction guide

### 📚 API Documentation
**Location**: [`api/`](api/)

Technical API references and guides:
- [`IGNITION-8.3-API-GUIDE.md`](api/IGNITION-8.3-API-GUIDE.md) - Ignition API usage patterns
- [`IGNITION-8.3-OPENAPI-ADVANTAGE.md`](api/IGNITION-8.3-OPENAPI-ADVANTAGE.md) - OpenAPI benefits and usage

### 🛠️ Troubleshooting & Support
**Location**: [`troubleshooting/`](troubleshooting/)

Solutions for common issues:
- [`CONFLICT-RESOLUTION-GUIDE.md`](troubleshooting/CONFLICT-RESOLUTION-GUIDE.md) - Port conflicts and resolution
- [`ORBSTACK-CONFLICT-RESOLUTION.md`](troubleshooting/ORBSTACK-CONFLICT-RESOLUTION.md) - OrbStack-specific issues
- [`BUGFIX-SUMMARY.md`](troubleshooting/BUGFIX-SUMMARY.md) - Known issues and workarounds

### 🎯 Demo & Presentation Guides
**Location**: [`demos/`](demos/), [`runbooks/`](runbooks/), [`presentations/`](presentations/)

Materials for demonstrations and presentations:
- [`demos/`](demos/) - Step-by-step demo execution guides
- [`runbooks/`](runbooks/) - Presentation preparation and talk runbooks
- [`presentations/`](presentations/) - Slide outlines and presentation materials

## Documentation Standards

### Writing Guidelines
- **Audience-focused**: Write for the intended reader (developer, presenter, etc.)
- **Actionable**: Include specific commands and examples
- **Linked**: Cross-reference related documentation
- **Updated**: Keep documentation current with code changes

### File Organization
```
docs/
├── setup/              # Environment and installation guides
├── development/        # Developer resources and workflows
├── api/                # API documentation and references
├── troubleshooting/    # Problem resolution guides
├── demos/              # Demo execution instructions
├── runbooks/           # Presentation and talk preparation
└── presentations/      # Slide outlines and materials
```

### Contributing to Documentation

#### Adding New Documentation
1. **Determine location**: Use the structure above to find the right directory
2. **Follow naming conventions**: Use descriptive, kebab-case filenames
3. **Include in navigation**: Update this README and [`../GUIDE-INDEX.md`](../GUIDE-INDEX.md)
4. **Cross-link**: Reference related documentation
5. **Test examples**: Verify all commands and links work

#### Updating Existing Documentation
1. **Check for accuracy**: Ensure instructions still work
2. **Update cross-references**: Fix any broken links
3. **Maintain consistency**: Follow existing style and format
4. **Version information**: Note any version-specific requirements

## Common Documentation Tasks

### Finding Information
```bash
# Search all documentation
grep -r "keyword" docs/

# Find files by name
find docs/ -name "*keyword*"

# List all documentation
tree docs/
```

### Validating Documentation
```bash
# Check links (if using markdown link checker)
markdown-link-check docs/**/*.md

# Validate commands in development guide
cd docs/development && ./validate-commands.sh

# Test demo instructions
./demos/scripts/run-full-stack-demo.sh --auto
```

## Quick Reference

### Essential Documentation
- **New users**: [`../README.md`](../README.md) → [`development/GETTING-STARTED.md`](development/GETTING-STARTED.md)
- **Demo presenters**: [`demos/`](demos/) → [`runbooks/`](runbooks/)
- **Troubleshooting**: [`troubleshooting/`](troubleshooting/) → [`../scripts/demo-preflight.sh`](../scripts/demo-preflight.sh)
- **API developers**: [`api/`](api/) → [`../services/README.md`](../services/README.md)

### External Links
- **Main repository navigation**: [`../GUIDE-INDEX.md`](../GUIDE-INDEX.md)
- **Architecture overview**: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
- **Service documentation**: [`../services/README.md`](../services/README.md)
- **Demo execution**: [`../demos/README.md`](../demos/README.md)

### Getting Help
- **General questions**: Check [`../GUIDE-INDEX.md`](../GUIDE-INDEX.md) for navigation
- **Setup issues**: Start with [`troubleshooting/`](troubleshooting/)
- **Development problems**: See [`development/GETTING-STARTED.md`](development/GETTING-STARTED.md)
- **Demo issues**: Run [`../scripts/demo-preflight.sh`](../scripts/demo-preflight.sh)

---

**💡 Tip**: Use [`../GUIDE-INDEX.md`](../GUIDE-INDEX.md) as your main navigation hub for the entire repository.