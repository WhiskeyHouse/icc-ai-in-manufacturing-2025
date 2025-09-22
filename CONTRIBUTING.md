# Contributing to AI in Manufacturing 2025

Welcome! This guide helps you contribute effectively to our AI-powered manufacturing demo platform.

## Quick Start for Contributors

1. **Set up your development environment**: [`docs/development/GETTING-STARTED.md`](docs/development/GETTING-STARTED.md)
2. **Understand the architecture**: [`ARCHITECTURE.md`](ARCHITECTURE.md)
3. **Run tests**: `npm test` or see [`docs/development/WHK-TESTING-FRAMEWORK.md`](docs/development/WHK-TESTING-FRAMEWORK.md)
4. **Check code quality**: See [`docs/development/IGNITION-LINTER.md`](docs/development/IGNITION-LINTER.md)

## Development Workflow

### 1. Before You Start
- Create an issue describing your proposed changes
- Check if similar work is already in progress
- Read relevant documentation in [`docs/development/`](docs/development/)

### 2. Development Process
```bash
# Fork and clone the repository
git clone <your-fork-url>
cd icc-ai-in-manufacturing-2025

# Create a feature branch
git checkout -b feature/your-feature-name

# Set up development environment
docker compose up -d
npm install

# Run preflight checks
./scripts/demo-preflight.sh

# Make your changes...

# Test your changes
npm test
./demos/scripts/run-full-stack-demo.sh --auto

# Commit with descriptive messages
git commit -m "feat: add manufacturing efficiency metrics"
```

### 3. Pull Request Guidelines
- **Title**: Use conventional commit format (`feat:`, `fix:`, `docs:`, etc.)
- **Description**: 
  - What does this change do?
  - Why is it needed?
  - How to test it?
- **Testing**: Include test results or demo verification
- **Documentation**: Update relevant docs if needed

## Repository Structure

Understanding our organized structure helps you contribute more effectively:

```
├── services/           # Core platform services
│   ├── ignition/       # SCADA/HMI configurations
│   ├── llama-index/    # AI RAG service
│   ├── rules-engine/   # Validation engine
│   └── monitoring/     # Observability stack
├── docs/               # Documentation (organized by purpose)
├── demos/              # Interactive demonstrations
├── config/             # Service configurations
├── scripts/            # Automation utilities
└── tests/              # Test suites
```

## What We're Looking For

### High-Priority Contributions
- 🤖 **AI/ML improvements**: Enhanced RAG capabilities, better context engineering
- 🏭 **Manufacturing workflows**: New industrial automation scenarios
- 🧪 **Testing**: Expanded test coverage, better validation
- 📊 **Monitoring**: Enhanced observability and metrics
- 📚 **Documentation**: Clearer guides, better examples

### Code Quality Standards
- **Ignition projects**: Follow established patterns in `services/ignition/`
- **Python services**: Use type hints, follow PEP 8
- **Docker**: Multi-stage builds, proper health checks
- **Documentation**: Update both inline and external docs

## Service-Specific Guidelines

### Ignition Components (`services/ignition/`)
- Use consistent naming conventions for views/scripts
- Include resource.json files for all components
- Test with multiple browser sizes
- Document any new modules or dependencies

### AI RAG Service (`services/llama-index/`)
- Include unit tests for new endpoints
- Document new query patterns
- Test with various manufacturing data types
- Consider performance implications

### Rules Engine (`services/rules-engine/`)
- Add validation tests for new rules
- Document business logic clearly
- Ensure error handling is comprehensive
- Test with edge cases

## Testing Your Contributions

### Required Tests
```bash
# Environment validation
./scripts/demo-preflight.sh

# Core functionality
npm test

# End-to-end demo verification
./demos/scripts/run-full-stack-demo.sh --auto

# Service-specific tests (if applicable)
cd services/llama-index && python -m pytest
```

### Manual Testing Checklist
- [ ] All services start without errors
- [ ] Ignition Gateway loads correctly (https://localhost:9043)
- [ ] API endpoints respond as expected
- [ ] Demos run successfully
- [ ] No port conflicts or resource issues

## Documentation Standards

### When to Update Documentation
- Adding new features or services
- Changing configuration requirements
- Updating dependencies or setup steps
- Adding new demo scenarios

### Documentation Locations
- **Setup guides**: `docs/setup/`
- **Developer guides**: `docs/development/`
- **API documentation**: `docs/api/`
- **Troubleshooting**: `docs/troubleshooting/`
- **Service-specific**: `services/{service}/README.md`

### Writing Style
- Use clear, actionable language
- Include code examples where helpful
- Provide context for why changes are needed
- Link to related documentation

## Getting Help

### Resources
- **Architecture questions**: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Setup issues**: [`docs/troubleshooting/`](docs/troubleshooting/)
- **Development environment**: [`docs/development/GETTING-STARTED.md`](docs/development/GETTING-STARTED.md)
- **Navigation help**: [`GUIDE-INDEX.md`](GUIDE-INDEX.md)

### Common Issues
- **Port conflicts**: See [`docs/troubleshooting/CONFLICT-RESOLUTION-GUIDE.md`](docs/troubleshooting/CONFLICT-RESOLUTION-GUIDE.md)
- **Authentication problems**: Check [`docs/setup/SECRETS-QUICKSTART.md`](docs/setup/SECRETS-QUICKSTART.md)
- **Service startup failures**: Run `./scripts/demo-preflight.sh` for diagnostics

## Code Review Process

### What We Look For
- **Functionality**: Does it work as intended?
- **Testing**: Are there appropriate tests?
- **Documentation**: Is it properly documented?
- **Performance**: Does it impact system performance?
- **Security**: Are there any security implications?

### Review Criteria
- Code follows established patterns
- Tests pass and provide good coverage
- Documentation is updated and clear
- No breaking changes without discussion
- Commit messages are descriptive

## Release Process

- **Development**: Feature branches merged to `main`
- **Testing**: Automated tests + manual demo verification
- **Documentation**: Updated with each release
- **Deployment**: Docker images rebuilt and tagged

## Recognition

Contributors are recognized in:
- Release notes for significant contributions
- Documentation credits
- Repository contributor lists

Thank you for contributing to the future of AI in manufacturing! 🏭🤖