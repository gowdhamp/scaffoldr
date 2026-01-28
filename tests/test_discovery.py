import os
import pytest
from core.discovery import discover_tools

def test_discover_tools(tmp_path):
    # Simulating a definitions directory
    defs = tmp_path / "definitions"
    defs.mkdir()
    
    backup = defs / "backup"
    backup.mkdir()
    
    borg = backup / "borgmatic"
    borg.mkdir()
    (borg / "borgmatic.yaml").write_text("heading: {}")
    
    # We need to mock get_resource_path or set it up correctly
    # For simplicity, we'll just check if the logic works when pointed correctly
    
    import core.discovery
    original_get_resource_path = core.discovery.get_resource_path
    core.discovery.get_resource_path = lambda x: str(tmp_path / x)
    
    try:
        tools = discover_tools()
        assert "backup" in tools
        assert "borgmatic" in tools["backup"]
    finally:
        core.discovery.get_resource_path = original_get_resource_path
