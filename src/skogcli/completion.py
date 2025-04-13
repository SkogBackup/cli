"""Shell completion functionality for SkogCLI."""

import os
import typer
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Iterable

# Import functions needed for completion
from .misc import list_available_scripts, get_user_scripts_dir, get_global_scripts_dir
from .settings import load_settings, get_setting

def get_script_names() -> List[str]:
    """Get a list of all available script names for completion."""
    scripts = list_available_scripts(global_scripts=True)
    return [script.stem for script in scripts]

def get_script_templates() -> List[str]:
    """Get a list of available script templates for completion."""
    from .misc import TEMPLATES
    return list(TEMPLATES.keys())

def get_script_types() -> List[str]:
    """Get a list of available script types for completion."""
    return ["python", "shell"]

def get_config_keys() -> List[str]:
    """Get a list of all configuration keys for completion."""
    settings = load_settings()
    
    def extract_keys(data, prefix=""):
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                keys.append(full_key)
                keys.extend(extract_keys(value, f"{full_key}."))
            else:
                keys.append(full_key)
        return keys
    
    return extract_keys(settings)

def get_memory_folders() -> List[str]:
    """Get a list of memory folders for completion."""
    # This is a placeholder - in a real implementation, you would
    # query basic-memory for the actual folders
    return ["notes", "meetings", "projects", "ideas", "research", "journal"]

def get_memory_projects() -> List[str]:
    """Get a list of memory projects for completion."""
    # This is a placeholder - in a real implementation, you would
    # query basic-memory for the actual projects
    default_project = get_setting("memory.default_project")
    projects = ["default"]
    if default_project and default_project not in projects:
        projects.append(default_project)
    return projects

def register_completion_callbacks(app: typer.Typer) -> None:
    """Register shell completion callbacks for the main app and subcommands."""
    # This function will be called to set up all completion callbacks
    pass
