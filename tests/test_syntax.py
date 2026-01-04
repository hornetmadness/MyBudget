"""Test for Python syntax errors across all Python files."""
import py_compile
import sys
from pathlib import Path


def test_all_python_files_have_valid_syntax():
    """Check that all Python files in the app directory have valid syntax."""
    app_dir = Path(__file__).parent.parent / "app"
    python_files = list(app_dir.rglob("*.py"))
    
    assert len(python_files) > 0, "No Python files found in app directory"
    
    errors = []
    for filepath in python_files:
        try:
            py_compile.compile(str(filepath), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{filepath}: {e}")
    
    if errors:
        error_message = "Syntax errors found in the following files:\n" + "\n".join(errors)
        raise AssertionError(error_message)
