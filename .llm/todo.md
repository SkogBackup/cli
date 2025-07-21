# Current Tasks

## Fixed Issues  
- [x] Memory read command now returns exit code 1 when note not found
- [x] Added TDD context permanently to CLAUDE.md includes
- [x] Fixed context loss issue that caused erratic behavior

## In Progress
- [ ] Fix script metadata path configuration issues in tests
  - Tests setting config via subprocess but functions read environment variables first
  - Need to set `SKOGAI_SCRIPT_METADATA_DIR` environment variable directly in test setup
  - Started editing tests/test_misc.py line 67-68 but need to complete

## Pending  
- [ ] Run full test suite to identify other failing tests
- [ ] Verify all test expectations match documented TDD behavior
- [ ] Fix config programming - reset/show-defaults/edit-defaults logic is broken
- [ ] Revert default_settings.json corruption - file got mangled during config testing
