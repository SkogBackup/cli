---
title: SkogCLI Standards MCP Implementation Plan
type: note
permalink: skog-ai/implementation/skog-cli-standards-mcp-implementation-plan
---

# SkogCLI Standards MCP Implementation Plan

This document outlines the plan for implementing the Standards MCP as a full-fledged MCP service.

## Implementation Roadmap

### Phase 1: Local Standards Module (Current POC)
- Implement the standards registry as a local module
- Define the config_paths standard
- Integrate with the settings module
- Use for validation, normalization, and formatting

### Phase 2: Standalone Standards Service
- Create a dedicated standards service package
- Move standards definitions to a database or JSON files
- Implement a CLI for managing standards
- Add unit tests and documentation

### Phase 3: MCP Standards Service
- Implement the Standards MCP service interface
- Define the MCP tool schema for standards operations
- Create the MCP service implementation
- Implement client libraries for Python and other languages

### Phase 4: Integration and Ecosystem
- Integrate with existing MCP infrastructure
- Implement standards checks in CI/CD pipelines
- Create VS Code and other editor extensions
- Implement a standards dashboard

## Detailed Phase 3 Plan: MCP Standards Service

This section outlines the implementation of the Standards MCP service.

### 1. MCP Tool Schema

```json
{
  "name": "skogai-standards",
  "description": "Standards MCP for managing SkogAI project standards",
  "tools": [
    {
      "name": "get_standard",
      "description": "Get a standard definition by name",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Name of the standard to retrieve"
          }
        },
        "required": ["name"]
      }
    },
    {
      "name": "validate",
      "description": "Validate a value against a standard",
      "parameters": {
        "type": "object",
        "properties": {
          "standard_name": {
            "type": "string",
            "description": "Name of the standard to validate against"
          },
          "value": {
            "description": "Value to validate"
          }
        },
        "required": ["standard_name", "value"]
      }
    },
    {
      "name": "normalize",
      "description": "Normalize a value to comply with a standard",
      "parameters": {
        "type": "object",
        "properties": {
          "standard_name": {
            "type": "string",
            "description": "Name of the standard to normalize for"
          },
          "value": {
            "description": "Value to normalize"
          }
        },
        "required": ["standard_name", "value"]
      }
    },
    {
      "name": "format",
      "description": "Format a value according to a standard format",
      "parameters": {
        "type": "object",
        "properties": {
          "standard_name": {
            "type": "string",
            "description": "Name of the standard to format for"
          },
          "value": {
            "description": "Value to format"
          },
          "format_type": {
            "description": "Format type to use"
          }
        },
        "required": ["standard_name", "value", "format_type"]
      }
    },
    {
      "name": "get_examples",
      "description": "Get examples for a standard",
      "parameters": {
        "type": "object",
        "properties": {
          "standard_name": {
            "type": "string",
            "description": "Name of the standard to get examples for"
          },
          "count": {
            "type": "integer",
            "description": "Maximum number of examples to return"
          }
        },
        "required": ["standard_name"]
      }
    },
    {
      "name": "list_standards",
      "description": "List available standards",
      "parameters": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "description": "Filter by category"
          },
          "scope": {
            "type": "string",
            "description": "Filter by scope"
          }
        }
      }
    },
    {
      "name": "create_standard",
      "description": "Create a new standard",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Name of the standard"
          },
          "description": {
            "type": "string",
            "description": "Description of the standard"
          },
          "category": {
            "type": "string",
            "description": "Category of the standard"
          },
          "scope": {
            "type": "string",
            "description": "Scope of the standard"
          },
          "definition": {
            "type": "object",
            "description": "Standard definition"
          },
          "examples": {
            "type": "array",
            "description": "Examples for the standard"
          }
        },
        "required": ["name", "description", "category", "definition"]
      }
    },
    {
      "name": "update_standard",
      "description": "Update an existing standard",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Name of the standard to update"
          },
          "updates": {
            "type": "object",
            "description": "Updates to apply to the standard"
          }
        },
        "required": ["name", "updates"]
      }
    }
  ]
}
```

### 2. MCP Service Implementation

