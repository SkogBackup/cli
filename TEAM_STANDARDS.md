# SkogCLI Team Standards

## Code Style and Conventions

### Python Code Standards

#### Formatting and Style
- **Line Length**: 88 characters (Black default)
- **Import Organization**: Use `ruff` for automatic import sorting
- **Type Hints**: Required for all public functions and methods
- **Docstrings**: Google-style docstrings for all public functions, classes, and modules

#### Example Function Template
```python
def process_user_data(
    user_id: str, 
    data: Dict[str, Any], 
    validate: bool = True
) -> ProcessingResult:
    """Process user data with optional validation.
    
    Args:
        user_id: Unique identifier for the user
        data: User data dictionary to process
        validate: Whether to validate data before processing
        
    Returns:
        ProcessingResult containing success status and processed data
        
    Raises:
        ValidationError: If validation fails when validate=True
        ProcessingError: If data processing fails
        
    Example:
        >>> result = process_user_data("user123", {"name": "John"})
        >>> result.success
        True
    """
```

#### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`
- **Files/Modules**: `snake_case.py`

#### Error Handling
```python
# Preferred: Specific exception types
try:
    result = risky_operation()
except SpecificError as e:
    logger.error("Operation failed: %s", e)
    raise ProcessingError(f"Failed to process: {e}") from e

# Avoid: Bare except clauses
try:
    result = risky_operation()
except:  # ❌ Don't do this
    pass
```

### Testing Standards

#### Test Organization
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Component interaction tests
├── functional/     # End-to-end workflow tests
├── fixtures/       # Shared test data
└── conftest.py     # Pytest configuration
```

#### Test Naming
```python
def test_should_return_valid_config_when_file_exists():
    """Test name explains what should happen when condition is met."""
    pass

def test_should_raise_error_when_config_file_missing():
    """Clear expectation of error conditions."""
    pass
```

#### Test Structure (Arrange-Act-Assert)
```python
def test_user_registration_creates_account():
    # Arrange
    user_data = {"email": "test@example.com", "name": "Test User"}
    mock_db = Mock()
    service = UserService(mock_db)
    
    # Act
    result = service.register_user(user_data)
    
    # Assert
    assert result.success is True
    assert result.user_id is not None
    mock_db.save_user.assert_called_once()
```

### Git Workflow Standards

#### Commit Message Format
We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(auth): add user authentication system
fix(api): resolve timeout issue in data processing
docs: update API documentation for v2 endpoints
test(core): add integration tests for settings module
```

#### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

#### Pull Request Process
1. **Create Feature Branch**: `git checkout -b feature/user-authentication`
2. **Make Changes**: Follow coding standards
3. **Run Tests**: `make test` and `make lint`
4. **Write Tests**: Ensure >90% coverage for new code
5. **Create PR**: Use template, reference issues
6. **Code Review**: Minimum 1 approval required
7. **Merge**: Squash and merge with clean commit message

### Code Review Guidelines

#### What to Look For
- **Functionality**: Does the code do what it's supposed to do?
- **Performance**: Are there obvious performance issues?
- **Security**: Any security vulnerabilities?
- **Maintainability**: Is the code readable and well-structured?
- **Testing**: Are there appropriate tests?

#### Review Checklist
- [ ] Code follows style guidelines
- [ ] Functions have appropriate type hints
- [ ] Public functions have docstrings
- [ ] Tests cover new functionality
- [ ] No obvious security issues
- [ ] Performance considerations addressed
- [ ] Error handling is appropriate

#### Providing Feedback
- **Be Constructive**: Suggest improvements, not just problems
- **Be Specific**: Point to exact lines or provide examples
- **Ask Questions**: "Could this be simplified?" vs "This is wrong"
- **Acknowledge Good Work**: Highlight clever solutions or good practices

### Documentation Standards

#### Code Documentation
- **Modules**: Brief module-level docstring explaining purpose
- **Classes**: Class-level docstring with usage examples
- **Functions**: Google-style docstrings with Args, Returns, Raises
- **Complex Logic**: Inline comments explaining why, not what

