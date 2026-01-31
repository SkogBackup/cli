# SkogCLI Functional Map

**Total Code**: ~8200 lines → **Core Functionality**: 2 systems

## System 1: Script Manager/Executor

### Core Types
```python
Script = {
    name: str,
    type: "python" | "shell",
    path: Path,
    content: str,
    executable: bool
}

ScriptMetadata = {
    script_path: str,
    description: str,
    template: str,
    type: str,
    created: datetime,
    last_updated: datetime,
    last_edited: datetime,
    last_run: datetime,
    run_count: int
}

Template = {
    name: str,
    type: "python" | "shell",
    content: str
}

ScriptLocation = "user" | "global"
```

### Pure Functions

#### Discovery & Retrieval
```
get_templates_dir() -> Path
  env:SKOGAI_TEMPLATES_DIR || config:script.templates_dir || package/data/templates

get_template_content(name: str, type: str) -> str
  templates_dir / type / name.ext

list_available_templates() -> {type: [name]}
  scan package & user template dirs

get_user_scripts_dir() -> Path
  env:SKOGAI_TEST_SCRIPT_USER_SCRIPTS_DIR || config:script.user_scripts_dir || env:SKOGAI_SCRIPTS_DIR

get_global_scripts_dir() -> Path
  env:SKOGAI_SCRIPTS_GLOBAL_DIR || /usr/local/share/skogcli/scripts

find_script(name: str, global: bool) -> Path?
  search user_scripts_dir, then global_scripts_dir for [name.py, name.sh, name]

list_available_scripts(global: bool) -> [Path]
  glob user + optional global scripts
```

#### Metadata Operations
```
get_metadata_file() -> Path
  env:SKOGAI_TEST_SCRIPT_METADATA_DIR || config:script.metadata_dir || env:SKOGAI_SCRIPT_METADATA_DIR

load_metadata() -> {script_path: ScriptMetadata}
  json.load(metadata_file)

save_metadata(metadata: {str: Any}) -> void
  json.dump(metadata, metadata_file)

get_script_metadata(path: Path) -> ScriptMetadata
  load_metadata()[str(path)]

update_script_metadata(path: Path, metadata: ScriptMetadata) -> void
  load → merge → add timestamp → save
```

#### Script Execution
```
is_executable(path: Path) -> bool
  os.access(path, os.X_OK)

run_script(name: str, args: [str], global: bool) -> Result
  path = find_script(name, global)
  update_metadata(run_count++, last_run)

  match path.suffix:
    ".py" -> importlib.load + module.main(args)
    _     -> make_executable + subprocess.run([path] + args)
```

#### Script Manipulation
```
create_script(name: str, type: str, template: str, global: bool, description: str) -> Path
  content = get_template_content(template, type)
  dir = global ? get_global_scripts_dir() : get_user_scripts_dir()
  path = dir / f"{name}.{ext}"
  write(path, content)
  chmod(path, +x)
  update_script_metadata(path, {description, template, type, created, run_count: 0})

edit_script(name: str, global: bool, editor: str) -> Result
  path = find_script(name, global)
  check_permissions(path, W_OK)
  subprocess.call([editor, path])
  update_script_metadata(path, {last_edited})

remove_script(name: str, global: bool) -> void
  path = find_script(name, global)
  unlink(path)
  delete_metadata(path)

copy_script(source: str, dest: str, global_src: bool, global_dst: bool) -> void
  src_path = find_script(source, global_src)
  dst_path = dest_dir / f"{dest}{src_path.suffix}"
  shutil.copy2(src_path, dst_path)
  chmod(dst_path, +x)
  copy_metadata(src_path -> dst_path, reset: {created, run_count})
```

#### Code Operations
```
read_script_code(name: str, global: bool) -> str
  find_script(name, global) |> read_file

write_script_code(name: str, content: str, global: bool) -> void
  path = find_script(name, global)
  write(path, content)
  chmod(path, +x)
  update_script_metadata(path, {last_edited})

transform_script(name: str, pattern: str, replacement: str, backup: bool) -> str
  content = read_script_code(name)
  backup ? shutil.copy2(path, path.bak)
  transformed = re.sub(pattern, replacement, content)
  write_script_code(name, transformed)

search_scripts(pattern: str, regex: bool, case_sensitive: bool, global: bool) -> [(Path, [(line_num, line)])]
  scripts = list_available_scripts(global)
  for script in scripts:
    content = read(script)
    matches = find_matches(content, pattern, regex, case_sensitive)
    yield (script, matches)
```

#### Batch Operations
```
batch_process(script_list: Path, command: str, options: BatchOptions) -> void
  scripts = read_lines(script_list)
  for name in scripts:
    path = find_script(name, options.global)

    match command:
      "code"      -> read_script_code + output
      "info"      -> get_script_metadata + display
      "run"       -> run_script
      "search"    -> search_in_script(pattern)
      "transform" -> transform_script(pattern, replacement)
```