```python
# skogai_standards/mcp_service.py

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from mcp import MCPService
from .standards_registry import StandardsRegistry, Standard

class StandardsMCPService(MCPService):
    """MCP service for managing standards."""
    
    def __init__(self):
        """Initialize the service."""
        super().__init__("skogai-standards")
        self.registry = StandardsRegistry()
        self.load_standards()
    
    def load_standards(self):
        """Load standards from the registry."""
        # Load from database or file
    
    async def get_standard(self, request):
        """Get a standard by name."""
        name = request.args.get("name")
        standard = self.registry.get(name)
        if not standard:
            return {"error": f"Standard not found: {name}"}
        
        return {
            "name": standard.name,
            "description": standard.description,
            "definition": standard.definition,
            "examples": standard.examples,
            "metadata": standard.metadata
        }
    
    async def validate(self, request):
        """Validate a value against a standard."""
        standard_name = request.args.get("standard_name")
        value = request.args.get("value")
        
        try:
            result = self.registry.validate(standard_name, value)
            return {"valid": result}
        except ValueError as e:
            return {"error": str(e), "valid": False}
    
    async def normalize(self, request):
        """Normalize a value to comply with a standard."""
        standard_name = request.args.get("standard_name")
        value = request.args.get("value")
        
        try:
            result = self.registry.normalize(standard_name, value)
            return {"normalized": result}
        except ValueError as e:
            return {"error": str(e)}
    
    async def format(self, request):
        """Format a value according to a standard format."""
        standard_name = request.args.get("standard_name")
        value = request.args.get("value")
        format_type = request.args.get("format_type")
        
        try:
            result = self.registry.format(standard_name, value, format_type)
            return {"formatted": result}
        except ValueError as e:
            return {"error": str(e)}
    
    async def get_examples(self, request):
        """Get examples for a standard."""
        standard_name = request.args.get("standard_name")
        count = request.args.get("count")
        
        try:
            examples = self.registry.get_examples(standard_name, count)
            return {"examples": examples}
        except ValueError as e:
            return {"error": str(e)}
    
    async def list_standards(self, request):
        """List available standards."""
        category = request.args.get("category")
        scope = request.args.get("scope")
        
        standards = []
        for name, standard in self.registry.standards.items():
            if (category and standard.metadata.get("category") != category) or \
               (scope and standard.metadata.get("scope") != scope):
                continue
            
            standards.append({
                "name": standard.name,
                "description": standard.description,
                "category": standard.metadata.get("category"),
                "scope": standard.metadata.get("scope")
            })
        
        return {"standards": standards}
    
    async def create_standard(self, request):
        """Create a new standard."""
        name = request.args.get("name")
        description = request.args.get("description")
        category = request.args.get("category")
        scope = request.args.get("scope")
        definition = request.args.get("definition")
        examples = request.args.get("examples", [])
        
        # Check if standard already exists
        if self.registry.get(name):
            return {"error": f"Standard already exists: {name}"}
        
        # Create and register the standard
        standard = Standard(
            name=name,
            description=description,
            definition=definition,
            examples=examples,
            metadata={
                "category": category,
                "scope": scope,
                "created_at": datetime.now().isoformat()
            }
        )
        
        self.registry.register(standard)
        
        return {"success": True, "standard": name}
    
    async def update_standard(self, request):
        """Update an existing standard."""
        name = request.args.get("name")
        updates = request.args.get("updates", {})
        
        # Check if standard exists
        standard = self.registry.get(name)
        if not standard:
            return {"error": f"Standard not found: {name}"}
        
        # Update the standard
        for key, value in updates.items():
            if key == "name":
                # Name changes are not allowed
                continue
            elif key == "metadata":
                # Merge metadata
                standard.metadata.update(value)
            elif hasattr(standard, key):
                setattr(standard, key, value)
        
        # Update metadata
        standard.metadata["updated_at"] = datetime.now().isoformat()
        
        return {"success": True, "standard": name}

# Start the service
if __name__ == "__main__":
    service = StandardsMCPService()
    service.run()
```

### 3. Python Client Library

