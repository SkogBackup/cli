# SkogCLI Team Onboarding Guide

Welcome to the SkogCLI development team! This guide will help you get up and running quickly and understand our development culture.

## 🚀 Quick Start (15 minutes)

### Prerequisites
- **Python 3.12+** installed
- **Git** configured with your credentials
- **UV** package manager (we'll install this)
- **VS Code** (recommended) or your preferred editor

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-org/skogcli.git
cd skogcli

# Install UV (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up development environment
make dev

# Activate virtual environment
source .venv/bin/activate

# Verify installation
skogcli version
skogcli --help
```

### 2. Verify Your Setup
```bash
# Run the test suite
make test

# Run code quality checks
make lint

# Build documentation
mkdocs serve
```

If all commands succeed, you're ready to develop! 🎉

## 📚 Understanding the Codebase

### Project Structure
```
skogcli/
├── src/skogcli/          # Main package
│   ├── __init__.py       # CLI entry point
│   ├── settings.py       # Configuration management
│   ├── script.py         # Script management
│   ├── memory.py         # Memory/knowledge management
│   ├── agent.py          # AI agent integration
│   └── monitoring.py     # Logging and metrics
├── tests/                # Test suite
│   ├── unit/            # Fast, isolated tests
│   ├── integration/     # Component interaction tests
│   └── functional/      # End-to-end workflows
├── docs/                # Documentation source
├── .github/             # CI/CD and issue templates
└── scripts/             # Development scripts
```

### Key Concepts
- **CLI-First Design**: Everything accessible via command line
- **Configuration Management**: Centralized, versioned configuration
- **Script Management**: Create, run, and manage custom scripts
- **Memory System**: Knowledge management for AI agents
- **Team Standards**: Consistent code style and practices

## 🎯 Your First Contribution

### 1. Pick a Good First Issue
Look for issues labeled `good-first-issue` or `help-wanted`. These are:
- Well-defined scope
- Clear acceptance criteria
- Mentorship available
- Good learning opportunities

### 2. Development Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit code ...

# Run tests and quality checks
make check

# Commit with conventional commit format
git commit -m "feat: add new feature description"

# Push and create pull request
git push origin feature/your-feature-name
```

### 3. Pull Request Process
1. **Create PR** using our template
2. **Automated checks** run (CI/CD pipeline)
3. **Code review** from team members
4. **Address feedback** if needed
5. **Merge** when approved and checks pass

## 🛠️ Development Tools

### Essential Commands
```bash
# Development
make dev              # Set up development environment
make test             # Run all tests
make test-unit        # Run only unit tests
make lint             # Code linting and formatting
make type-check       # Type checking with MyPy
make security         # Security scanning

# Documentation
mkdocs serve          # Serve docs locally
mkdocs build          # Build docs for production

# Release
make clean            # Clean build artifacts
make build            # Build package
```

### VS Code Setup
Our `.vscode/` directory includes:
- **Settings**: Formatting, linting, testing configuration
- **Extensions**: Recommended development extensions
- **Tasks**: Common development operations
- **Debug configs**: For debugging CLI and tests

### Git Workflow
We use **Conventional Commits**:
```
feat: add user authentication system
fix: resolve timeout issue in data processing
docs: update API documentation for v2 endpoints
test: add integration tests for settings module
```

**Branch naming**:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🎓 Learning Path

### Week 1: Foundation
- [ ] Complete environment setup
- [ ] Read team standards document
- [ ] Explore codebase structure
- [ ] Run existing tests and understand test patterns
- [ ] Make first small contribution (documentation, test improvement)

### Week 2: Core Development
- [ ] Implement a small feature or bug fix
- [ ] Write comprehensive tests
- [ ] Go through code review process
- [ ] Understand CI/CD pipeline
- [ ] Participate in team discussions

### Week 3: Advanced Topics
- [ ] Work on larger feature
- [ ] Contribute to architecture decisions
- [ ] Help review others' code
- [ ] Improve development tools or processes
- [ ] Mentor newer team members

## 🤝 Team Culture

### Communication
- **Daily Standups**: Share progress and blockers
- **Code Reviews**: Constructive feedback and knowledge sharing
- **Documentation**: Keep documentation current and helpful
- **Knowledge Sharing**: Regular tech talks and learning sessions

### Code Review Principles
- **Be Kind**: Constructive feedback, not criticism
- **Be Specific**: Point to exact issues with suggestions
- **Ask Questions**: "Could this be simplified?" vs "This is wrong"
- **Acknowledge Good Work**: Highlight clever solutions
- **Focus on Important Issues**: Don't nitpick formatting (automation handles that)

### Quality Standards
- **Test Coverage**: >90% for new code
- **Documentation**: All public APIs documented
- **Type Hints**: Required for all functions
- **Security**: Regular scans, no secrets in code
- **Performance**: Profile before optimizing

## 🔧 Common Development Tasks

### Adding a New CLI Command
1. **Add command function** in appropriate module
2. **Add to CLI app** in `__init__.py`
3. **Write comprehensive tests** (unit + integration)
4. **Update documentation**
5. **Add to help system**

### Debugging Issues
```bash
# Run specific test
pytest tests/unit/test_specific.py::test_function -v

# Debug with pdb
pytest --pdb tests/unit/test_specific.py::test_function

# Check logs
skogcli --debug command-that-fails

# Profile performance
python -m cProfile -o profile.out script.py
```

### Working with Configuration
```bash
# Show current config
skogcli config show

# Modify config for testing
skogcli config set test.setting value

# Reset to defaults
skogcli config reset --yes
```

## 🚨 Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure you're in the right directory and venv is activated
cd /path/to/skogcli
source .venv/bin/activate
```

**Test failures:**
```bash
# Run tests with verbose output
pytest -v -s

# Run only failed tests
pytest --lf

# Clear test cache
pytest --cache-clear
```

**CI/CD failures:**
```bash
# Run the same checks locally
make check

# Fix formatting issues
make format

# Update dependencies
uv pip sync requirements.txt
```

### Getting Help
- **Ask in team chat** for quick questions
- **Create GitHub issues** for bugs or feature requests
- **Schedule pair programming** for complex problems
- **Check documentation** in `docs/` directory
- **Review existing code** for patterns and examples

## 📖 Additional Resources

### Documentation
- [Team Standards](TEAM_STANDARDS.md) - Comprehensive coding standards
- [Architecture Decision Records](docs/architecture/) - Key design decisions
- [API Documentation](https://skogix.github.io/skogcli/) - Complete API reference

### External Resources
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

### Tools Documentation
- [UV Package Manager](https://docs.astral.sh/uv/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [Black Formatter](https://black.readthedocs.io/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)

## 🎯 Success Metrics

After your first month, you should be able to:
- [ ] Navigate the codebase confidently
- [ ] Implement features following team standards
- [ ] Write comprehensive tests
- [ ] Participate effectively in code reviews
- [ ] Debug issues independently
- [ ] Contribute to architectural discussions
- [ ] Help onboard newer team members

## 🤔 Feedback and Improvement

We're always improving our onboarding process. Please share feedback:
- What was confusing or unclear?
- What additional resources would be helpful?
- What took longer than expected?
- What went really well?

Create an issue with the `onboarding-feedback` label or discuss in team chat.

---

## Welcome to the Team! 🎉

Remember, everyone was new once. Don't hesitate to ask questions - we're here to help you succeed and contribute to making SkogCLI even better.

**Your success is our success. Let's build something amazing together!**

---

*Need immediate help? Contact your onboarding buddy or post in the team chat.*