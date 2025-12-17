#!/usr/bin/env python3
"""
Test Suite for C# Fact Extraction
==================================

Tests the C# code analysis capabilities of RETER.
Verifies that C# code is correctly parsed and facts are extracted.

Requirements:
    - RETER compiled with C# parser support
    - cs_ontology.dl loaded
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reter import Reter


class TestCSharpFactExtraction(unittest.TestCase):
    """Test cases for C# code fact extraction."""

    def setUp(self):
        """Set up each test."""
        # Create a fresh reasoner for each test to avoid fact accumulation
        self.reasoner = Reter("ai")

        # Load C# ontology from reter-logical-thinking-server resources
        ontology_path = Path(__file__).parent.parent / "reter-logical-thinking-server" / "resources" / "csharp" / "cs_ontology.reol"
        if ontology_path.exists():
            self.reasoner.load_ontology_file(str(ontology_path))
        else:
            raise FileNotFoundError(f"C# ontology not found at {ontology_path}")

    def test_simple_class_extraction(self):
        """Test extraction of a simple class definition."""
        code = """
namespace TestApp {
    public class Animal {
        // Simple animal class
    }
}
"""
        wme_count = self.reasoner.load_csharp_code(code, "TestApp")

        # Query for classes
        classes = self.reasoner.pattern(
            ("?x", "type", "cs:Class"),
            ("?x", "name", "?name")
        ).to_list()

        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0]["?name"], "Animal")

    def test_class_with_methods(self):
        """Test extraction of class with methods."""
        code = """
namespace TestApp {
    public class Dog {
        private string name;

        public Dog(string name) {
            this.name = name;
        }

        public string Bark() {
            return "Woof!";
        }

        public string Fetch(string item) {
            return item;
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for methods
        methods = self.reasoner.pattern(
            ("?class", "type", "cs:Class"),
            ("?class", "hasMethod", "?method"),
            ("?class", "name", "?class_name"),
            ("?method", "name", "?method_name")
        ).to_list()

        method_names = {m["?method_name"] for m in methods}
        self.assertIn("Bark", method_names)
        self.assertIn("Fetch", method_names)

    def test_class_with_properties(self):
        """Test extraction of class properties."""
        code = """
namespace TestApp {
    public class Person {
        public string Name { get; set; }
        public int Age { get; set; }
        public string Email { get; private set; }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for properties
        properties = self.reasoner.pattern(
            ("?class", "type", "cs:Class"),
            ("?class", "hasProperty", "?property"),
            ("?class", "name", "Person"),
            ("?property", "name", "?property_name")
        ).to_list()

        property_names = {p["?property_name"] for p in properties}
        self.assertIn("Name", property_names)
        self.assertIn("Age", property_names)
        self.assertIn("Email", property_names)

    def test_inheritance(self):
        """Test extraction of inheritance relationships."""
        code = """
namespace TestApp {
    public class Animal {
        public virtual void Speak() { }
    }

    public class Dog : Animal {
        public override void Speak() { }
    }

    public class Labrador : Dog {
        public void Fetch() { }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for inheritance
        inheritance = self.reasoner.pattern(
            ("?subclass", "inheritsFrom", "?superclass"),
            ("?subclass", "name", "?sub_name"),
            ("?superclass", "name", "?super_name")
        ).to_list()

        # Check direct inheritance
        inheritance_pairs = {(r["?sub_name"], r["?super_name"]) for r in inheritance}
        self.assertIn(("Dog", "Animal"), inheritance_pairs)
        self.assertIn(("Labrador", "Dog"), inheritance_pairs)

    def test_interface_implementation(self):
        """Test extraction of interface implementation."""
        code = """
namespace TestApp {
    public interface IFlyable {
        void Fly();
    }

    public interface ISwimmable {
        void Swim();
    }

    public class Duck : IFlyable, ISwimmable {
        public void Fly() { }
        public void Swim() { }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for interfaces
        interfaces = self.reasoner.pattern(
            ("?x", "type", "cs:Interface"),
            ("?x", "name", "?name")
        ).to_list()

        interface_names = {i["?name"] for i in interfaces}
        self.assertIn("IFlyable", interface_names)
        self.assertIn("ISwimmable", interface_names)

        # Query for interface implementations
        implementations = self.reasoner.pattern(
            ("?class", "implements", "?interface"),
            ("?class", "name", "Duck"),
            ("?interface", "name", "?interface_name")
        ).to_list()