```python
# skogai_standards/client.py

from typing import Any, Dict, List, Optional, Union
from mcp import MCPClient

class StandardsClient:
    """Client for the Standards MCP service."""
    
    def __init__(self):
        """Initialize the client."""
        self.client = MCPClient("skogai-standards")
    
    def get_standard(self, name: str) -> Dict:
        """Get a standard by name."""
        response = self.client.call("get_standard", {"name": name})
        if "error" in response:
            raise ValueError(response["error"])
        return response
    
    def validate(self, standard_name: str, value: Any) -> bool:
        """Validate a value against a standard."""
        response = self.client.call("validate", {
            "standard_name": standard_name,
            "value": value
        })
        if "error" in response:
            raise ValueError(response["error"])
        return response["valid"]
    
    def normalize(self, standard_name: str, value: Any) -> Any:
        """Normalize a value to comply with a standard."""
        response = self.client.call("normalize", {
            "standard_name": standard_name,
            "value": value
        })
        if "error" in response:
            raise ValueError(response["error"])
        return response["normalized"]
    
    def format(self, standard_name: str, value: Any, format_type: Any) -> Any:
        """Format a value according to a standard format."""
        response = self.client.call("format", {
            "standard_name": standard_name,
            "value": value,
            "format_type": format_type
        })
        if "error" in response:
            raise ValueError(response["error"])
        return response["formatted"]
    
    def get_examples(self, standard_name: str, count: Optional[int] = None) -> List[Dict]:
        """Get examples for a standard."""
        params = {"standard_name": standard_name}
        if count is not None:
            params["count"] = count
            
        response = self.client.call("get_examples", params)
        if "error" in response:
            raise ValueError(response["error"])
        return response["examples"]
    
    def list_standards(self, category: Optional[str] = None, scope: Optional[str] = None) -> List[Dict]:
        """List available standards."""
        params = {}
        if category:
            params["category"] = category
        if scope:
            params["scope"] = scope
            
        response = self.client.call("list_standards", params)
        return response["standards"]
    
    def create_standard(self, name: str, description: str, definition: Dict,
                        category: Optional[str] = None, scope: Optional[str] = None,
                        examples: Optional[List[Dict]] = None) -> Dict:
        """Create a new standard."""
        params = {
            "name": name,
            "description": description,
            "definition": definition
        }
        
        if category:
            params["category"] = category
        if scope:
            params["scope"] = scope
        if examples:
            params["examples"] = examples
            
        response = self.client.call("create_standard", params)
        if "error" in response:
            raise ValueError(response["error"])
        return response
    
    def update_standard(self, name: str, updates: Dict) -> Dict:
        """Update an existing standard."""
        response = self.client.call("update_standard", {
            "name": name,
            "updates": updates
        })
        if "error" in response:
            raise ValueError(response["error"])
        return response
```

### 4. CLI Tool

