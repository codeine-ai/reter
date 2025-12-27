"""
RETER - High-performance Description Logic reasoner with C++ RETE engine

This package provides:
- Fast OWL 2 RL reasoning using C++ RETE algorithm
- Description Logic parser (C++ implementation)
- SWRL rule support
- Query interface with Arrow integration
- Source tracking for incremental ontology loading
- Binary serialization for fast loading
"""

__version__ = "0.1.1"

# Import main reasoner class when package is imported
from reter.reasoner import Reter, QueryResultSet

# Re-export owl_rete_cpp from reter_core for backwards compatibility
from reter_core import owl_rete_cpp

def get_version_info():
    """
    Get comprehensive version information for debugging.

    Returns:
        dict: Version info including:
            - python_package: Python package version
            - cpp_binding: C++ binding version and build timestamp
            - optional_fix: Whether OPTIONAL column rename fix is present
    """
    cpp_info = owl_rete_cpp.get_version_info()
    return {
        "python_package": __version__,
        "cpp_binding": {
            "version": getattr(owl_rete_cpp, "__version__", "unknown"),
            "build_timestamp": getattr(owl_rete_cpp, "__build_timestamp__", "unknown"),
        },
        "cpp_version_info": cpp_info,
        "optional_fix": cpp_info.get("optional_fix", False),
    }

__all__ = ['Reter', 'QueryResultSet', '__version__', 'get_version_info']