#### Import/Export
```
export_script(name: str, output: Path, include_metadata: bool) -> void
  path = find_script(name)
  content = read(path)
  metadata = get_script_metadata(path) if include_metadata
  export = {name, content, type: path.suffix, metadata, exported_at, exported_by}
  json.dump(export, output)

import_script(file: Path, global: bool, overwrite: bool) -> void
  data = json.load(file)
  validate_fields(data, ["name", "content", "type"])
  dir = global ? get_global_scripts_dir() : get_user_scripts_dir()
  path = dir / f"{data.name}.{data.type}"
  write(path, data.content)
  chmod(path, +x)
  if data.metadata: update_script_metadata(path, data.metadata)

import_file(file: Path, name: str?, global: bool) -> void
  name = name || file.stem
  dir = global ? get_global_scripts_dir() : get_user_scripts_dir()
  dest = dir / f"{name}{file.suffix}"
  shutil.copy2(file, dest)
  chmod(dest, +x)
  update_script_metadata(dest, {description: f"Added from {file}", source_file: file})
```

#### AI Generation
```
generate_script(name: str, description: str, type: str, model: str?, api_key: str?, local: bool) -> Path
  if !local && api_key:
    prompt = build_prompt(description, type)
    content = call_openai_api(prompt, model)
  else:
    template = select_template_by_keywords(description)
    content = get_template_content(template, type)
    content = customize_template(content, description)

  content = add_shebang(content, type)
  path = create_script(name, type, content)
  create_symlink(name + ext -> path)  # for user scripts
```

---

## System 2: JSON Key-Value Manipulation

### Core Types
```python
ConfigPath = str  # dot notation: "a.b.c"

Settings = {
  settings: {
    meta: {version: int, last_updated: timestamp},
    module: {history: [HistoryItem]},
    ...nested config...
  },
  credentials: {key: value},
  ...root level config...
}

HistoryItem = {
  timestamp: float,
  session_id: str?,
  message: str?,
  metadata: Any?
}

BackupPath = Path  # config.json.YYYYMMDD_HHMMSS.bak
```

### Pure Functions

#### Path Resolution
```
get_config_dir() -> Path
  env:SKOGAI_CONFIG_DIR || config:settings.cli.storage_dir

get_config_file() -> Path
  get_config_dir() / "config.json"

get_sensitive_config_file() -> Path
  get_config_dir() / "credentials.json"

get_backup_dir() -> Path
  get_config_dir() / "backups"

get_default_settings_file() -> Path
  package / "data" / "default_settings.json"
```

#### Read/Write
```
load_default_settings() -> Settings
  json.load(default_settings.json)

load_settings() -> Settings
  file = get_config_file()
  if !exists(file):
    settings = load_default_settings()
    save_settings(settings)

  settings = json.load(file)
  settings = migrate_config(settings)
  settings = merge_defaults(settings, load_default_settings())

save_settings(settings: Settings) -> bool
  update_metadata(settings, {last_updated: now})
  create_backup(config_file)

  # Split sensitive data
  main = settings.copy()
  main.credentials = {}
  json.dump(main, config_file)

  if settings.credentials:
    json.dump(settings.credentials, credentials_file)

load_sensitive_settings() -> {str: Any}
  json.load(credentials_file) | {}
```

#### Key Access (Dot Notation)
```
get_setting(key: str) -> Any
  # Priority: test env vars > env vars > config file > default

  env_value = getenv(f"SKOGAI_TEST_{key.upper().replace('.', '_')}")
            || getenv(f"SKOGAI_{key.upper().replace('.', '_')}")
  if env_value: return parse_value(env_value)

  # Handle special $ section
  if key.startsWith("$."):
    return navigate_path(settings.$, key[2:])

  # Handle credentials separately
  if key.startsWith("credentials."):
    return load_sensitive_settings()[key.split('.', 1)[1]]

  # Navigate nested structure
  return navigate_path(settings, key.split('.'))

set_setting(key: str, value: Any) -> bool
  settings = load_settings()

  if key.startsWith("credentials."):
    sensitive = load_sensitive_settings()
    sensitive[key.split('.', 1)[1]] = value
    json.dump(sensitive, credentials_file)
    settings.credentials[...] = value
  else:
    set_nested(settings, key.split('.'), value)

  save_settings(settings)

navigate_path(data: dict, path: [str]) -> Any
  current = data
  for part in path:
    if part not in current: return None
    current = current[part]
  return current

set_nested(data: dict, path: [str], value: Any) -> void
  current = data
  for part in path[:-1]:
    if part not in current: current[part] = {}
    current = current[part]
  current[path[-1]] = value
```

