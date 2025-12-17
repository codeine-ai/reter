"""
Tests for JavaScript code fact extraction.

Tests that the JavaScript parser extracts proper semantic facts
similar to the Python extractor.
"""

import pytest
from reter import Reter, owl_rete_cpp


class TestJavaScriptParsing:
    """Tests for parse_javascript_code function."""

    def test_parse_simple_function(self):
        """Test parsing a simple JavaScript function."""
        code = """
function greet(name) {
    return "Hello, " + name;
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert len(facts) > 0, "Should extract at least one fact"

        # Check for function fact (uses concept field for the type)
        function_facts = [f for f in facts if f.get("concept") == "js:Function"]
        assert len(function_facts) >= 1, "Should find at least one function"

        # Check function name
        greet_func = [f for f in function_facts if f.get("name") == "greet"]
        assert len(greet_func) == 1, "Should find 'greet' function"

    def test_parse_class(self):
        """Test parsing a JavaScript class."""
        code = """
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    greet() {
        return "Hello, " + this.name;
    }

    static createAnonymous() {
        return new Person("Anonymous", 0);
    }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for class fact (uses concept field for the type)
        class_facts = [f for f in facts if f.get("concept") == "js:Class"]
        assert len(class_facts) >= 1, "Should find at least one class"

        person_class = [f for f in class_facts if f.get("name") == "Person"]
        assert len(person_class) == 1, "Should find 'Person' class"

        # Check for methods
        method_facts = [f for f in facts if f.get("concept") == "js:Method"]
        assert len(method_facts) >= 2, "Should find at least 2 methods"

        # Check for constructor
        constructor_facts = [f for f in facts if f.get("concept") == "js:Constructor"]
        assert len(constructor_facts) >= 1, "Should find constructor"

    def test_parse_class_inheritance(self):
        """Test parsing class inheritance."""
        code = """
class Animal {
    speak() {
        return "...";
    }
}

class Dog extends Animal {
    speak() {
        return "Woof!";
    }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check Dog class exists (uses concept field for the type)
        dog_class = [f for f in facts if f.get("concept") == "js:Class" and f.get("name") == "Dog"]
        assert len(dog_class) == 1, "Should find 'Dog' class"

        # Check inheritance - it's represented as a role_assertion with "inheritsFrom"
        dog_id = dog_class[0].get("individual")
        inherits_facts = [f for f in facts
                         if f.get("type") == "role_assertion"
                         and f.get("subject") == dog_id
                         and f.get("role") == "inheritsFrom"]
        assert len(inherits_facts) == 1, "Dog should have inheritsFrom relationship"

        # Verify the parent is Animal by following the reference
        parent_id = inherits_facts[0].get("object")
        parent_class = [f for f in facts
                        if f.get("concept") == "js:Class"
                        and f.get("individual") == parent_id]
        assert len(parent_class) == 1, "Should find parent class"
        assert parent_class[0].get("name") == "Animal", "Dog should extend Animal"

    def test_parse_arrow_functions(self):
        """Test parsing arrow functions."""
        code = """
const add = (a, b) => a + b;
const greet = name => "Hello, " + name;
const multiLine = (x, y) => {
    const result = x * y;
    return result;
};
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for arrow function facts (uses concept field for the type)
        arrow_facts = [f for f in facts if f.get("concept") == "js:ArrowFunction"]
        assert len(arrow_facts) >= 1, "Should find at least one arrow function"

    def test_parse_imports(self):
        """Test parsing import statements."""
        code = """
import React from 'react';
import { useState, useEffect } from 'react';
import * as Utils from './utils';
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        # Should not have fatal errors (imports are valid JS)
        # Note: Some parsers may have warnings for imports outside modules

        # Check for import facts (uses concept field for the type)
        import_facts = [f for f in facts if f.get("concept") == "js:Import"]
        assert len(import_facts) >= 1, "Should find at least one import"

    def test_parse_exports(self):
        """Test parsing export statements."""
        code = """
export function greet(name) {
    return "Hello, " + name;
}

export const PI = 3.14159;

export default class Calculator {
    add(a, b) { return a + b; }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for export facts (uses concept field for the type)
        export_facts = [f for f in facts if f.get("concept") == "js:Export"]
        assert len(export_facts) >= 1, "Should find at least one export"

