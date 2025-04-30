"""Agent commands for SkogCLI."""

import typer
import json
import os
import stat
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from .decorators import with_explanation
from .settings import get_setting, set_setting, get_config_keys

# Create a Typer app for the agent commands
agent_app = typer.Typer(
    help="Interact with SkogAI agents",
    no_args_is_help=True
)

console = Console()

def get_scripts_dir() -> Path:
    """
    Get the path to the scripts directory, creating it if it doesn't exist.
    
    Returns:
        Path: Path to the scripts directory
    """
    scripts_dir = Path("./scripts")
    scripts_dir.mkdir(exist_ok=True)
    return scripts_dir

def ensure_executable(path: str) -> bool:
    """
    Ensure a file is executable by adding execute permissions if needed.
    
    Args:
        path: Path to the file to check
        
    Returns:
        bool: True if the file is now executable, False otherwise
    """
    try:
        # Check if the file exists
        if not os.path.isfile(path):
            return False
            
        # Check if the file is already executable
        if os.access(path, os.X_OK):
            return True
            
        # Add execute permission
        current_permissions = os.stat(path).st_mode
        os.chmod(path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        # Verify the change worked
        return os.access(path, os.X_OK)
    except Exception:
        return False

def create_agent_script(agent_name: str, command: str) -> Path:
    """
    Create or update a script for the specified agent.
    
    Args:
        agent_name: Name of the agent
        command: Command to run in the script
        
    Returns:
        Path: Path to the created script
    """
    scripts_dir = get_scripts_dir()
    script_path = scripts_dir / f"{agent_name}.sh"
    
    # Create the script content with $1 as the message parameter
    # Replace {message} with $1 in the command
    command_with_param = command.replace("{message}", "$1")
    
    script_content = f"""#!/bin/bash
# Agent script for {agent_name}
# This file is managed by skogcli - manual changes may be overwritten

# Execute the agent command
# $1 is the message parameter passed to the script
{command_with_param}
"""
    
    # Write the script
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make it executable
    ensure_executable(str(script_path))
    
    return script_path

def get_agent_config_keys() -> List[str]:
    """Get a list of agent configuration keys for completion."""
    all_keys = get_config_keys()
    return [key for key in all_keys if key.startswith("agent.")]

def get_agent_names() -> List[str]:
    """Get a list of configured agent names for completion."""
    # Try to get agent names from configuration
    agents = get_setting("agent.agents") or []
    if isinstance(agents, list):
        return agents
    return ["default", "assistant", "researcher", "coder"]

@agent_app.command("migrate-scripts")
@with_explanation("Migrate all agents to use script files.")
def migrate_scripts():
    """
    Create script files for all existing agents.
    
    This command will create script files in the ./scripts directory for all
    configured agents, based on their current command templates.
    """
    # Get all agents
    agents = get_setting("agent.agents") or []
    
    if not agents:
        console.print("[yellow]No agents configured.[/]")
        return
    
    # Create scripts directory if it doesn't exist
    scripts_dir = get_scripts_dir()
    
    # Migrate each agent
    migrated = 0
    for agent_name in agents:
        # Get the command template
        command_template = get_setting(f"agent.{agent_name}.command_template")
        message_template = get_setting(f"agent.{agent_name}.message_template")
        message_setting = get_setting(f"agent.{agent_name}.message")
        
        # Determine the command to use
        if message_setting:
            command = message_setting.format(message="{message}")
        elif command_template:
            command = command_template.format(message="{message}")
        elif message_template:
            command = message_template.format(message="{message}")
        else:
            command = f"echo \"Agent {agent_name} is responding to: $1\""
        
        # Create the script
        script_path = create_agent_script(agent_name, command)
        console.print(f"Created script for agent '{agent_name}': {script_path}")
        migrated += 1
    
    console.print(f"[green]Migration complete:[/] {migrated} agent scripts created in {scripts_dir}")

@agent_app.callback()
def agent_callback(ctx: typer.Context):
    """Interact with SkogAI agents."""
    # Check if we're using dot notation format (agent.name)
    if ctx.invoked_subcommand is None and len(ctx.args) > 0:
        # Get the first argument which should be in format "name"
        arg = ctx.args[0]
        if "." in arg and not arg.startswith("-"):
            # Split into agent name and command
            parts = arg.split(".", 1)
            if len(parts) == 2:
                agent_name = parts[1]
                
                # Check if there are remaining arguments
                remaining_args = ctx.args[1:] if len(ctx.args) > 1 else []
                
                try:
                    if remaining_args and remaining_args[0] == "send" and len(remaining_args) > 1:
                        # Call the send command with the agent name
                        message = remaining_args[1]
                        ctx.invoke(send, message=message, agent_name=agent_name)
                        return
                    elif remaining_args and remaining_args[0] == "read":
                        # Call the read command with the agent name
                        ctx.invoke(read_agent, name=agent_name)
                        return
                    else:
                        # Default to read if no command is specified
                        ctx.invoke(read_agent, name=agent_name)
                        return
                except Exception as e:
                    console.print(f"[bold red]Error:[/] {str(e)}")
                    raise typer.Exit(1)

@agent_app.command("send")
@with_explanation("Send a message to an agent.")
def send(
    message: str = typer.Argument(..., help="Message to send to the agent"),
    agent_name: str = typer.Option(
        "default", "--agent", "-a", 
        help="Name of the agent to send the message to",
        autocompletion=get_agent_names
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", 
        help="Model to use for this interaction"
    ),
    system_prompt: Optional[str] = typer.Option(
        None, "--system", "-s", 
        help="System prompt to use for this interaction"
    ),
    raw: bool = typer.Option(
        False, "--raw", "-r", 
        help="Display raw response without formatting"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", 
        help="Output response in JSON format"
    ),
):
    """
    Send a message to an agent and display the response.
    
    Examples:
    
    Send a simple message:
      skogcli agent send "What is the capital of France?"
    
    Specify an agent:
      skogcli agent send "Write a Python function to calculate Fibonacci numbers" --agent coder
    
    Use a specific model:
      skogcli agent send "Summarize this article" --model gpt-4
    """
    # Get agent configuration
    agent_config = get_setting(f"agent.{agent_name}") or {}
    
    # Use provided model or fall back to agent config or default
    model_to_use = model or agent_config.get("model") or get_setting("agent.default_model") or "gpt-3.5-turbo"
    
    # Use provided system prompt or fall back to agent config or default
    system_to_use = system_prompt or agent_config.get("system_prompt") or get_setting("agent.default_system_prompt") or ""
    
    # Get the message template from the agent configuration
    message_template = get_setting(f"agent.{agent_name}.message")
    
    import subprocess
    from shlex import split
    
    # Get the command template from the agent configuration
    # Check all possible configuration keys for backward compatibility
    command_template = get_setting(f"agent.{agent_name}.command_template")
    message_template = get_setting(f"agent.{agent_name}.message_template")
    message_setting = get_setting(f"agent.{agent_name}.message")
    
    # Determine the command to run
    if message_setting:
        # This is the primary setting that should be used
        command = message_setting.format(message=message)
    elif command_template:
        # Secondary option
        command = command_template.format(message=message)
    elif message_template:
        # Legacy support
        command = message_template.format(message=message)
    else:
        # Default to a simple echo command if no template is found
        default_msg = f"No command template configured for agent '{agent_name}'. Please set one using 'skogcli agent set message \"your command {{message}}\" --agent {agent_name}'"
        command = f"echo \"{default_msg}\""
    
    # Create or update the agent script
    script_path = create_agent_script(agent_name, command)
    
    # Prepare the command to run the script
    args = [str(script_path)]
    
    # Call the command with the provided message
    try:
        # Execute the script with the message as an argument
        result = subprocess.run(
            [args[0], message],  # Pass message as an argument to the script
            capture_output=True,
            text=True,
            check=True
        )
        response = result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr
        response = f"[bold red]Error:[/] {error_msg}"
    except FileNotFoundError:
        response = f"[bold red]Error:[/] Script not found: {args[0]}"
    except Exception as e:
        response = f"[bold red]Error:[/] {str(e)}"
    
    # Display the response
    if json_output:
        output = {
            "agent": agent_name,
            "model": model_to_use,
            "message": message,
            "response": response
        }
        print(json.dumps(output, indent=2))
    elif raw:
        print(response)
    else:
        console.print(Panel(
            Markdown(response),
            title=f"Response from {agent_name}",
            border_style="green"
        ))

@agent_app.command("list")
@with_explanation("List available agents.")
def list_agents():
    """List all available agents and their configurations."""
    # Get agent configuration
    agents = get_setting("agent.agents") or []
    
    if not agents:
        console.print("[yellow]No agents configured.[/]")
        console.print("Use 'skogcli agent create' to create a new agent.")
        return
    
    console.print("[bold]Available agents:[/]")
    for agent_name in agents:
        agent_config = get_setting(f"agent.{agent_name}") or {}
        model = agent_config.get("model", get_setting("agent.default_model") or "Not specified")
        
        console.print(f"  [bold]{agent_name}[/]")
        console.print(f"    Model: {model}")
        if "description" in agent_config:
            console.print(f"    Description: {agent_config['description']}")

@agent_app.command("create")
@with_explanation("Create a new agent.")
def create_agent(
    name: str = typer.Argument(..., help="Name for the new agent"),
    model: str = typer.Option(
        None, "--model", "-m", 
        help="Model to use for this agent"
    ),
    system_prompt: Optional[str] = typer.Option(
        None, "--system", "-s", 
        help="System prompt for this agent"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", 
        help="Description of this agent"
    ),
    command_template: Optional[str] = typer.Option(
        None, "--command", "-c",
        help="Command template to use for this agent (e.g., 'python -m goose run --text {message}')"
    ),
):
    """
    Create a new agent with the specified configuration.
    
    Examples:
    
    Create a basic agent:
      skogcli agent create researcher
    
    Create an agent with a specific model:
      skogcli agent create coder --model gpt-4
    
    Create an agent with a system prompt:
      skogcli agent create assistant --system "You are a helpful assistant."
    """
    # Get existing agents
    agents = get_setting("agent.agents") or []
    
    # Check if agent already exists
    if name in agents:
        console.print(f"[yellow]Agent '{name}' already exists.[/]")
        console.print("Use 'skogcli agent set' to update its configuration.")
        return
    
    # Create agent configuration
    agent_config = {}
    if model:
        agent_config["model"] = model
    if system_prompt:
        agent_config["system_prompt"] = system_prompt
    if description:
        agent_config["description"] = description
    if command_template:
        agent_config["command_template"] = command_template
        
        # Create the agent script
        command = command_template.format(message="{message}")
        create_agent_script(name, command)
    else:
        # Create a default script
        default_cmd = f"echo \"Agent {name} is responding to: {{message}}\""
        create_agent_script(name, default_cmd)
    
    # Save agent configuration
    set_setting(f"agent.{name}", agent_config)
    
    # Add to agents list
    agents.append(name)
    set_setting("agent.agents", agents)
    
    console.print(f"[green]Created agent:[/] {name}")
    console.print(f"Script created at: ./scripts/{name}.sh")

@agent_app.command("set")
@with_explanation("Set a configuration value for an agent.")
def set_agent_config(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Value to set"),
    agent_name: Optional[str] = typer.Option(
        None, "--agent", "-a", 
        help="Agent name (if not included in the key)",
        autocompletion=get_agent_names
    ),
):
    """
    Set a configuration value for an agent.
    
    If the agent name is not included in the key, it must be provided with --agent.
    
    Examples:
    
    Set a model for an agent:
      skogcli agent set model gpt-4 --agent researcher
    
    Set a system prompt:
      skogcli agent set system_prompt "You are a helpful assistant." --agent assistant
    
    Set a configuration directly:
      skogcli agent set agent.coder.model gpt-4
    """
    # Determine the full configuration key
    if key.startswith("agent."):
        # Key already includes the agent prefix
        full_key = key
    elif agent_name:
        # Construct key with agent name
        full_key = f"agent.{agent_name}.{key}"
    else:
        # Neither agent in key nor agent option provided
        console.print("[bold red]Error:[/] Agent name must be provided either in the key or with --agent")
        return
    
    # Try to parse as JSON first (for objects, arrays, etc.)
    try:
        json_value = json.loads(value)
        set_setting(full_key, json_value)
        if isinstance(json_value, dict) or isinstance(json_value, list):
            json_str = json.dumps(json_value, indent=2)
            console.print(f"[green]Set[/] {full_key} = ")
            console.print(json_str)
        else:
            console.print(f"[green]Set[/] {full_key} = {json_value}")
        return
    except json.JSONDecodeError:
        # Not valid JSON, continue with other type conversions
        pass
    
    # Try as int
    try:
        int_value = int(value)
        set_setting(full_key, int_value)
        console.print(f"[green]Set[/] {full_key} = {int_value}")
        return
    except ValueError:
        pass
    
    # Try as float
    try:
        float_value = float(value)
        set_setting(full_key, float_value)
        console.print(f"[green]Set[/] {full_key} = {float_value}")
        return
    except ValueError:
        pass
    
    # Try as boolean
    if value.lower() in ("true", "yes", "1"):
        set_setting(full_key, True)
        console.print(f"[green]Set[/] {full_key} = True")
        return
    elif value.lower() in ("false", "no", "0"):
        set_setting(full_key, False)
        console.print(f"[green]Set[/] {full_key} = False")
        return
    
    # Try as null/None
    if value.lower() in ("null", "none"):
        set_setting(full_key, None)
        console.print(f"[green]Set[/] {full_key} = None")
        return
    
    # Default to string
    set_setting(full_key, value)
    console.print(f"[green]Set[/] {full_key} = \"{value}\"")

@agent_app.command("get")
@with_explanation("Get a configuration value for an agent.")
def get_agent_config(
    key: str = typer.Argument(
        ..., 
        help="Configuration key",
        autocompletion=get_agent_config_keys
    ),
    agent_name: Optional[str] = typer.Option(
        None, "--agent", "-a", 
        help="Agent name (if not included in the key)",
        autocompletion=get_agent_names
    ),
    raw: bool = typer.Option(
        False, "--raw", "-r", 
        help="Output raw value without formatting"
    ),
    json_format: bool = typer.Option(
        False, "--json", "-j", 
        help="Output as formatted JSON"
    ),
):
    """
    Get a configuration value for an agent.
    
    If the agent name is not included in the key, it must be provided with --agent.
    
    Examples:
    
    Get a model for an agent:
      skogcli agent get model --agent researcher
    
    Get a system prompt:
      skogcli agent get system_prompt --agent assistant
    
    Get a configuration directly:
      skogcli agent get agent.coder.model
    """
    # Determine the full configuration key
    if key.startswith("agent."):
        # Key already includes the agent prefix
        full_key = key
    elif agent_name:
        # Construct key with agent name
        full_key = f"agent.{agent_name}.{key}"
    else:
        # Neither agent in key nor agent option provided
        console.print("[bold red]Error:[/] Agent name must be provided either in the key or with --agent")
        return
    
    # Get the value
    value = get_setting(full_key)
    
    if value is None:
        console.print(f"[bold red]Error:[/] Key '{full_key}' not found in configuration.")
        return
    
    # Output as JSON when --json flag is used
    if json_format:
        print(json.dumps(value, indent=2))
        return
    
    # Output raw value when --raw flag is used
    if raw:
        print(value)
    elif isinstance(value, dict) or isinstance(value, list):
        json_str = json.dumps(value, indent=2)
        console.print(f"[bold]{full_key}[/] = ")
        console.print(json_str)
    else:
        console.print(f"[bold]{full_key}[/] = {value}")

@agent_app.command("read")
@with_explanation("Read information about an agent.")
def read_agent(
    name: str = typer.Argument(
        None, 
        help="Name of the agent to read",
        autocompletion=get_agent_names
    ),
    agent_name: str = typer.Option(
        None, "--agent", "-a", 
        help="Name of the agent to read (alternative to NAME argument)",
        autocompletion=get_agent_names
    ),
    raw: bool = typer.Option(
        False, "--raw", "-r", 
        help="Display raw response without formatting"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", 
        help="Output response in JSON format"
    ),
):
    """
    Read information about an agent.
    
    Examples:
    
    Read agent information:
      skogcli agent read default
      
    Read agent using option:
      skogcli agent read --agent default
    
    Get raw output:
      skogcli agent read researcher --raw
    """
    # This is a placeholder implementation that just returns "Hello world"
    # In a real implementation, this would fetch and display agent information
    
    # Use either the argument or the option for the agent name
    agent = agent_name if agent_name is not None else name
    
    # Handle case where neither is provided
    if agent is None:
        console.print("[bold red]Error:[/] Agent name must be provided either as an argument or with --agent")
        raise typer.Exit(1)
    
    # Get agent configuration
    agent_config = get_setting(f"agent.{agent}") or {}
    
    # For now, just return a simple message
    message = f"Hello world from agent: {agent}"
    
    # Display the response
    if json_output:
        output = {
            "agent": agent,
            "message": message,
            "config": agent_config
        }
        print(json.dumps(output, indent=2))
    elif raw:
        print(message)
    else:
        console.print(Panel(
            Markdown(message),
            title=f"Agent: {agent}",
            border_style="blue"
        ))

@agent_app.command("edit-script")
@with_explanation("Edit the script for an agent.")
def edit_agent_script(
    name: str = typer.Argument(
        ..., 
        help="Name of the agent whose script to edit",
        autocompletion=get_agent_names
    ),
):
    """
    Open the agent's script in your default editor.
    
    Examples:
    
    Edit an agent script:
      skogcli agent edit-script researcher
    """
    script_path = get_scripts_dir() / f"{name}.sh"
    
    # Check if the script exists
    if not script_path.exists():
        # Get the command template
        command_template = get_setting(f"agent.{name}.command_template")
        message_template = get_setting(f"agent.{name}.message_template")
        message_setting = get_setting(f"agent.{name}.message")
        
        # Determine the command to use
        if message_setting:
            command = message_setting.format(message="{message}")
        elif command_template:
            command = command_template.format(message="{message}")
        elif message_template:
            command = message_template.format(message="{message}")
        else:
            command = f"echo \"Agent {name} is responding to: {{message}}\""
        
        # Create the script
        create_agent_script(name, command)
        console.print(f"Created script: {script_path}")
    
    # Open the editor
    import subprocess
    editor = os.environ.get("EDITOR", "vim")
    try:
        subprocess.run([editor, script_path])
        console.print(f"[green]Edited script:[/] {script_path}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to open editor: {str(e)}")

@agent_app.command("delete")
@with_explanation("Delete an agent.")
def delete_agent(
    name: str = typer.Argument(
        ..., 
        help="Name of the agent to delete",
        autocompletion=get_agent_names
    ),
    force: bool = typer.Option(
        False, "--force", "-f", 
        help="Delete without confirmation"
    ),
):
    """
    Delete an agent and its configuration.
    
    Examples:
    
    Delete an agent with confirmation:
      skogcli agent delete researcher
    
    Force delete without confirmation:
      skogcli agent delete researcher --force
    """
    # Get existing agents
    agents = get_setting("agent.agents") or []
    
    # Check if agent exists
    if name not in agents:
        console.print(f"[bold red]Error:[/] Agent '{name}' not found.")
        return
    
    # Confirm deletion
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete agent '{name}'?")
        if not confirm:
            console.print("Deletion cancelled.")
            return
    
    # Remove from agents list
    agents.remove(name)
    set_setting("agent.agents", agents)
    
    # Remove agent configuration
    set_setting(f"agent.{name}", None)
    
    # Remove agent script if it exists
    script_path = get_scripts_dir() / f"{name}.sh"
    if script_path.exists():
        script_path.unlink()
        console.print(f"Removed script: {script_path}")
    
    console.print(f"[green]Deleted agent:[/] {name}")