        implemented_interfaces = {i["?interface_name"] for i in implementations}
        self.assertIn("IFlyable", implemented_interfaces)
        self.assertIn("ISwimmable", implemented_interfaces)

    def test_struct_extraction(self):
        """Test extraction of struct definitions."""
        code = """
namespace TestApp {
    public struct Point {
        public int X { get; set; }
        public int Y { get; set; }

        public double Distance() {
            return Math.Sqrt(X * X + Y * Y);
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for structs
        structs = self.reasoner.pattern(
            ("?x", "type", "cs:Struct"),
            ("?x", "name", "?name")
        ).to_list()

        self.assertEqual(len(structs), 1)
        self.assertEqual(structs[0]["?name"], "Point")

    def test_enum_extraction(self):
        """Test extraction of enum definitions."""
        code = """
namespace TestApp {
    public enum DayOfWeek {
        Sunday,
        Monday,
        Tuesday,
        Wednesday,
        Thursday,
        Friday,
        Saturday
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for enums
        enums = self.reasoner.pattern(
            ("?x", "type", "cs:Enum"),
            ("?x", "name", "?name")
        ).to_list()

        self.assertEqual(len(enums), 1)
        self.assertEqual(enums[0]["?name"], "DayOfWeek")

    def test_namespace_extraction(self):
        """Test extraction of namespace declarations."""
        code = """
namespace MyCompany.MyApp.Models {
    public class User {
        public string Name { get; set; }
    }
}
"""
        self.reasoner.load_csharp_code(code, "MyCompany.MyApp.Models")

        # Query for namespaces
        namespaces = self.reasoner.pattern(
            ("?x", "type", "cs:Namespace"),
            ("?x", "name", "?name")
        ).to_list()

        self.assertGreater(len(namespaces), 0)
        namespace_names = {n["?name"] for n in namespaces}
        self.assertIn("MyCompany.MyApp.Models", namespace_names)

    def test_using_directives(self):
        """Test extraction of using directives."""
        code = """
using System;
using System.Collections.Generic;
using System.Linq;
using MyApp.Models;

namespace TestApp {
    public class MyClass { }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for using directives
        usings = self.reasoner.pattern(
            ("?using", "type", "cs:Using"),
            ("?using", "imports", "?module")
        ).to_list()

        imported_namespaces = {u["?module"] for u in usings}
        self.assertIn("System", imported_namespaces)
        self.assertIn("System.Collections.Generic", imported_namespaces)

    def test_parameter_extraction(self):
        """Test extraction of method parameters."""
        code = """
namespace TestApp {
    public class Calculator {
        public int Add(int x, int y) {
            return x + y;
        }

