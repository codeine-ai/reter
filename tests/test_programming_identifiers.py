#!/usr/bin/env python3
"""
Test suite for programming language identifier support via variant="ai" parameter.
Validates identifiers from C++, Python, Java, C#, and JavaScript.
"""

import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from reter import owl_rete_cpp


class TestProgrammingIdentifiers(unittest.TestCase):
    """Test identifier patterns from various programming languages using variant='ai'."""

    def assert_parses(self, ontology_text):
        """Assert that ontology text parses successfully with AI variant."""
        net = owl_rete_cpp.ReteNetwork()
        try:
            wme_count = net.load_ontology_from_string(ontology_text, variant="ai")
            self.assertGreater(wme_count, 0, f"No WMEs created for: {ontology_text}")
        except Exception as e:
            self.fail(f"Failed to parse with AI variant: {ontology_text}\nError: {e}")

    # ============================================
    # C++ IDENTIFIERS
    # ============================================

    def test_cpp_namespaces(self):
        """Test C++ namespace identifiers."""
        cpp_ids = [
            "std::vector",
            "std::chrono::seconds",
            "boost::filesystem::path",
            "my_namespace::MyClass",
            "detail::impl::internal::Helper",
        ]
        for id_text in cpp_ids:
            with self.subTest(cpp_id=id_text):
                self.assert_parses(f"{id_text} is_subclass_of Type")

    def test_cpp_special_names(self):
        """Test C++ special naming patterns."""
        cpp_special = [
            "_Reserved",
            "__cplusplus",
            "m_memberVariable",
            "g_globalVariable",
            "s_staticMember",
            "k_constantValue",
        ]
        for id_text in cpp_special:
            with self.subTest(cpp_special=id_text):
                self.assert_parses(f"{id_text} is_subclass_of Thing")

    def test_cpp_not_supported(self):
        """Test C++ patterns that require quoting with backticks."""
        # These should be quoted to work as single identifiers
        cpp_complex = [
            "std::vector<int>",           # Templates
            "std::array<int, 10>",        # Multi-param templates
            "operator++",                 # Operators
            "*pointer",                   # Pointers
            "&reference",                 # References
        ]
        for id_text in cpp_complex:
            with self.subTest(cpp_complex=id_text):
                # Use backticks for quoting in AI variant
                self.assert_parses(f'`{id_text}` is_a ComplexIdentifier')

    # ============================================
    # PYTHON IDENTIFIERS
    # ============================================

    def test_python_modules(self):
        """Test Python module path identifiers."""
        python_modules = [
            "os.path",
            "numpy.ndarray",
            "pandas.DataFrame",
            "django.contrib.auth.models",
            "my_package.my_module.MyClass",
        ]
        for id_text in python_modules:
            with self.subTest(python_module=id_text):
                self.assert_parses(f"{id_text} is_subclass_of Module")

    def test_python_naming_conventions(self):
        """Test Python naming conventions."""
        python_names = [
            "_private",
            "__dunder__",
            "__init__",
            "__name__",
            "_single_leading_underscore",
            "snake_case_function",
            "CONSTANT_VALUE",
            "@decorator",  # Decorator syntax
            # Note: #tag is treated as a comment in AI variant
        ]
        for id_text in python_names:
            with self.subTest(python_name=id_text):
                self.assert_parses(f"{id_text} is_a Identifier")

    def test_python_not_supported(self):
        """Test Python patterns that require quoting with backticks."""
        python_complex = [
            "func()",               # Function calls
            "obj.method()",         # Method calls
            "**kwargs",             # Keyword args
            "*args",                # Variable args
        ]
        for id_text in python_complex:
            with self.subTest(python_complex=id_text):
                # Use backticks for quoting in AI variant
                self.assert_parses(f'`{id_text}` is_a ComplexIdentifier')

    # ============================================
    # JAVA IDENTIFIERS
    # ============================================

    def test_java_packages(self):
        """Test Java package identifiers."""
        java_packages = [
            "java.lang.String",
            "java.util.ArrayList",
            "com.example.myapp.MainActivity",
            "org.apache.commons.lang3.StringUtils",
            "javax.servlet.http.HttpServletRequest",
        ]
        for id_text in java_packages:
            with self.subTest(java_package=id_text):
                # Object is a reserved keyword, must escape it with backticks
                self.assert_parses(f"{id_text} is_subclass_of `Object`")

    def test_java_inner_classes(self):
        """Test Java inner class notation."""
        java_inner = [
            "OuterClass$InnerClass",
            "Package$Class$Nested$Deep",
            "MyClass$Builder",
            # Note: Can't use $1 style - digits can't follow $ separator
        ]
        for id_text in java_inner:
            with self.subTest(java_inner=id_text):
                self.assert_parses(f"{id_text} is_subclass_of Class")

    def test_java_annotations(self):
        """Test Java annotation identifiers."""
        java_annotations = [
            "@Override",
            "@Deprecated",
            "@SuppressWarnings",
            "@FunctionalInterface",
            "@Entity",
        ]
        for id_text in java_annotations:
            with self.subTest(java_annotation=id_text):
                self.assert_parses(f"{id_text} is_a Annotation")

    def test_java_not_supported(self):
        """Test Java patterns that require quoting with backticks."""
        java_complex = [
            "List<String>",                 # Generics
            "Map<String, Integer>",         # Multi-type generics
            "array[0]",                     # Array access
            "Class::method",                # Method reference
            "package.*",                    # Wildcard import
        ]
        for id_text in java_complex:
            with self.subTest(java_complex=id_text):
                # Use backticks for quoting in AI variant
                self.assert_parses(f'`{id_text}` is_a ComplexIdentifier')

    # ============================================
    # C# IDENTIFIERS
    # ============================================

    def test_csharp_namespaces(self):
        """Test C# namespace identifiers."""
        csharp_namespaces = [
            "System.String",
            "System.Collections.Generic",
            "Microsoft.AspNetCore.Mvc",
            "MyCompany.MyApp.Models.User",
            "System.Threading.Tasks.Task",
        ]
        for id_text in csharp_namespaces:
            with self.subTest(csharp_namespace=id_text):
                self.assert_parses(f"{id_text} is_subclass_of Type")

    def test_csharp_verbatim(self):
        """Test C# verbatim identifiers."""
        csharp_verbatim = [
            "@class",      # Keyword as identifier
            "@if",
            "@foreach",
            "@event",
        ]
        for id_text in csharp_verbatim:
            with self.subTest(csharp_verbatim=id_text):
                self.assert_parses(f"{id_text} is_a Identifier")

    def test_csharp_not_supported(self):
        """Test C# patterns that require quoting with backticks."""
        csharp_complex = [
            "List<T>",                      # Generics
            "Dictionary<K, V>",             # Multiple type params
            "array[index]",                 # Indexers
            "obj?.Property",                # Null-conditional
            "Class+NestedClass",            # Nested class syntax
        ]
        for id_text in csharp_complex:
            with self.subTest(csharp_complex=id_text):
                # Use backticks for quoting in AI variant
                self.assert_parses(f'`{id_text}` is_a ComplexIdentifier')

    # ============================================
    # JAVASCRIPT IDENTIFIERS
    # ============================================

    def test_javascript_special_prefixes(self):
        """Test JavaScript special prefix identifiers."""
        js_prefixes = [
            # Note: $ is reserved as CUR token in AI variant
            "$jquery",
            "$$angular",
            "_lodash",
            "__core__",
            # Note: #privateField would be treated as a comment
        ]
        for id_text in js_prefixes:
            with self.subTest(js_prefix=id_text):
                self.assert_parses(f"{id_text} is_a Variable")

    def test_javascript_module_patterns(self):
        """Test JavaScript module patterns."""
        js_modules = [
            "module.exports",
            "React.Component",
            "window.document.body",
            "process.env.NODE_ENV",
            "express.Router",
        ]
        for id_text in js_modules:
            with self.subTest(js_module=id_text):
                self.assert_parses(f"{id_text} is_a Module")

    def test_javascript_naming_styles(self):
        """Test JavaScript naming conventions."""
        js_names = [
            "camelCase",
            "PascalCase",
            "CONSTANT_VALUE",
            "_privateVar",
            "$specialVar",
            "my_snake_case",  # Less common but valid
        ]
        for id_text in js_names:
            with self.subTest(js_name=id_text):
                self.assert_parses(f"{id_text} is_a Variable")

    def test_javascript_not_supported(self):
        """Test JavaScript patterns that require quoting with backticks."""
        js_complex = [
            "array[0]",                     # Array access
            "obj['property']",              # Bracket notation
            "func()",                       # Function calls
            "obj?.prop",                    # Optional chaining
            "...spread",                    # Spread operator
            "import * as name",             # Import syntax
        ]
        for id_text in js_complex:
            with self.subTest(js_complex=id_text):
                # Use backticks for quoting in AI variant
                self.assert_parses(f'`{id_text}` is_a ComplexIdentifier')

    # ============================================
    # CROSS-LANGUAGE PATTERNS
    # ============================================

    def test_cross_language_common(self):
        """Test identifiers common across languages."""
        common = [
            "MyClass",
            "myVariable",
            "_private",
            "__special__",
            "CONSTANT",
            "namespace1.namespace2.Class",
            "package.subpackage.Module",
        ]
        for id_text in common:
            with self.subTest(common=id_text):
                self.assert_parses(f"{id_text} is_a Thing")

    def test_mixed_in_expressions(self):
        """Test identifiers in ontology expressions."""
        expressions = [
            "com.example.Person is_subclass_of com.example.Entity",
            "std::vector is_equivalent_to java.util.ArrayList",
            "MyClass$Inner is_subclass_of BaseClass",
        ]

        for expr in expressions:
            with self.subTest(expression=expr):
                self.assert_parses(expr)


class TestIdentifierEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions for identifiers using variant='ai'."""

    def assert_parses(self, ontology_text):
        """Assert that ontology text parses successfully with AI variant."""
        net = owl_rete_cpp.ReteNetwork()
        try:
            wme_count = net.load_ontology_from_string(ontology_text, variant="ai")
            self.assertGreater(wme_count, 0, f"No WMEs created for: {ontology_text}")
        except Exception as e:
            self.fail(f"Failed to parse with AI variant: {ontology_text}\nError: {e}")

    def test_numbers_in_identifiers(self):
        """Test identifiers with numbers."""
        valid_with_numbers = [
            "var1",
            "test123",
            "id_456",
            "v2_0_1",
            "utf8",
            "base64",
        ]
        for id_text in valid_with_numbers:
            with self.subTest(id_with_numbers=id_text):
                self.assert_parses(f"{id_text} is_a Variable")

    def test_special_prefixes(self):
        """Test special character prefixes."""
        special_prefixes = [
            "@annotation",
            # Note: #tag is treated as a comment
            # Note: $var - $ is CUR token, not part of identifier
            "_private",
        ]
        for id_text in special_prefixes:
            with self.subTest(special_prefix=id_text):
                self.assert_parses(f"{id_text} is_a Identifier")

    def test_very_long_namespaces(self):
        """Test extremely long namespace chains."""
        # Build a very long Java-style namespace
        long_java = ".".join(["package"] * 20)
        self.assert_parses(f"{long_java} is_a Module")

        # Build a very long C++ namespace
        long_cpp = "::".join(["namespace"] * 20)
        self.assert_parses(f"{long_cpp} is_a Type")


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
