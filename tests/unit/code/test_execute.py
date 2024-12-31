import pytest
from src.e2b.execute import execute_code

def test_execute_code_success():
    code = 'print("hello")'
    stdout, stderr = execute_code(code)
    assert stdout.strip() == "hello"
    assert not stderr

def test_execute_code_error():
    code = 'print(undefined_var)'
    stdout, stderr = execute_code(code)
    assert not stdout
    assert "NameError" in stderr

def test_execute_code_syntax_error():
    code = 'print("hello'  # Missing closing quote
    stdout, stderr = execute_code(code)
    assert not stdout
    assert "SyntaxError" in stderr 