```python
# skogai_standards/cli.py

import argparse
import json
import sys
from typing import Any, Dict, List, Optional
from .client import StandardsClient

def main():
    """Run the Standards CLI."""
    parser = argparse.ArgumentParser(description="Standards MCP CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # get-standard command
    get_parser = subparsers.add_parser("get-standard", help="Get a standard by name")
    get_parser.add_argument("name", help="Name of the standard to retrieve")
    
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a value against a standard")
    validate_parser.add_argument("standard", help="Name of the standard to validate against")
    validate_parser.add_argument("value", help="Value to validate")
    
    # normalize command
    normalize_parser = subparsers.add_parser("normalize", help="Normalize a value to comply with a standard")
    normalize_parser.add_argument("standard", help="Name of the standard to normalize for")
    normalize_parser.add_argument("value", help="Value to normalize")
    
    # format command
    format_parser = subparsers.add_parser("format", help="Format a value according to a standard format")
    format_parser.add_argument("standard", help="Name of the standard to format for")
    format_parser.add_argument("value", help="Value to format")
    format_parser.add_argument("format_type", help="Format type to use")
    
    # get-examples command
    examples_parser = subparsers.add_parser("get-examples", help="Get examples for a standard")
    examples_parser.add_argument("standard", help="Name of the standard to get examples for")
    examples_parser.add_argument("--count", type=int, help="Maximum number of examples to return")
    
    # list-standards command
    list_parser = subparsers.add_parser("list-standards", help="List available standards")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--scope", help="Filter by scope")
    
    # create-standard command
    create_parser = subparsers.add_parser("create-standard", help="Create a new standard")
    create_parser.add_argument("name", help="Name of the standard")
    create_parser.add_argument("description", help="Description of the standard")
    create_parser.add_argument("--definition-file", help="Path to definition file")
    create_parser.add_argument("--category", help="Category of the standard")
    create_parser.add_argument("--scope", help="Scope of the standard")
    create_parser.add_argument("--examples-file", help="Path to examples file")
    
    # update-standard command
    update_parser = subparsers.add_parser("update-standard", help="Update an existing standard")
    update_parser.add_argument("name", help="Name of the standard to update")
    update_parser.add_argument("--updates-file", help="Path to updates file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = StandardsClient()
    
    try:
        if args.command == "get-standard":
            result = client.get_standard(args.name)
            print(json.dumps(result, indent=2))
            
        elif args.command == "validate":
            result = client.validate(args.standard, args.value)
            print(f"Valid: {result}")
            
        elif args.command == "normalize":
            result = client.normalize(args.standard, args.value)
            print(f"Normalized: {result}")
            
        elif args.command == "format":
            result = client.format(args.standard, args.value, args.format_type)
            print(f"Formatted: {result}")
            
        elif args.command == "get-examples":
            result = client.get_examples(args.standard, args.count)
            print(json.dumps(result, indent=2))
            
        elif args.command == "list-standards":
            result = client.list_standards(args.category, args.scope)
            print(json.dumps(result, indent=2))
            
        elif args.command == "create-standard":
            # Load definition from file
            if args.definition_file:
                with open(args.definition_file, "r") as f:
                    definition = json.load(f)
            else:
                definition = {}
            
            # Load examples from file
            examples = None
            if args.examples_file:
                with open(args.examples_file, "r") as f:
                    examples = json.load(f)
            
            result = client.create_standard(
                args.name,
                args.description,
                definition,
                args.category,
                args.scope,
                examples
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == "update-standard":
            # Load updates from file
            if args.updates_file:
                with open(args.updates_file, "r") as f:
                    updates = json.load(f)
            else:
                updates = {}
            
            result = client.update_standard(args.name, updates)
            print(json.dumps(result, indent=2))
            
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Migration Path

### 1. From Local Module to MCP Service

To migrate from the local standards module to the MCP service:

```python
# Before: Using local standards module
from src.skogcli.standards import standards

if standards.validate("config_paths", user_input):
    # Process the input
    
# After: Using MCP client
from skogai_standards.client import StandardsClient

standards = StandardsClient()

if standards.validate("config_paths", user_input):
    # Process the input
```

The API remains the same, so switching should be seamless.

### 2. Integration Testing

During migration, we can run both implementations in parallel to ensure they behave identically:

```python
def test_standards_compatibility():
    """Test that local and MCP implementations behave the same."""
    from src.skogcli.standards import standards as local_standards
    from skogai_standards.client import StandardsClient
    
    mcp_standards = StandardsClient()
    
    test_cases = [
        "memory.page_size",
        "memory://page_size",
        "memory-page-size",
        "memory_page_size",
        "invalid.format"
    ]
    
    for case in test_cases:
        local_result = local_standards.validate("config_paths", case)
        mcp_result = mcp_standards.validate("config_paths", case)
        assert local_result == mcp_result
```

## Benefits of the Full MCP Implementation

1. **Service-Oriented Architecture**:
   - Standards available across multiple projects
   - Centralized management of standards
   - Versioning and history tracking

2. **Language-Agnostic Interface**:
   - Accessible from any language via MCP clients
   - Consistent behavior across implementations
   - Standardized error handling

3. **Advanced Features**:
   - Schema validation for standards definitions
   - User permissions and role-based access
   - Import/export capabilities
   - Notifications of standard changes

4. **Integration Capabilities**:
   - CI/CD pipeline integration
   - Editor plugin support
   - Documentation generation
   - Standards compliance reporting

5. **Extensibility**:
   - Support for more complex standard types
   - Custom validation and normalization functions
   - Project-specific standard extensions
   - Inheritance and composition of standards

This implementation plan provides a clear path from the current proof-of-concept to a full-fledged MCP service, ensuring consistency and standards compliance across the SkogAI ecosystem.