# Test Plan for SkogCLI Memory Module

## Testing Strategy

Test SkogCLI memory commands as users experience them, focusing on CLI interface correctness and subprocess integration.

## Commands to Test (from COMMANDS.md)

### `memory bm` - Direct Passthrough
- test_bm_passthrough(List[str]: args): subprocess_result - Test direct passthrough to basic-memory, verify args passed correctly

### `memory write` - Create/Update Notes  
- test_write_basic(str, str, str: title, folder, content): success_message - Test basic note creation with required args
- test_write_with_tags(str, str, str, str: title, folder, content, tags): success_message - Test note creation with comma-separated tags
- test_write_with_project(str, str, str, str: title, folder, content, project): success_message - Test note creation with specific project
- test_write_stdin_content(str, str: title, folder): success_message - Test reading content from stdin when not provided
- test_write_failure(str, str, str: title, folder, content): error_message - Test error handling when basic-memory fails

### `memory read` - Read Notes
- test_read_basic(str: identifier): formatted_output - Test reading note by identifier with default formatting
- test_read_with_pagination(str, int, int: identifier, page, page_size): formatted_output - Test pagination options
- test_read_with_project(str, str: identifier, project): formatted_output - Test reading from specific project
- test_read_raw_output(str: identifier): raw_markdown - Test raw markdown output without formatting
- test_read_to_file(str, str: identifier, output_path): file_created - Test saving note content to file
- test_read_not_found(str: identifier): error_message - Test handling when note doesn't exist

### `memory search` - Search Notes
- test_search_basic(str: query): search_results - Test basic text search across notes
- test_search_with_filters(str, bool, bool: query, permalink, title): filtered_results - Test permalink/title filter options
- test_search_date_filters(str, str, str: query, after_date, before_date): filtered_results - Test date range filtering
- test_search_pagination(str, int, int: query, page, page_size): paginated_results - Test search result pagination
- test_search_json_format(str: query): json_output - Test JSON output format
- test_search_markdown_format(str: query): markdown_output - Test markdown output format

### `memory list` - List Activity
- test_list_default(): recent_activity - Test default recent activity listing
- test_list_with_timeframe(str: timeframe): filtered_activity - Test custom timeframe (7d, 1w, 1m, etc.)
- test_list_with_type_filter(str: activity_type): filtered_activity - Test filtering by activity type
- test_list_with_folder_filter(str: folder): filtered_activity - Test filtering by folder
- test_list_with_depth(int: depth): activity_with_related - Test depth control for related entities
- test_list_json_format(): json_output - Test JSON output format

### `memory sync` - Synchronize
- test_sync_default(): sync_result - Test basic synchronization
- test_sync_with_project(str: project): sync_result - Test syncing specific project
- test_sync_force(): sync_result - Test forced synchronization
- test_sync_dry_run(): preview_result - Test dry run mode
- test_sync_verbose(): detailed_output - Test verbose output mode

### `memory status` - Project Status
- test_status_default(): project_info - Test default project status display
- test_status_specific_project(str: project): project_info - Test status for specific project
- test_status_all_projects(): all_projects_info - Test status for all projects
- test_status_json_format(): json_output - Test JSON output format
- test_status_check_mode(): exit_code - Test check mode returning status codes

## Error Handling Tests
- test_subprocess_failure(): error_handling - Test when subprocess call fails
- test_json_parse_error(): graceful_fallback - Test handling malformed responses
- test_missing_binary(): installation_error - Test when basic-memory not found

## Integration Tests
- test_write_read_workflow(): end_to_end - Test creating then reading same note
- test_search_finds_created_note(): workflow_validation - Test search finds previously created content

## Test Implementation Notes

- Use `subprocess.run` patches to control basic-memory responses
- Verify exact command construction: `["uvx", "basic-memory", ...]`
- Test realistic basic-memory JSON response formats
- Validate user-facing CLI output and formatting
- Test both success and failure scenarios
- Ensure proper exit codes for all commands

## Success Criteria

- All documented CLI commands work as specified
- Subprocess calls constructed correctly
- Response processing handles real data formats
- Error scenarios handled gracefully
- User output formatted consistently
- Fast test execution (< 5 seconds total)