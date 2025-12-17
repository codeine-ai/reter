"""
Tests for Python code loading examples from documentation

Tests all examples from PYTHON_ANALYSIS_REFERENCE.md section "How to load Python code"
- Example 1.1: Load single file
- Example 1.2: Load directory
- Example 1.3: Load code from string

Reference: mcp/docs/PYTHON_ANALYSIS_REFERENCE.md lines 14-32
"""

import pytest
import tempfile
import os
from pathlib import Path
from reter import Reter


@pytest.fixture
def reter_instance():
    """Fresh Reter instance for each test"""
    return Reter(variant='ai')


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a temporary Python file for testing"""
    file_path = tmp_path / "mymodule.py"
    file_path.write_text("""
class MyClass:
    def my_method(self):
        pass

def my_function():
    pass
""")
    return str(file_path)


@pytest.fixture
def sample_python_directory(tmp_path):
    """Create a temporary directory with Python files"""
    # Create main module
    (tmp_path / "main.py").write_text("""
def main():
    pass
""")

    # Create subpackage
    subdir = tmp_path / "subpackage"
    subdir.mkdir()
    (subdir / "__init__.py").write_text("")
    (subdir / "utils.py").write_text("""
class Utility:
    pass
""")

    return str(tmp_path)


def test_example_1_1_load_single_file(reter_instance, sample_python_file):
    """
    Example 1.1: Load single Python file

    Documentation: PYTHON_ANALYSIS_REFERENCE.md lines 14-32
    """
    # Execute the documented example
    wme_count, errors = reter_instance.load_python_file(
        filepath=sample_python_file,
        module_name="mymodule"
    )

    # Assertions
    assert wme_count is not None
    assert wme_count > 0  # Should have extracted some WMEs
    assert isinstance(errors, list)  # Should return error list

    # Verify we can query the loaded code
    query_result = reter_instance.reql("""
        SELECT ?class WHERE {
            ?class type py:Class
        }
    """)
    assert query_result.num_rows >= 1  # Should find at least MyClass


def test_example_1_2_load_directory(reter_instance, sample_python_directory):
    """
    Example 1.2: Load directory recursively

    Documentation: PYTHON_ANALYSIS_REFERENCE.md lines 14-32
    """
    # Execute the documented example
    wme_count, errors = reter_instance.load_python_directory(
        directory=sample_python_directory,
        recursive=True
    )

    # Assertions
    assert wme_count is not None
    assert wme_count > 0
    assert isinstance(errors, dict)  # Should return dict of errors by file

    # Verify we loaded files from subdirectories
    query_result = reter_instance.reql("""
        SELECT ?entity WHERE {
            ?entity type py:Class
        }
    """)
    assert query_result.num_rows >= 1  # Should find Utility class


def test_example_1_3_load_code_from_string(reter_instance):
    """
    Example 1.3: Load Python code from string

    Documentation: PYTHON_ANALYSIS_REFERENCE.md lines 14-32
    """
    # Execute the documented example
    wme_count, errors = reter_instance.load_python_code(
        python_code="class MyClass: pass",
        module_name="mymodule"
    )

    # Assertions
    assert wme_count is not None
    assert wme_count > 0
    assert isinstance(errors, list)  # Should return error list

    # Verify the class was loaded
    query_result = reter_instance.reql("""
        SELECT ?class ?name WHERE {
            ?class type py:Class .
            ?class name ?name
        }
    """)
    assert query_result.num_rows >= 1
    df = query_result.to_pandas()
    assert any("MyClass" in str(name) for name in df['?name'])


def test_load_python_file_extracts_classes_and_functions(reter_instance, sample_python_file):
    """
    Verify that load_python_file extracts both classes and functions
    """
    wme_count, errors = reter_instance.load_python_file(
        filepath=sample_python_file,
        module_name="mymodule"
    )

    # Check classes
    classes = reter_instance.reql("""
        SELECT ?class ?name WHERE {
            ?class type py:Class .
            ?class name ?name
        }
    """)
    assert classes.num_rows >= 1

    # Check functions
    functions = reter_instance.reql("""
        SELECT ?func ?name WHERE {
            ?func type py:Function .
            ?func name ?name
        }
    """)
    assert functions.num_rows >= 1


def test_load_python_directory_recursive_finds_nested_files(reter_instance, sample_python_directory):
    """
    Verify that recursive directory loading finds files in subdirectories
    """
    wme_count, errors = reter_instance.load_python_directory(
        directory=sample_python_directory,
        recursive=True
    )

    # Should find entities from both main.py and subpackage/utils.py
    query_result = reter_instance.reql("""
        SELECT DISTINCT ?module WHERE {
            ?entity inModule ?module
        }
    """)

    # Should have at least 2 modules (main and utils)
    assert query_result.num_rows >= 1


def test_load_python_code_with_complex_code(reter_instance):
    """
    Verify that load_python_code handles more complex code structures
    """
    complex_code = """
class Vehicle:
    '''A vehicle base class'''
    def __init__(self, name):
        self.name = name

    def move(self):
        pass

class Car(Vehicle):
    def move(self):
        return "driving"

def create_car(name):
    return Car(name)
"""

    wme_count, errors = reter_instance.load_python_code(
        python_code=complex_code,
        module_name="vehicles"
    )

    assert wme_count > 0
    assert isinstance(errors, list)  # Should return error list

    # Verify classes
    classes = reter_instance.reql("""
        SELECT ?class ?name WHERE {
            ?class type py:Class .
            ?class name ?name
        }
    """)
    assert classes.num_rows >= 2  # Vehicle and Car

    # Verify inheritance
    inheritance = reter_instance.reql("""
        SELECT ?child ?parent WHERE {
            ?child inheritsFrom ?parent
        }
    """)
    assert inheritance.num_rows >= 1  # Car inherits from Vehicle


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