#### Backup/Restore
```
create_backup(file: Path) -> Path?
  if !exists(file): return None
  backup = backup_dir / f"{file.name}.{timestamp}.bak"
  shutil.copy2(file, backup)

restore_from_latest_backup() -> Settings?
  backups = glob(backup_dir / "config.json.*.bak")
  latest = max(backups, key=lambda p: p.stat().st_mtime)
  json.load(latest)

list_backups() -> [(Path, mtime, size)]
  backups = glob(backup_dir / "*.bak")
  sort_by_mtime_desc(backups)
```

#### Migration
```
migrate_config(settings: Settings) -> Settings
  if !has_version(settings):
    settings.settings.meta = {version: CONFIG_VERSION, last_updated: now()}
    settings.settings.module = {history: []}
    settings.credentials = {}

  # Move old chat.history to settings.module.history
  if "chat" in settings && "history" in settings.chat:
    settings.settings.module.history = settings.chat.history

  # Future: version-based migrations
  return settings

reset_settings() -> bool
  create_backup(config_file)
  create_backup(credentials_file)
  settings = load_default_settings()
  settings.credentials = {}
  settings.settings.meta = {last_updated: now()}
  save_settings(settings)
```

#### History Management
```
add_chat_history_item(item: HistoryItem) -> bool
  settings = load_settings()
  ensure_path(settings, "settings.module.history")
  item.timestamp = now()
  settings.settings.module.history.append(item)

  max_items = settings.settings.module.max_history_items | 100
  if len(history) > max_items:
    history = history[-max_items:]

  save_settings(settings)

get_chat_history(limit: int?) -> [HistoryItem]
  settings = load_settings()
  history = settings.settings.module.history | []
  sort_by_timestamp_desc(history)
  return history[:limit] if limit else history

clear_chat_history() -> bool
  settings = load_settings()
  create_backup(config_file)
  settings.settings.module.history = []
  save_settings(settings)
```

#### Environment Export
```
export_env(namespace: str?, output: Path?) -> str
  settings = load_settings()
  env_pairs = extract_env_pairs(settings)  # all *.env.* keys

  if namespace:
    # Support comma-separated with precedence: "claude,agent" -> agent wins
    env_dict = {}
    for ns in namespace.split(','):
      pairs = filter(lambda (k,v): k.startsWith(f"{ns}.env."), env_pairs)
      for key, value in pairs:
        env_name = key.split(".env.")[1]
        env_dict[env_name] = value  # later namespaces override

    env_pairs = env_dict.items()

  export_lines = [f'export {name}="{escape(value)}"' for name, value in env_pairs]

  if output:
    write(output, "\n".join(export_lines))
  else:
    print("\n".join(export_lines))

extract_env_pairs(data: dict, prefix: str = "") -> [(str, Any)]
  pairs = []
  for key, value in data.items():
    full_key = prefix + key
    if isinstance(value, dict):
      pairs.extend(extract_env_pairs(value, full_key + "."))
    elif ".env." in full_key && value != None:
      pairs.append((full_key, value))
  return pairs
```

#### Query/List
```
get_config_keys() -> [str]
  settings = load_settings()
  extract_all_keys(settings)  # recursive flatten

extract_all_keys(data: dict, prefix: str = "") -> [str]
  keys = []
  for key, value in data.items():
    full_key = prefix + key
    keys.append(full_key)
    if isinstance(value, dict):
      keys.extend(extract_all_keys(value, full_key + "."))
  return keys
```

---

## Additional Subsystems

### Memory System (Wrapper around basic-memory)
```
run_basic_memory(args: [str]) -> subprocess.CompletedProcess
  subprocess.run(["uvx", "basic-memory"] + args)

# All commands are thin wrappers:
write_note(title, folder, content?, tags?, project?) -> subprocess -> basic-memory tool write-note
read_note(identifier, page, page_size, project?, raw?) -> subprocess -> basic-memory tool read-note
search_notes(query, filters, page, project?) -> subprocess -> basic-memory tool search-notes
list_notes(type?, folder?, timeframe, page, project?) -> subprocess -> basic-memory tool recent-activity
sync(project?, force?, dry_run?, verbose?) -> subprocess -> basic-memory sync
status(project?, format?, show_all?) -> subprocess -> basic-memory project info
```

### Agent System (Script-based execution)
```
Agent = {
  name: str,
  model: str?,
  system_prompt: str?,
  description: str?,
  command_template: str?  # e.g. "python -m goose run --text {message}"
}

create_agent_script(name: str, command: str) -> Path
  script = f"""#!/bin/bash
# Agent script for {name}
{command.replace("{message}", "$1")}
"""
  path = ./scripts / f"{name}.sh"
  write(path, script)
  chmod(path, +x)

send(message: str, agent: str, model?: str, system?: str) -> str
  script = ./scripts / f"{agent}.sh"
  if !exists(script): create_agent_script(agent, default_cmd)
  result = subprocess.run([script, message], capture_output=True)
  return result.stdout

# Agent CRUD operations are just config operations:
create_agent(name, config) -> set_setting(f"agent.{name}", config) + create_agent_script
list_agents() -> get_setting("agent.agents")
delete_agent(name) -> remove from agents list + delete config + unlink script
```

