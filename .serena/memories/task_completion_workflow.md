# Task Completion Workflow

## Development Methodology: TDD/DDD
1. **ALWAYS START BY WRITING TESTS FIRST** - Non-negotiable
2. **DO NOT MODIFY SOURCE CODE** without proper test coverage first
3. Tests serve as executable specifications
4. Documentation guides design and implementation
5. Any new functionality must be documented before implementation

## Red-Green-Refactor Process
1. **Red**: Write failing test that enforces new desired behavior
2. **Green**: Write simplest code to make all tests pass
3. **Refactor**: Improve code quality while maintaining passing tests

## When Task is Completed
1. **Run all tests**: `make test` or `./tests/run_tests.sh -v`
2. **Run code quality checks**: `make all-checks`
   - Format: `make format` (black)
   - Lint: `make lint` (black check + ruff) 
   - Type check: `make type-check` (mypy)
   - Security: `make security` (bandit)
3. **Run pre-commit hooks**: `make pre-commit`
4. **Verify build**: `make build` (if building package)

## Git Workflow
1. Work on feature branches (not master/main)
2. Commit messages should:
   - Start with present-tense verb (fix, add, implement)
   - Be concise (60-120 characters)
   - End with period
   - Describe intent, not implementation details
3. **No Claude attribution footer** in commits
4. Stage files individually with `git add <file1> <file2>`
5. Use single quotes around filenames with `$` characters

## Verification Commands
- Tests pass: `make test`
- No linting issues: `make lint` 
- No type errors: `make type-check`
- No security issues: `make security`
- Pre-commit hooks pass: `make pre-commit`
- CI simulation: `make ci` (runs all-checks + test)