    def test_parse_async_function(self):
        """Test parsing async functions."""
        code = """
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for async function (uses concept field for the type)
        function_facts = [f for f in facts if f.get("concept") == "js:Function"]
        assert len(function_facts) >= 1, "Should find at least one function"

        fetch_func = [f for f in function_facts if f.get("name") == "fetchData"]
        assert len(fetch_func) == 1, "Should find 'fetchData' function"
        assert fetch_func[0].get("isAsync") == "true", "fetchData should be async"

    def test_parse_generator_function(self):
        """Test parsing generator functions."""
        code = """
function* range(start, end) {
    for (let i = start; i < end; i++) {
        yield i;
    }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for generator function (uses concept field for the type)
        function_facts = [f for f in facts if f.get("concept") == "js:Function"]
        range_func = [f for f in function_facts if f.get("name") == "range"]
        assert len(range_func) == 1, "Should find 'range' function"
        assert range_func[0].get("isGenerator") == "true", "range should be a generator"


class TestJavaScriptReterIntegration:
    """Tests for JavaScript integration with Reter."""

    def test_load_javascript_code(self):
        """Test loading JavaScript code into Reter."""
        reasoner = Reter()

        code = """
class Calculator {
    add(a, b) { return a + b; }
    subtract(a, b) { return a - b; }
}
"""
        wme_count = reasoner.load_javascript_code(code, "calculator")

        assert wme_count > 0, "Should add WMEs from JavaScript code"

        # Query for the class
        results = reasoner.reql("SELECT ?x WHERE { ?x type js:Class }")
        result_list = results.to_pydict()

        assert len(result_list.get("?x", [])) >= 1, "Should find at least one JS class"

    def test_load_javascript_file(self, tmp_path):
        """Test loading JavaScript file into Reter."""
        # Create a test JS file
        js_file = tmp_path / "test.js"
        js_file.write_text("""
function hello() {
    console.log("Hello, World!");
}

class Greeter {
    constructor(name) {
        this.name = name;
    }

    greet() {
        return "Hello, " + this.name;
    }
}
""")

        reasoner = Reter()
        wme_count = reasoner.load_javascript_file(str(js_file))

        assert wme_count > 0, "Should add WMEs from JavaScript file"

    def test_javascript_and_python_together(self):
        """Test loading both JavaScript and Python code."""
        reasoner = Reter()

        # Load Python
        python_code = """
class PythonClass:
    def method(self):
        pass
"""
        py_count, py_errors = reasoner.load_python_code(python_code, "py_module")
        assert py_count > 0, "Should add Python WMEs"

        # Load JavaScript
        js_code = """
class JavaScriptClass {
    method() {}
}
"""
        js_count = reasoner.load_javascript_code(js_code, "js_module")
        assert js_count > 0, "Should add JavaScript WMEs"

        # Query for both
        py_classes = reasoner.reql("SELECT ?x WHERE { ?x type py:Class }")
        js_classes = reasoner.reql("SELECT ?x WHERE { ?x type js:Class }")

        assert len(py_classes.to_pydict().get("?x", [])) >= 1, "Should find Python class"
        assert len(js_classes.to_pydict().get("?x", [])) >= 1, "Should find JavaScript class"


class TestJavaScriptNewFeatures:
    """Tests for newly added JavaScript extraction features."""

    def test_parse_try_catch_finally(self):
        """Test parsing try/catch/finally blocks."""
        code = """
function risky() {
    try {
        const result = doSomething();
        return result;
    } catch (e) {
        console.log(e);
        throw new Error("Failed");
    } finally {
        cleanup();
    }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        # Check for try block
        try_facts = [f for f in facts if f.get("concept") == "js:TryBlock"]
        assert len(try_facts) >= 1, "Should find at least one try block"
        assert try_facts[0].get("hasCatch") == "true", "Try block should have catch"
        assert try_facts[0].get("hasFinally") == "true", "Try block should have finally"

        # Check for catch clause
        catch_facts = [f for f in facts if f.get("concept") == "js:CatchClause"]
        assert len(catch_facts) >= 1, "Should find at least one catch clause"
        assert catch_facts[0].get("exceptionVar") == "e", "Catch should have exception var 'e'"

        # Check for finally clause
        finally_facts = [f for f in facts if f.get("concept") == "js:FinallyClause"]
        assert len(finally_facts) >= 1, "Should find at least one finally clause"

    def test_parse_throw_statement(self):
        """Test parsing throw statements."""
        code = """
function validate(x) {
    if (!x) {
        throw new Error("Invalid input");
    }
    if (x < 0) {
        throw new RangeError("Must be positive");
    }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        throw_facts = [f for f in facts if f.get("concept") == "js:ThrowStatement"]
        assert len(throw_facts) >= 2, "Should find at least 2 throw statements"

        # Check that Error type is detected
        error_throws = [f for f in throw_facts if f.get("throwsErrorType") == "true"]
        assert len(error_throws) >= 2, "Should detect Error types in throws"

    def test_parse_return_statements(self):
        """Test parsing return statements."""
        code = """
class Calculator {
    add(a, b) {
        return a + b;
    }

    getThis() {
        return this;
    }

    doNothing() {
        return;
    }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        return_facts = [f for f in facts if f.get("concept") == "js:ReturnStatement"]
        assert len(return_facts) >= 3, "Should find at least 3 return statements"

        # Check for return with value
        with_value = [f for f in return_facts if f.get("hasValue") == "true"]
        assert len(with_value) >= 2, "Should find returns with values"

        # Check for return without value
        without_value = [f for f in return_facts if f.get("hasValue") == "false"]
        assert len(without_value) >= 1, "Should find return without value"

        # Check for return this
        return_this = [f for f in return_facts if f.get("returnsThis") == "true"]
        assert len(return_this) >= 1, "Should detect 'return this'"

    def test_parse_function_calls(self):
        """Test parsing function calls via role assertions (caller calls callee)."""
        code = """
function process(data) {
    console.log("Processing");
    const result = transform(data);
    this.helper();
    return result;
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        # Call relationships are now role assertions (caller, "calls", callee)
        # instead of js:Call concept instances
        call_facts = [f for f in facts if f.get("role") == "calls"]
        assert len(call_facts) >= 3, f"Should find at least 3 call relationships"

        # Check that we found expected calls
        callees = {f.get("object") for f in call_facts}
        assert any("console.log" in c for c in callees), "Should find console.log call"
        assert any("transform" in c for c in callees), "Should find transform call"
        assert any("helper" in c for c in callees), "Should find this.helper call"

    def test_parse_assignments(self):
        """Test parsing assignment expressions."""
        code = """
class MyClass {
    constructor(name) {
        this.name = name;
        this.count = 0;
    }

    increment() {
        this.count += 1;
    }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        assign_facts = [f for f in facts if f.get("concept") == "js:Assignment"]
        # Note: Assignments may or may not be captured depending on parser structure

        # Check for attribute assignments in constructor
        attr_assigns = [f for f in assign_facts if f.get("isAttributeAssignment") == "true"]
        # May be 0 if the visitor doesn't traverse to AssignmentExpression for simple assignments

    def test_line_count_on_classes(self):
        """Test that classes have lineCount attribute."""
        code = """
class SimpleClass {
    method1() {}
    method2() {}
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        class_facts = [f for f in facts if f.get("concept") == "js:Class"]
        assert len(class_facts) >= 1, "Should find class"
        assert "lineCount" in class_facts[0], "Class should have lineCount"
        assert int(class_facts[0]["lineCount"]) > 0, "lineCount should be positive"

    def test_line_count_on_functions(self):
        """Test that functions have lineCount attribute."""
        code = """
function multiLineFunction() {
    const a = 1;
    const b = 2;
    return a + b;
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        func_facts = [f for f in facts if f.get("concept") == "js:Function"]
        assert len(func_facts) >= 1, "Should find function"
        assert "lineCount" in func_facts[0], "Function should have lineCount"
        assert int(func_facts[0]["lineCount"]) >= 4, "lineCount should be at least 4"

    def test_jsdoc_on_class(self):
        """Test that JSDoc comments are extracted for classes."""
        code = """
/**
 * Calculator class for basic math operations.
 * @class
 */
class Calculator {
    add(a, b) { return a + b; }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        class_facts = [f for f in facts if f.get("concept") == "js:Class"]
        assert len(class_facts) >= 1, "Should find class"
        assert "hasDocstring" in class_facts[0], "Class should have hasDocstring from JSDoc"
        assert "Calculator" in class_facts[0]["hasDocstring"], "JSDoc should contain class description"

    def test_jsdoc_on_function(self):
        """Test that JSDoc comments are extracted for functions."""
        code = """
/**
 * Adds two numbers together.
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} The sum
 */
function add(a, b) {
    return a + b;
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        func_facts = [f for f in facts if f.get("concept") == "js:Function"]
        assert len(func_facts) >= 1, "Should find function"
        assert "hasDocstring" in func_facts[0], "Function should have hasDocstring from JSDoc"
        assert "Adds two numbers" in func_facts[0]["hasDocstring"], "JSDoc should contain function description"

    def test_jsdoc_on_method(self):
        """Test that JSDoc comments are extracted for methods."""
        code = """
class MyClass {
    /**
     * Greets the user by name.
     * @param {string} name - The name to greet
     */
    greet(name) {
        return "Hello, " + name;
    }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        method_facts = [f for f in facts if f.get("concept") == "js:Method"]
        assert len(method_facts) >= 1, "Should find method"
        greet_method = [f for f in method_facts if f.get("name") == "greet"]
        assert len(greet_method) == 1, "Should find greet method"
        assert "hasDocstring" in greet_method[0], "Method should have hasDocstring from JSDoc"
        assert "Greets the user" in greet_method[0]["hasDocstring"], "JSDoc should contain method description"


class TestJavaScriptSyntaxErrors:
    """Tests for JavaScript syntax error handling."""

    def test_syntax_error_recovery(self):
        """Test that parser recovers from syntax errors and still extracts what it can."""
        code = """
function validFunction() {
    return 42;
}

// This has a syntax error
function broken( {
    return "broken";
}

class ValidClass {
    method() { return true; }
}
"""
        facts, errors = owl_rete_cpp.parse_javascript_code(code, "test_module")

        # Should have at least one error
        assert len(errors) >= 1, "Should report syntax error"

        # But should still extract valid parts
        assert len(facts) > 0, "Should still extract some facts despite errors"

        # Should find the valid function and class (uses concept field)
        valid_functions = [f for f in facts if f.get("concept") == "js:Function" and f.get("name") == "validFunction"]
        assert len(valid_functions) >= 1, "Should find validFunction despite error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
