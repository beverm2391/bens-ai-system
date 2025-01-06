"""Tests for the toolbox and tool decorator."""
import pytest
from src.agents.toolbox import Tool, Toolbox, register_tool

def test_tool_import_detection():
    def tool_with_imports():
        import json
        from datetime import datetime
        return json.dumps({"time": str(datetime.now())})
    
    tool = Tool(name="json_tool", func=tool_with_imports, description="Test tool")
    assert tool.required_imports == {"json", "datetime"}

def test_tool_no_imports():
    def simple_tool(x, y):
        return x + y
    
    tool = Tool(name="add", func=simple_tool, description="Add numbers")
    assert tool.required_imports == set()

def test_register_tool_decorator():
    toolbox = Toolbox()
    toolbox.tools.clear()  # Clean start
    
    @register_tool(description="Test tool")
    def decorated_tool():
        import math
        return math.pi
    
    tool = toolbox.get_tool("decorated_tool")
    assert tool is not None
    assert tool.name == "decorated_tool"
    assert tool.description == "Test tool"
    assert tool.required_imports == {"math"}
    
    # Cleanup
    toolbox.tools.clear()

def test_toolbox_singleton():
    toolbox1 = Toolbox()
    toolbox2 = Toolbox()
    toolbox1.tools.clear()  # Clean start
    assert toolbox1 is toolbox2
    
    @register_tool
    def tool1(): pass
    
    assert "tool1" in toolbox2.tools
    
    # Cleanup
    toolbox1.tools.clear()

def test_get_required_imports():
    toolbox = Toolbox()
    toolbox.tools.clear()  # Clean start
    
    def tool1():
        import os
        import sys
        return os.getcwd()
    
    def tool2():
        from datetime import datetime
        import json
        return json.dumps({"now": str(datetime.now())})
    
    toolbox.add_tool(Tool(name="tool1", func=tool1, description="Tool 1"))
    toolbox.add_tool(Tool(name="tool2", func=tool2, description="Tool 2"))
    
    required_imports = toolbox.get_required_imports()
    assert required_imports == {"os", "sys", "datetime", "json"}
    
    # Cleanup
    toolbox.tools.clear()

def test_tool_redefinition():
    toolbox = Toolbox()
    
    def tool1():
        import os
        return os.getcwd()
    
    def tool1_new():
        import sys
        return sys.version
    
    toolbox.add_tool(Tool(name="tool1", func=tool1, description="Original"))
    toolbox.add_tool(Tool(name="tool1", func=tool1_new, description="New"))
    
    assert toolbox.get_tool("tool1").required_imports == {"sys"}

def test_get_nonexistent_tool():
    toolbox = Toolbox()
    assert toolbox.get_tool("nonexistent") is None

def test_code_validation():
    def safe_tool(x, y):
        return x + y
    
    def unsafe_tool():
        exec("print('hello')")  # This should be caught
        return True
    
    def file_operation_tool():
        with open('test.txt', 'w') as f:  # This should be caught
            f.write('test')
    
    def subprocess_tool():
        import subprocess  # This should be caught
        subprocess.run(['ls'])
    
    # Test safe tool
    tool = Tool(name="safe", func=safe_tool, description="Safe tool")
    is_valid, msg = tool.validate_code()
    assert is_valid is True
    assert msg == ""
    
    # Test exec usage
    tool = Tool(name="unsafe", func=unsafe_tool, description="Unsafe tool")
    is_valid, msg = tool.validate_code()
    assert is_valid is False
    assert "exec" in msg.lower()
    
    # Test file operations
    tool = Tool(name="file_op", func=file_operation_tool, description="File operation tool")
    is_valid, msg = tool.validate_code()
    assert is_valid is False
    assert "file operations" in msg.lower()
    
    # Test subprocess usage
    tool = Tool(name="subprocess", func=subprocess_tool, description="Subprocess tool")
    is_valid, msg = tool.validate_code()
    assert is_valid is False
    assert "subprocess" in msg.lower()