#### API Documentation
- All public APIs must be documented
- Include examples for complex operations
- Document error conditions and responses
- Keep examples up-to-date with code changes

#### Architecture Documentation
- Document major design decisions
- Include diagrams for complex systems
- Explain trade-offs and alternatives considered
- Update documentation when architecture changes

### Security Standards

#### Input Validation
```python
def process_user_input(data: str) -> str:
    # Validate input
    if not data or len(data) > MAX_INPUT_LENGTH:
        raise ValidationError("Invalid input length")
    
    # Sanitize input
    cleaned_data = sanitize_input(data)
    
    return process_data(cleaned_data)
```

#### Secret Management
- **Never commit secrets** to version control
- Use environment variables for configuration
- Use secret management tools for production
- Rotate secrets regularly

#### Dependencies
- Keep dependencies up-to-date
- Use `safety` to check for vulnerabilities
- Pin dependency versions in production
- Review new dependencies before adding

### Performance Standards

#### General Guidelines
- **Profile before optimizing**: Use actual data to identify bottlenecks
- **Prefer readability**: Only optimize when necessary
- **Use appropriate data structures**: Choose the right tool for the job
- **Cache appropriately**: But avoid premature caching

#### Database Operations
- Use connection pooling
- Implement query timeouts
- Use appropriate indexes
- Avoid N+1 queries

#### Memory Management
- Clean up resources in `finally` blocks or context managers
- Monitor memory usage in long-running processes
- Use generators for large data sets
- Profile memory usage regularly

### Quality Gates

#### Pre-commit Checks
- Code formatting (Black, Ruff)
- Type checking (MyPy)
- Security scanning (Bandit)
- Test execution (fast tests only)

#### CI/CD Pipeline
- All tests must pass
- Code coverage > 90%
- Security scans must pass
- Documentation builds successfully
- Performance benchmarks within thresholds

#### Definition of Done
- [ ] Feature implemented according to requirements
- [ ] Unit tests written and passing
- [ ] Integration tests updated if needed
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] CI/CD pipeline passes
- [ ] Manual testing completed
- [ ] Security considerations reviewed

### Team Communication

#### Daily Practices
- **Stand-ups**: Daily sync on progress and blockers
- **Code Reviews**: Timely reviews within 24 hours
- **Documentation**: Keep README and docs up-to-date
- **Issues**: Use GitHub issues for bug reports and feature requests

#### Knowledge Sharing
- **Tech Talks**: Weekly presentations on new technologies or solutions
- **Code Walkthroughs**: Regular sessions to explain complex code
- **Documentation**: Write ADRs (Architecture Decision Records)
- **Retrospectives**: Regular team retrospectives to improve processes

### Tools and Environment

#### Required Tools
- **Python 3.12+**: Project requirement
- **UV**: Fast package management
- **Pre-commit**: Automated quality checks
- **VS Code**: Recommended IDE with shared settings

#### Optional but Recommended
- **Poetry**: Alternative package management
- **Docker**: Containerized development
- **GitHub CLI**: Command-line GitHub operations
- **Makefile**: Standardized build commands

### Continuous Improvement

#### Metrics We Track
- **Code Quality**: Coverage, complexity, technical debt
- **Performance**: Response times, throughput, resource usage
- **Team Velocity**: Story points, cycle time, deployment frequency
- **Quality**: Bug rate, customer satisfaction, uptime

#### Regular Reviews
- **Monthly**: Review and update coding standards
- **Quarterly**: Architecture and technology decisions
- **Annually**: Major process and tooling changes

---

## Getting Started

### New Team Member Checklist
- [ ] Read and understand this document
- [ ] Set up development environment using `make dev`
- [ ] Complete coding exercise to validate setup
- [ ] Attend code review training session
- [ ] Join team communication channels
- [ ] Review project architecture documentation

### Questions?
- Ask in team chat for quick questions
- Create GitHub issues for documentation improvements
- Schedule 1:1s for detailed discussions
- Refer to project documentation for technical details

---

*This document is living - please suggest improvements through pull requests.*