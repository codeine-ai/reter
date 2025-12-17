"""
Pytest configuration for test suite.
Ensures PyArrow DLLs are available for owl_rete_cpp import on Windows.
"""

import os
import sys

# Add PyArrow DLL directory to PATH on Windows
if sys.platform == 'win32':
    try:
        import pyarrow as pa
        dll_path = pa.get_library_dirs()[0]
        os.add_dll_directory(dll_path)
    except Exception as e:
        print(f"Warning: Could not add PyArrow DLL directory: {e}")