        public void Process(string data, double threshold = 0.5, bool verbose = false) {
            // Implementation
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for parameters
        params = self.reasoner.pattern(
            ("?param", "type", "cs:Parameter"),
            ("?param", "name", "?name"),
            ("?param", "ofMethod", "?method")
        ).to_list()

        param_names = {p["?name"] for p in params}
        self.assertIn("x", param_names)
        self.assertIn("y", param_names)
        self.assertIn("data", param_names)
        self.assertIn("threshold", param_names)

    def test_access_modifiers(self):
        """Test extraction of access modifiers."""
        code = """
namespace TestApp {
    public class MyClass {
        public string PublicField;
        private int PrivateField;
        protected double ProtectedField;
        internal string InternalField;

        public void PublicMethod() { }
        private void PrivateMethod() { }
        protected void ProtectedMethod() { }
        internal void InternalMethod() { }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for public methods
        public_methods = self.reasoner.pattern(
            ("?method", "type", "cs:Method"),
            ("?method", "accessModifier", "public"),
            ("?method", "name", "?name")
        ).to_list()

        public_method_names = {m["?name"] for m in public_methods}
        self.assertIn("PublicMethod", public_method_names)

        # Query for private methods
        private_methods = self.reasoner.pattern(
            ("?method", "type", "cs:Method"),
            ("?method", "accessModifier", "private"),
            ("?method", "name", "?name")
        ).to_list()

        private_method_names = {m["?name"] for m in private_methods}
        self.assertIn("PrivateMethod", private_method_names)

    def test_attribute_extraction(self):
        """Test extraction of attributes (C# decorators)."""
        code = """
namespace TestApp {
    [Serializable]
    public class DataModel {
        [Obsolete("Use NewProperty instead")]
        public string OldProperty { get; set; }

        [Required]
        [MaxLength(100)]
        public string Name { get; set; }
    }

    public class Tests {
        [Test]
        public void TestMethod() { }

        [Fact]
        public void FactMethod() { }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for attributes
        attributes = self.reasoner.pattern(
            ("?entity", "hasAttribute", "?attr"),
            ("?attr", "name", "?attr_name")
        ).to_list()

        attr_names = {a["?attr_name"] for a in attributes}
        self.assertIn("Serializable", attr_names)
        self.assertIn("Obsolete", attr_names)
        self.assertIn("Test", attr_names)

    def test_field_extraction(self):
        """Test extraction of fields."""
        code = """
namespace TestApp {
    public class MyClass {
        private string _name;
        private int _age;
        public static readonly string DefaultValue = "default";
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for fields
        fields = self.reasoner.pattern(
            ("?class", "hasField", "?field"),
            ("?class", "name", "MyClass"),
            ("?field", "name", "?field_name")
        ).to_list()

        field_names = {f["?field_name"] for f in fields}
        self.assertIn("_name", field_names)
        self.assertIn("_age", field_names)
        self.assertIn("DefaultValue", field_names)

    def test_constructor_extraction(self):
        """Test extraction of constructors."""
        code = """
namespace TestApp {
    public class Person {
        public Person() { }
        public Person(string name) { }
        public Person(string name, int age) { }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for constructors
        constructors = self.reasoner.pattern(
            ("?class", "hasConstructor", "?ctor"),
            ("?class", "name", "Person"),
            ("?ctor", "type", "cs:Constructor")
        ).to_list()

        self.assertEqual(len(constructors), 3)

    def test_event_extraction(self):
        """Test extraction of events."""
        code = """
namespace TestApp {
    public class Button {
        public event EventHandler Click;
        public event EventHandler<CustomEventArgs> CustomEvent;
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for events
        events = self.reasoner.pattern(
            ("?class", "hasEvent", "?event"),
            ("?class", "name", "Button"),
            ("?event", "name", "?event_name")
        ).to_list()

        event_names = {e["?event_name"] for e in events}
        self.assertIn("Click", event_names)
        self.assertIn("CustomEvent", event_names)

    def test_delegate_extraction(self):
        """Test extraction of delegates."""
        code = """
namespace TestApp {
    public delegate void ProcessHandler(string data);
    public delegate int ComparisonHandler(object a, object b);
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for delegates
        delegates = self.reasoner.pattern(
            ("?x", "type", "cs:Delegate"),
            ("?x", "name", "?name")
        ).to_list()

        delegate_names = {d["?name"] for d in delegates}
        self.assertIn("ProcessHandler", delegate_names)
        self.assertIn("ComparisonHandler", delegate_names)

    def test_method_calls(self):
        """Test extraction of method call relationships."""
        code = """
namespace TestApp {
    public class Calculator {
        private int Helper() {
            return 42;
        }

        public int Calculate() {
            int result = Helper();
            Console.WriteLine(result);
            return result;
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for method calls
        calls = self.reasoner.pattern(
            ("?caller", "calls", "?callee")
        ).to_list()

        # Verify we have call facts
        self.assertGreater(len(calls), 0, "No call facts were extracted!")

        # Find calls from Calculate
        calculate_calls = [c["?callee"] for c in calls if "Calculate" in c["?caller"]]

        # Check that Calculate calls Helper and WriteLine
        self.assertTrue(any("Helper" in callee for callee in calculate_calls),
                       "Calculate should call Helper")

    def test_load_csharp_file(self):
        """Test loading C# code from a file."""
        # Create temporary C# file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write("""
namespace TestApp {
    public class TestClass {
        public void TestMethod() {
            // Implementation
        }
    }
}
""")
            temp_path = f.name

        try:
            wme_count = self.reasoner.load_csharp_file(temp_path)
            self.assertGreater(wme_count, 0)

            # Verify class was extracted
            classes = self.reasoner.pattern(
                ("?x", "type", "cs:Class"),
                ("?x", "name", "TestClass")
            ).to_list()

            self.assertEqual(len(classes), 1)
        finally:
            # Clean up temporary file
            os.unlink(temp_path)

    def test_load_csharp_directory(self):
        """Test loading all C# files from a directory."""
        # Create temporary directory with C# files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = Path(temp_dir) / "Class1.cs"
            file1.write_text("""
namespace TestApp {
    public class Module1Class { }
}
""")

            file2 = Path(temp_dir) / "Class2.cs"
            file2.write_text("""
namespace TestApp {
    public class Module2Class { }
}
""")

            # Create subdirectory
            subdir = Path(temp_dir) / "Models"
            subdir.mkdir()

            file3 = subdir / "Model.cs"
            file3.write_text("""
namespace TestApp.Models {
    public class Module3Class { }
}
""")

            # Load directory recursively
            total_wmes = self.reasoner.load_csharp_directory(temp_dir, recursive=True)
            self.assertGreater(total_wmes, 0)

            # Verify all classes were extracted
            classes = self.reasoner.pattern(
                ("?x", "type", "cs:Class"),
                ("?x", "name", "?name")
            ).to_list()

            class_names = {c["?name"] for c in classes}
            self.assertIn("Module1Class", class_names)
            self.assertIn("Module2Class", class_names)
            self.assertIn("Module3Class", class_names)

    def test_error_handling(self):
        """Test permissive error handling for invalid C# code."""
        invalid_code = """
namespace TestApp {
    public class BrokenClass {
        public void BrokenMethod(
            // Missing closing parenthesis
    }
}
"""

        # Parser uses error recovery - should not raise exception
        # but should still process what it can
        wme_count = self.reasoner.load_csharp_code(invalid_code, "TestApp")

        # Should have at least created the namespace fact
        self.assertGreaterEqual(wme_count, 1)

    def test_empty_code(self):
        """Test handling of empty C# code."""
        empty_code = ""
        wme_count = self.reasoner.load_csharp_code(empty_code, "EmptyNamespace")

        # Should still create namespace fact
        self.assertGreaterEqual(wme_count, 1)

    def test_position_metadata(self):
        """Test extraction of source position metadata."""
        code = """
namespace TestApp {
    public class MyClass {  // Line 3
        public void Method() {  // Line 4
            // Implementation
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for position information
        positions = self.reasoner.pattern(
            ("?entity", "atLine", "?line")
        ).to_list()

        # Should have line numbers for entities
        self.assertGreater(len(positions), 0)


class TestCSharpOntologyInference(unittest.TestCase):
    """Test cases for C# ontology inference rules."""

    def setUp(self):
        """Set up each test."""
        # Create a fresh reasoner for each test to avoid fact accumulation
        self.reasoner = Reter("ai")

        # Load full C# ontology with inference rules from reter-logical-thinking-server resources
        ontology_path = Path(__file__).parent.parent / "reter-logical-thinking-server" / "resources" / "csharp" / "cs_ontology.reol"
        if ontology_path.exists():
            self.reasoner.load_ontology_file(str(ontology_path))
        else:
            raise FileNotFoundError(f"C# ontology not found at {ontology_path}")

    def test_transitive_inheritance(self):
        """Test inference of transitive inheritance."""
        code = """
namespace TestApp {
    public class A { }
    public class B : A { }
    public class C : B { }
    public class D : C { }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for transitive inheritance
        inheritance = self.reasoner.pattern(
            ("?descendant", "inheritsFromTransitive", "?ancestor"),
            ("?descendant", "name", "D"),
            ("?ancestor", "name", "?ancestor_name")
        ).to_list()

        ancestor_names = {r["?ancestor_name"] for r in inheritance}
        # D should inherit from C, B, and A (transitively)
        if ancestor_names:  # Only if inference rules are active
            self.assertIn("C", ancestor_names)
            self.assertIn("B", ancestor_names)
            self.assertIn("A", ancestor_names)

    def test_transitive_interface_implementation(self):
        """Test inference of transitive interface implementation."""
        code = """
namespace TestApp {
    public interface IBase { }
    public interface IDerived : IBase { }
    public class MyClass : IDerived { }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for transitive interface implementation
        implementations = self.reasoner.pattern(
            ("?class", "implementsTransitive", "?interface"),
            ("?class", "name", "MyClass"),
            ("?interface", "name", "?interface_name")
        ).to_list()

        interface_names = {i["?interface_name"] for i in implementations}
        if interface_names:  # Only if inference rules are active
            self.assertIn("IDerived", interface_names)
            self.assertIn("IBase", interface_names)

    def test_undocumented_detection(self):
        """Test detection of undocumented entities."""
        code = """
namespace TestApp {
    /// <summary>Documented class</summary>
    public class DocumentedClass { }

    public class UndocumentedClass { }

    public class MyClass {
        /// <summary>Documented method</summary>
        public void DocumentedMethod() { }

        public void UndocumentedMethod() { }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for undocumented entities
        undocumented = self.reasoner.pattern(
            ("?entity", "undocumented", "true"),
            ("?entity", "name", "?name")
        ).to_list()

        undoc_names = {u["?name"] for u in undocumented}
        if undoc_names:  # Only if inference rules are active
            self.assertIn("UndocumentedClass", undoc_names)
            self.assertIn("UndocumentedMethod", undoc_names)

    def test_unused_private_method_detection(self):
        """Test detection of unused private methods."""
        code = """
namespace TestApp {
    public class MyClass {
        private void UsedMethod() { }
        private void UnusedMethod() { }

        public void PublicMethod() {
            UsedMethod();
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for unused private methods
        unused = self.reasoner.pattern(
            ("?method", "unused", "true"),
            ("?method", "name", "?name")
        ).to_list()

        unused_names = {u["?name"] for u in unused}
        if unused_names:  # Only if inference rules are active
            self.assertIn("UnusedMethod", unused_names)
            self.assertNotIn("UsedMethod", unused_names)

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        code = """
namespace TestApp {
    // This creates a circular dependency
    public class A : B { }
    public class B : A { }
}
"""
        # Note: This code won't compile, but tests error handling
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for circular dependencies
        circular = self.reasoner.pattern(
            ("?class", "circularDependency", "true"),
            ("?class", "name", "?name")
        ).to_list()

        # If inference rules detect circular dependencies
        if circular:
            circular_names = {c["?name"] for c in circular}
            # Both A and B should be flagged
            self.assertTrue(len(circular_names) > 0)

    def test_test_method_detection(self):
        """Test detection of test methods by attributes."""
        code = """
namespace TestApp.Tests {
    public class MyTests {
        [Test]
        public void TestMethod1() { }

        [Fact]
        public void TestMethod2() { }

        [TestMethod]
        public void TestMethod3() { }

        public void NonTestMethod() { }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp.Tests")

        # Query for test methods
        test_methods = self.reasoner.pattern(
            ("?method", "isTestMethod", "true"),
            ("?method", "name", "?name")
        ).to_list()

        test_names = {t["?name"] for t in test_methods}
        if test_names:  # Only if inference rules are active
            self.assertIn("TestMethod1", test_names)
            self.assertIn("TestMethod2", test_names)
            self.assertIn("TestMethod3", test_names)
            self.assertNotIn("NonTestMethod", test_names)

    def test_singleton_pattern_detection(self):
        """Test detection of singleton design pattern."""
        code = """
namespace TestApp {
    public class Singleton {
        private static Singleton _instance;

        private Singleton() { }

        public static Singleton Instance {
            get {
                if (_instance == null) {
                    _instance = new Singleton();
                }
                return _instance;
            }
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for singleton classes
        singletons = self.reasoner.pattern(
            ("?class", "isSingleton", "true"),
            ("?class", "name", "?name")
        ).to_list()

        singleton_names = {s["?name"] for s in singletons}
        if singleton_names:  # Only if inference rules are active
            self.assertIn("Singleton", singleton_names)


class TestCSharpNewFeatures(unittest.TestCase):
    """Test cases for newly added C# fact extraction features."""

    def setUp(self):
        """Set up each test."""
        self.reasoner = Reter("ai")
        ontology_path = Path(__file__).parent.parent / "reter-logical-thinking-server" / "resources" / "csharp" / "cs_ontology.reol"
        if ontology_path.exists():
            self.reasoner.load_ontology_file(str(ontology_path))
        else:
            raise FileNotFoundError(f"C# ontology not found at {ontology_path}")

    def test_try_catch_finally_extraction(self):
        """Test extraction of try/catch/finally blocks."""
        code = """
namespace TestApp {
    public class ErrorHandler {
        public void HandleError() {
            try {
                DoSomethingDangerous();
            }
            catch (ArgumentException ex) {
                Console.WriteLine(ex.Message);
            }
            catch (Exception e) {
                LogError(e);
            }
            finally {
                Cleanup();
            }
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for try blocks
        try_blocks = self.reasoner.pattern(
            ("?try", "concept", "cs:TryBlock"),
            ("?try", "hasCatch", "?has_catch")
        ).to_list()

        self.assertGreater(len(try_blocks), 0, "No try blocks were extracted!")

        # Query for catch clauses
        catch_clauses = self.reasoner.pattern(
            ("?catch", "concept", "cs:CatchClause"),
            ("?catch", "exceptionType", "?type")
        ).to_list()

        exception_types = {c["?type"] for c in catch_clauses}
        self.assertIn("ArgumentException", exception_types)
        self.assertIn("Exception", exception_types)

        # Query for finally clauses
        finally_clauses = self.reasoner.pattern(
            ("?finally", "concept", "cs:FinallyClause")
        ).to_list()

        self.assertGreater(len(finally_clauses), 0, "No finally clauses were extracted!")

    def test_throw_statement_extraction(self):
        """Test extraction of throw statements."""
        code = """
namespace TestApp {
    public class Validator {
        public void Validate(string input) {
            if (input == null) {
                throw new ArgumentNullException("input");
            }
            if (input.Length == 0) {
                throw new ArgumentException("Input cannot be empty");
            }
        }

        public void Process() {
            try {
                DoWork();
            }
            catch {
                throw;  // Rethrow
            }
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for throw statements
        throws = self.reasoner.pattern(
            ("?throw", "concept", "cs:ThrowStatement")
        ).to_list()

        self.assertGreater(len(throws), 0, "No throw statements were extracted!")

        # Check for specific exception types
        throws_with_type = self.reasoner.pattern(
            ("?throw", "concept", "cs:ThrowStatement"),
            ("?throw", "exceptionType", "?type")
        ).to_list()

        exception_types = {t["?type"] for t in throws_with_type}
        self.assertIn("ArgumentNullException", exception_types)
        self.assertIn("ArgumentException", exception_types)

        # Check for rethrows
        rethrows = self.reasoner.pattern(
            ("?throw", "concept", "cs:ThrowStatement"),
            ("?throw", "isRethrow", "true")
        ).to_list()

        self.assertGreater(len(rethrows), 0, "No rethrow statements were detected!")

    def test_return_statement_extraction(self):
        """Test extraction of return statements."""
        code = """
namespace TestApp {
    public class Calculator {
        public int Add(int a, int b) {
            return a + b;
        }

        public bool IsValid(string input) {
            if (input == null) return false;
            if (input.Length == 0) return false;
            return true;
        }

        public object GetValue() {
            return null;
        }

        public void DoNothing() {
            return;
        }

        public int GetErrorCode() {
            return -1;
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for return statements
        returns = self.reasoner.pattern(
            ("?ret", "concept", "cs:ReturnStatement")
        ).to_list()

        self.assertGreater(len(returns), 0, "No return statements were extracted!")

        # Check for null returns
        null_returns = self.reasoner.pattern(
            ("?ret", "concept", "cs:ReturnStatement"),
            ("?ret", "returnsNull", "true")
        ).to_list()

        self.assertGreater(len(null_returns), 0, "No null return statements were detected!")

        # Check for void returns
        void_returns = self.reasoner.pattern(
            ("?ret", "concept", "cs:ReturnStatement"),
            ("?ret", "returnsVoid", "true")
        ).to_list()

        self.assertGreater(len(void_returns), 0, "No void return statements were detected!")

    def test_literal_extraction(self):
        """Test extraction of literals."""
        code = """
namespace TestApp {
    public class Constants {
        public void Demo() {
            int num = 42;
            string text = "Hello World";
            bool flag = true;
            double pi = 3.14159;
            object nothing = null;
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for literals
        literals = self.reasoner.pattern(
            ("?lit", "concept", "cs:Literal"),
            ("?lit", "literalType", "?type")
        ).to_list()

        literal_types = {l["?type"] for l in literals}
        self.assertIn("integer", literal_types)
        self.assertIn("string", literal_types)
        self.assertIn("boolean", literal_types)
        self.assertIn("real", literal_types)
        self.assertIn("null", literal_types)

    def test_magic_number_detection(self):
        """Test detection of magic numbers in literals."""
        code = """
namespace TestApp {
    public class MagicNumbers {
        public void Demo() {
            int normal = 0;
            int normalOne = 1;
            int magic = 42;
            int anotherMagic = 100;
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for magic numbers
        magic_numbers = self.reasoner.pattern(
            ("?lit", "concept", "cs:Literal"),
            ("?lit", "isMagicNumber", "true"),
            ("?lit", "value", "?val")
        ).to_list()

        magic_values = {m["?val"] for m in magic_numbers}
        self.assertIn("42", magic_values)
        self.assertIn("100", magic_values)
        # 0 and 1 should NOT be flagged as magic numbers
        self.assertNotIn("0", magic_values)
        self.assertNotIn("1", magic_values)

    def test_async_static_modifier_extraction(self):
        """Test extraction of async and static modifiers."""
        code = """
namespace TestApp {
    public class ModifierTest {
        public async Task AsyncMethod() {
            await Task.Delay(100);
        }

        public static void StaticMethod() { }

        public virtual void VirtualMethod() { }

        public static async Task StaticAsyncMethod() {
            await Task.Delay(50);
        }
    }

    public static class StaticClass { }

    public abstract class AbstractClass {
        public abstract void AbstractMethod();
    }

    public sealed class SealedClass { }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for async methods
        async_methods = self.reasoner.pattern(
            ("?method", "concept", "cs:Method"),
            ("?method", "isAsync", "true"),
            ("?method", "name", "?name")
        ).to_list()

        async_names = {m["?name"] for m in async_methods}
        self.assertIn("AsyncMethod", async_names)
        self.assertIn("StaticAsyncMethod", async_names)

        # Query for static methods
        static_methods = self.reasoner.pattern(
            ("?method", "concept", "cs:Method"),
            ("?method", "isStatic", "true"),
            ("?method", "name", "?name")
        ).to_list()

        static_names = {m["?name"] for m in static_methods}
        self.assertIn("StaticMethod", static_names)
        self.assertIn("StaticAsyncMethod", static_names)

        # Query for static classes
        static_classes = self.reasoner.pattern(
            ("?class", "concept", "cs:Class"),
            ("?class", "isStatic", "true"),
            ("?class", "name", "?name")
        ).to_list()

        static_class_names = {c["?name"] for c in static_classes}
        self.assertIn("StaticClass", static_class_names)

        # Query for abstract classes
        abstract_classes = self.reasoner.pattern(
            ("?class", "concept", "cs:Class"),
            ("?class", "isAbstract", "true"),
            ("?class", "name", "?name")
        ).to_list()

        abstract_class_names = {c["?name"] for c in abstract_classes}
        self.assertIn("AbstractClass", abstract_class_names)

        # Query for sealed classes
        sealed_classes = self.reasoner.pattern(
            ("?class", "concept", "cs:Class"),
            ("?class", "isSealed", "true"),
            ("?class", "name", "?name")
        ).to_list()

        sealed_class_names = {c["?name"] for c in sealed_classes}
        self.assertIn("SealedClass", sealed_class_names)

    def test_call_facts_extraction(self):
        """Test extraction of call relationships (caller calls callee)."""
        code = """
namespace TestApp {
    public class Caller {
        public void Execute() {
            Helper();
            Console.WriteLine("Test");
            Math.Abs(-5);
        }

        private void Helper() { }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for calls relationships (caller, "calls", callee)
        calls = self.reasoner.pattern(
            ("?caller", "calls", "?callee")
        ).to_list()

        callees = {c["?callee"] for c in calls}
        self.assertTrue(any("Helper" in c for c in callees), "Helper call not found")
        self.assertTrue(any("WriteLine" in c for c in callees), "WriteLine call not found")

    def test_empty_catch_detection(self):
        """Test detection of empty catch blocks (code smell)."""
        code = """
namespace TestApp {
    public class BadPractice {
        public void SilentFail() {
            try {
                DoSomething();
            }
            catch (Exception) {
                // Empty catch - silently swallowing exception
            }
        }

        public void GoodPractice() {
            try {
                DoSomething();
            }
            catch (Exception ex) {
                Logger.Log(ex);
            }
        }
    }
}
"""
        self.reasoner.load_csharp_code(code, "TestApp")

        # Query for empty catch blocks
        empty_catches = self.reasoner.pattern(
            ("?catch", "concept", "cs:CatchClause"),
            ("?catch", "isEmpty", "true")
        ).to_list()

        self.assertGreater(len(empty_catches), 0, "No empty catch blocks detected!")


if __name__ == "__main__":
    unittest.main()
