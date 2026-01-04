"""Test for Python syntax errors across all Python files."""
import py_compile
import sys
from pathlib import Path


def test_all_python_files_have_valid_syntax():
    """Check that all Python files in the project have valid syntax."""
    project_root = Path(__file__).parent.parent
    
    # Scan all Python files, excluding cache and virtual environment directories
    python_files = [
        f for f in project_root.rglob("*.py")
        if "__pycache__" not in str(f) and ".pyenv" not in str(f) and "venv" not in str(f)
    ]
    
    assert len(python_files) > 0, "No Python files found in project"
    
    errors = []
    for filepath in python_files:
        try:
            py_compile.compile(str(filepath), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{filepath}: {e}")
    
    if errors:
        error_message = "Syntax errors found in the following files:\n" + "\n".join(errors)
        raise AssertionError(error_message)
