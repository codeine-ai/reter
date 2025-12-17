"""
Tests for HTML code fact extraction.

Tests that the HTML parser extracts proper semantic facts
including document structure, elements, scripts, and embedded JavaScript.
"""

import pytest
from reter import Reter, owl_rete_cpp


class TestHTMLParsing:
    """Tests for parse_html_code function."""

    def test_parse_simple_html(self):
        """Test parsing a simple HTML document."""
        html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><p>Hello</p></body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "test_doc")

        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert len(facts) > 0, "Should extract at least one fact"

        # Check for document fact
        doc_facts = [f for f in facts if f.get("concept") == "html:Document"]
        assert len(doc_facts) >= 1, "Should find at least one document"

    def test_parse_inline_script(self):
        """Test parsing HTML with inline JavaScript."""
        html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<script>
function greet() {
    console.log("Hello!");
}
</script>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "script_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for script fact
        script_facts = [f for f in facts if f.get("concept") == "html:Script"]
        assert len(script_facts) >= 1, "Should find at least one script"

        # Check that JavaScript was parsed - should have js:Function
        js_function_facts = [f for f in facts if f.get("concept") == "js:Function"]
        assert len(js_function_facts) >= 1, "Should find JavaScript function from embedded script"

    def test_parse_external_script(self):
        """Test parsing HTML with external script reference."""
        html = """<!DOCTYPE html>
<html>
<head>
<script src="https://example.com/script.js"></script>
</head>
<body></body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "external_script")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for external script reference
        script_facts = [f for f in facts if f.get("concept") == "html:ScriptReference"]
        assert len(script_facts) >= 1, "Should find script reference"

    def test_parse_form(self):
        """Test parsing HTML form elements."""
        html = """<!DOCTYPE html>
<html>
<body>
<form action="/submit" method="POST">
    <input type="text" name="username" />
    <input type="password" name="password" />
    <input type="submit" value="Login" />
</form>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "form_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for form fact
        form_facts = [f for f in facts if f.get("concept") == "html:Form"]
        assert len(form_facts) >= 1, "Should find at least one form"

        # Check for input facts
        input_facts = [f for f in facts if f.get("concept") == "html:FormInput"]
        assert len(input_facts) >= 1, "Should find form inputs"

    def test_parse_event_handler(self):
        """Test parsing HTML event handlers."""
        html = """<!DOCTYPE html>
<html>
<body>
<button onclick="alert('clicked!')">Click me</button>
<form onsubmit="validate()">
    <input type="submit" />
</form>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "event_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for event handler facts
        event_facts = [f for f in facts if f.get("concept") == "html:EventHandler"]
        assert len(event_facts) >= 1, "Should find at least one event handler"

    def test_parse_anchor_link(self):
        """Test parsing HTML anchor elements."""
        html = """<!DOCTYPE html>
<html>
<body>
<a href="https://example.com">External Link</a>
<a href="/internal">Internal Link</a>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "link_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for link facts
        link_facts = [f for f in facts if f.get("concept") == "html:Link"]
        assert len(link_facts) >= 1, "Should find at least one link"

    def test_parse_meta_tags(self):
        """Test parsing HTML meta tags."""
        html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="description" content="Test page">
<meta name="viewport" content="width=device-width">
</head>
<body></body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "meta_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for meta facts
        meta_facts = [f for f in facts if f.get("concept") == "html:Meta"]
        assert len(meta_facts) >= 1, "Should find at least one meta tag"


class TestFrameworkDetection:
    """Tests for framework detection in HTML."""

    def test_detect_vue_directives(self):
        """Test detection of Vue.js directives."""
        html = """<!DOCTYPE html>
<html>
<body>
<div id="app">
    <span v-if="isVisible">Hello</span>
    <button v-on:click="handleClick">Click</button>
    <input v-model="message" />
</div>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "vue_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for Vue directive facts
        vue_facts = [f for f in facts if f.get("concept") == "html:VueDirective"]
        assert len(vue_facts) >= 1, "Should detect Vue.js directives"

    def test_detect_htmx_attributes(self):
        """Test detection of HTMX attributes."""
        html = """<!DOCTYPE html>
<html>
<body>
<button hx-get="/api/data" hx-target="#result">Load Data</button>
<div hx-post="/api/submit" hx-swap="outerHTML">Submit</div>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "htmx_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for HTMX attribute facts
        htmx_facts = [f for f in facts if f.get("concept") == "html:HtmxAttribute"]
        assert len(htmx_facts) >= 1, "Should detect HTMX attributes"

    def test_detect_angular_directives(self):
        """Test detection of Angular directives."""
        html = """<!DOCTYPE html>
<html>
<body>
<div ng-app="myApp">
    <span ng-if="isVisible">Hello</span>
    <button ng-click="handleClick()">Click</button>
    <input ng-model="message" />
</div>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "angular_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for Angular directive facts
        angular_facts = [f for f in facts if f.get("concept") == "html:AngularDirective"]
        assert len(angular_facts) >= 1, "Should detect Angular directives"

    def test_detect_alpine_directives(self):
        """Test detection of Alpine.js directives."""
        html = """<!DOCTYPE html>
<html>
<body>
<div x-data="{ open: false }">
    <button x-on:click="open = !open">Toggle</button>
    <span x-show="open">Visible when open</span>
</div>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "alpine_test")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check for Alpine directive facts
        alpine_facts = [f for f in facts if f.get("concept") == "html:AlpineDirective"]
        assert len(alpine_facts) >= 1, "Should detect Alpine.js directives"


class TestHTMLWithReteNetwork:
    """Tests for loading HTML into RETE network."""

    def test_load_html_into_network(self):
        """Test loading HTML code into a RETE network."""
        html = """<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
<script>
function hello() {
    return "Hello World!";
}
</script>
<button onclick="hello()">Click</button>
</body>
</html>"""
        network = owl_rete_cpp.ReteNetwork()
        count = owl_rete_cpp.load_html_from_string(network, html, "network_test")

        assert count > 0, "Should add facts to the network"

        # Get facts and verify
        facts = network.get_all_facts()
        assert len(facts) > 0, "Network should contain facts"


class TestEmbeddedJavaScript:
    """Tests for JavaScript parsing within HTML."""

    def test_js_function_line_numbers(self):
        """Test that JS function line numbers are adjusted for embedding."""
        html = """<!DOCTYPE html>
<html>
<body>
<script>
function foo() {
    return 1;
}

function bar() {
    return 2;
}
</script>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "line_numbers")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Check that we extracted JavaScript functions
        js_functions = [f for f in facts if f.get("concept") == "js:Function"]
        assert len(js_functions) >= 2, "Should find both JavaScript functions"

    def test_multiple_script_blocks(self):
        """Test parsing multiple script blocks in HTML."""
        html = """<!DOCTYPE html>
<html>
<head>
<script>
function helper() {
    return "helper";
}
</script>
</head>
<body>
<script>
function main() {
    return helper();
}
</script>
</body>
</html>"""
        facts, errors = owl_rete_cpp.parse_html_code(html, "multi_script")

        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # Should have 2 script facts
        script_facts = [f for f in facts if f.get("concept") == "html:Script"]
        assert len(script_facts) >= 2, "Should find both script blocks"

        # Should have 2 JS function facts
        js_functions = [f for f in facts if f.get("concept") == "js:Function"]
        assert len(js_functions) >= 2, "Should find functions from both script blocks"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