---

## Core Functional Patterns

### Pattern 1: Path Resolution with Fallbacks
```
resolve_path(test_env, user_env, config_key, default) -> Path
  test_env_val || user_env_val || get_setting(config_key) || default
```

### Pattern 2: CRUD with Metadata Tracking
```
create(item) -> write(item) + track_metadata(created, last_updated)
read(item) -> load(item) + track_metadata(last_accessed?)
update(item) -> write(item) + track_metadata(last_updated, last_edited)
delete(item) -> unlink(item) + delete_metadata(item)
```

### Pattern 3: Batch Operations
```
batch(operation, items, continue_on_error) -> for item in items: try operation(item)
```

### Pattern 4: Environment Variable Override
```
get_value(key) -> env[TEST_PREFIX + key] || env[PREFIX + key] || config[key] || default[key]
```

### Pattern 5: Nested Key Navigation
```
navigate(data, "a.b.c") -> data["a"]["b"]["c"]
set_nested(data, "a.b.c", value) -> data["a"]["b"]["c"] = value
```

---

## Type System Summary

### Script System Types
```
Script, ScriptMetadata, Template, ScriptLocation
Path, Content: str, Executable: bool
Extension: ".py" | ".sh"
```

### Config System Types
```
Settings, ConfigPath, HistoryItem, BackupPath
Key: str, Value: Any, Timestamp: float
Namespace: str
```

### Common Types
```
Result<T> = Ok(T) | Error(str)
Path = string (absolute or relative file path)
Timestamp = float (seconds since epoch) | ISO8601 string
Metadata = {[string]: any}
```

---

## Composition Examples

### Script Workflow
```
create_and_run_script:
  template_content = get_template_content(template, type)
  path = create_script(name, template_content)
  result = run_script(name, args)
  return result

batch_transform:
  scripts = read_script_list(file)
  for script in scripts:
    content = read_script_code(script)
    transformed = transform(content, pattern, replacement)
    write_script_code(script, transformed)
```

### Config Workflow
```
safe_config_update:
  backup = create_backup(config_file)
  try:
    settings = load_settings()
    set_nested(settings, key.split('.'), value)
    save_settings(settings)
  except:
    restore(backup)

export_namespace_env:
  settings = load_settings()
  env_vars = extract_env_pairs(settings)
  filtered = filter_by_namespace(env_vars, namespace)
  export_statements = format_export(filtered)
  write_or_print(export_statements, output)
```

---

## Reduction to Core Transformations

### Script Manager
```
Templates × Scripts → Instances
Search(Scripts, Pattern) → Matches
Transform(Script, Pattern, Replacement) → Script'
Execute(Script, Args) → Result
Batch(Operation, [Scripts]) → [Result]
```

### JSON Manipulator
```
Get(Settings, Path) → Value
Set(Settings, Path, Value) → Settings'
Navigate(Settings, [PathPart]) → Value
Export(Settings, Namespace) → EnvVars
Backup(Settings) → Settings@Timestamp
Migrate(Settings@V_old) → Settings@V_new
```

### Cross-Cutting
```
MetadataTrack(Operation) → Operation' + UpdateMetadata
PathResolve([Source]) → Path
ValueParse(String) → TypedValue
```

---

## Implementation Notes

1. **All operations are effectful** - real I/O, subprocess, file system
2. **No pure functional core** - tightly coupled to side effects
3. **Metadata is parallel to data** - separate JSON file tracking
4. **Config is environment-aware** - multi-layer override system
5. **Scripts are templated** - parameterized text generation
6. **Agent system is thin** - just script generation + subprocess
7. **Memory is delegated** - wrapper around external tool

## Separation Strategy for Refactor

### System 1: Script Executor
```
Core: Execute(Path, Args) → Result
Metadata: Track(Path) → Metadata
Templates: Expand(Template, Params) → Content
Batch: Map(Operation, [Path]) → [Result]
```

### System 2: JSON Manipulator
```
Core: Get/Set(Data, KeyPath, Value?) → Value | Data'
Query: Navigate(Data, [PathPart]) → Value
Transform: Migrate(Data@V) → Data@V'
Export: ToEnv(Data, Namespace?) → [EnvVar]
```

### Shared
```
Path Resolution: Resolve([Source]) → Path
Value Parsing: Parse(String) → TypedValue
Backup/Restore: Snapshot(Data, Path) → Data@T
```
