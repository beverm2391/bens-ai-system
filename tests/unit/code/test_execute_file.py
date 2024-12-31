import pytest
from pathlib import Path
from src.e2b.execute_file import execute_file

@pytest.fixture
def temp_code_file(tmp_path):
    code_file = tmp_path / "test.py"
    code_file.write_text('print("hello from file")')
    return str(code_file)

@pytest.fixture
def temp_error_file(tmp_path):
    error_file = tmp_path / "error.py"
    error_file.write_text('print(undefined_var)')
    return str(error_file)

def test_execute_file_success(temp_code_file):
    stdout, stderr = execute_file(temp_code_file)
    assert stdout.strip() == "hello from file"
    assert not stderr

def test_execute_file_error(temp_error_file):
    stdout, stderr = execute_file(temp_error_file)
    assert not stdout
    assert "NameError" in stderr

def test_execute_file_not_found():
    with pytest.raises(FileNotFoundError):
        execute_file("nonexistent.py") 