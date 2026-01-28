import os
import sys

def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: Path relative to the project root.
        
    Returns:
        Absolute path to the resource.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except (AttributeError, Exception):
        # Fallback for development mode: navigate up from core/engine/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)

def get_tool_definition_path(tool_name: str) -> str:
    """
    Finds the YAML definition file for a given tool by searching in definitions/.
    
    Args:
        tool_name: Name of the tool (e.g., 'borgmatic').
        
    Returns:
        Absolute path to the YAML file or None if not found.
    """
    definitions_path = get_resource_path("definitions")
    
    if not os.path.exists(definitions_path):
        return None

    for root, _, files in os.walk(definitions_path):
        if f"{tool_name.lower()}.yaml" in files:
            return os.path.join(root, f"{tool_name.lower()}.yaml")
            
    return None
