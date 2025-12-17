#!/usr/bin/env python3
"""
Test suite for AI-friendly identifier handling via variant="ai" parameter.
Tests that various complex identifier patterns work with the AI syntax variant.
"""

import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from reter import owl_rete_cpp


class TestAIVariantIdentifiers(unittest.TestCase):
    """Test complex identifier patterns using variant='ai'."""

    def assert_parses(self, ontology_text):
        """Assert that ontology text parses successfully with AI variant."""
        net = owl_rete_cpp.ReteNetwork()
        try:
            wme_count = net.load_ontology_from_string(ontology_text, variant="ai")
            self.assertGreater(wme_count, 0, f"No WMEs created for: {ontology_text}")
        except Exception as e:
            self.fail(f"Failed to parse with AI variant: {ontology_text}\nError: {e}")

    # Test Simple Identifiers
    def test_simple_identifiers(self):
        """Test basic programming language identifiers."""
        simple_ids = [
            "Person",
            "myVariable",
            "MyClass",
            "_privateField",
            "__dunder__",
            "$jquery",
            "variable123",
            "CONSTANT_VALUE",
        ]
        for id_name in simple_ids:
            with self.subTest(id=id_name):
                self.assert_parses(f"{id_name} is_subclass_of Thing")

    # Test Namespaced Identifiers
    def test_java_package_identifiers(self):
        """Test Java-style package identifiers."""
        java_ids = [
            "com.example.MyClass",
            "org.apache.commons.lang3.StringUtils",
            "java.lang.String",
            "javax.swing.JFrame",
            "android.app.Activity",
        ]
        for id_name in java_ids:
            with self.subTest(id=id_name):
                # Object is a reserved keyword, must escape it with backticks
                self.assert_parses(f"{id_name} is_subclass_of `Object`")

    def test_cpp_namespace_identifiers(self):
        """Test C++ style namespace identifiers."""
        cpp_ids = [
            "std::vector",
            "std::vector::iterator",
            "boost::filesystem::path",
            "namespace1::namespace2::Class",
            "detail::impl::Helper",
        ]
        for id_name in cpp_ids:
            with self.subTest(id=id_name):
                self.assert_parses(f"{id_name} is_subclass_of Type")

    def test_inner_class_identifiers(self):
        """Test inner class notation with $."""
        inner_ids = [
            "OuterClass$InnerClass",
            "MyClass$Builder",
            "Package$Anonymous",  # Can't use $1 - digits can't follow separators
        ]
        for id_name in inner_ids:
            with self.subTest(id=id_name):
                self.assert_parses(f"{id_name} is_subclass_of Class")

    # Test Path Identifiers
    def test_unix_paths(self):
        """Test Unix/Linux file paths."""
        unix_paths = [
            "/usr/local/bin/app",
            "/home/user/document.txt",
            "/etc/config",
            "/var/log/system.log",
        ]
        for path in unix_paths:
            with self.subTest(path=path):
                # Paths are supported directly without quoting in AI variant
                self.assert_parses(f'{path} is_a FilePath')

    def test_relative_paths(self):
        """Test relative file paths."""
        rel_paths = [
            "./src/main.cpp",
            "./config.json",
            "../parent/file.txt",
            "../../../root.txt",
        ]
        for path in rel_paths:
            with self.subTest(path=path):
                # Relative paths need backticks due to ./ and ../ prefixes
                self.assert_parses(f'`{path}` is_a RelativePath')

    # Test URL Identifiers
    def test_url_identifiers(self):
        """Test URL/URI identifiers."""
        urls = [
            "http://example.com",
            "https://api.github.com/repos",
            "file:///home/user/file.txt",
            "ftp://ftp.example.com/pub/file.zip",
        ]
        for url in urls:
            with self.subTest(url=url):
                # URLs are supported directly in AI variant
                # Note: URLs with query params need backticks
                self.assert_parses(f'{url} is_a URL')

        # URL with query params needs backticks
        self.assert_parses('`https://www.google.com/search?q=test` is_a URL')

    # Test Quoted Identifiers
    def test_quoted_identifiers(self):
        """Test quoted identifiers with special characters using backticks."""
        quoted_ids = [
            "Complex ID with spaces",
            "special<>chars",
            "id!with@special#chars",
            "id-with-hyphens",  # Hyphens need backticks
            "id.with.dots.and-hyphens",  # Mixed separators need backticks
        ]
        for id_text in quoted_ids:
            with self.subTest(id=id_text):
                # AI variant uses backticks for quoting, not double quotes
                self.assert_parses(f'`{id_text}` is_a Identifier')

    # Test Version Strings
    def test_version_strings(self):
        """Test version string patterns."""
        # Note: Patterns with dots followed by numbers (like 1.2.3) are parsed as floats
        # Note: Hyphens followed by numbers can be confused with subtraction
        # So version strings with these patterns need backticks
        version_ids = [
            'version2',
            'v2',
            'myapp',
        ]
        for id_text in version_ids:
            with self.subTest(id=id_text):
                self.assert_parses(f'{id_text} is_a Version')

        # Version strings with dots/numbers or hyphens before numbers need backticks
        self.assert_parses('`v1.0.0` is_a Version')
        self.assert_parses('`libfoo-1.2.3` is_a Version')
        self.assert_parses('`my-app-version-2` is_a Version')

    # Test Complex Expressions
    def test_expressions_with_complex_ids(self):
        """Test that complex IDs work in expressions."""
        expressions = [
            "com.example.Person is_subclass_of com.example.Entity",
            "std::vector is_subclass_of Container",
            '`Complex-ID` is_a Person',  # Use backticks for identifiers with hyphens
            '`kebab-case-id` is_a Identifier',  # Hyphens need backticks
        ]
        for expr in expressions:
            with self.subTest(expr=expr):
                self.assert_parses(expr)


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
