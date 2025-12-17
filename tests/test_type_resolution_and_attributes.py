"""
Test type resolution and class attribute detection in Python code analysis.

Tests the new features added to PythonFactExtractionVisitor:
- Type tracking from constructor calls
- Class attribute detection with types
- Attribute visibility detection (public/private/protected)
- Method call resolution using type inference
- Cross-method type tracking
"""

import pytest
from reter import Reter
import tempfile
import os


@pytest.fixture
def reter_instance():
    """Create a fresh Reter instance for each test."""
    return Reter()


@pytest.fixture
def sample_code_with_attributes():
    """Sample Python code with various class attributes."""
    return '''
class PluginManager:
    """Manages plugins with different visibility levels."""

    def __init__(self, config):
        # Public attributes
        self.plugins = {}
        self.plugin_loader = PluginLoader()

        # Protected attributes (single underscore)
        self._internal_state = StateManager()
        self._cache = CacheManager()

        # Private attributes (double underscore - name mangling)
        self.__secret_key = SecretManager()
        self.__config = config

    def load_plugin(self, name):
        """Load a plugin by name."""
        plugin = self.plugin_loader.load(name)
        self.plugins[name] = plugin
        return plugin

    def get_state(self):
        """Get internal state."""
        return self._internal_state.get_current()

class PluginLoader:
    """Loads plugins from disk."""

    def load(self, name):
        """Load a plugin."""
        return Plugin(name)

class Plugin:
    """Represents a plugin."""

    def __init__(self, name):
        self.name = name

class StateManager:
    """Manages state."""

    def get_current(self):
        return "current_state"

class CacheManager:
    """Manages cache."""
    pass

class SecretManager:
    """Manages secrets."""
    pass
'''


@pytest.fixture
def sample_code_with_method_calls():
    """Sample Python code with method calls to test resolution."""
    return '''
class Server:
    """Main server class."""

    def __init__(self):
        self.manager = PluginManager()
        self.config = ConfigManager()

    def initialize(self):
        """Initialize the server."""
        # Method calls that should be resolved
        self.manager.load_all_plugins()
        self.config.validate()
        self.manager.get_status()

    def run(self):
        """Run the server."""
        status = self.manager.check_health()
        return status

class PluginManager:
    """Plugin manager."""

    def load_all_plugins(self):
        """Load all plugins."""
        pass

    def get_status(self):
        """Get status."""
        pass

    def check_health(self):
        """Check health."""
        return "healthy"

class ConfigManager:
    """Configuration manager."""

    def validate(self):
        """Validate configuration."""
        pass
'''


class TestClassAttributeDetection:
    """Test detection of class attributes and their properties."""

    def test_public_attributes_detected(self, reter_instance, sample_code_with_attributes):
        """Test that public attributes are correctly detected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_attributes)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Query for public attributes using REQL
            result = reter_instance.reql("""
                SELECT ?attr
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr name "plugins" .
                    ?attr visibility "public"
                }
            """)

            assert result.num_rows > 0, "Public attribute 'plugins' should be detected"

            # Check plugin_loader attribute
            result = reter_instance.reql("""
                SELECT ?attr
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr name "plugin_loader" .
                    ?attr visibility "public"
                }
            """)

            assert result.num_rows > 0, "Public attribute 'plugin_loader' should be detected"

        finally:
            os.unlink(temp_path)

    def test_protected_attributes_detected(self, reter_instance, sample_code_with_attributes):
        """Test that protected attributes (single underscore) are correctly detected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_attributes)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Query for protected attributes using REQL
            result = reter_instance.reql("""
                SELECT ?attr
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr name "_internal_state" .
                    ?attr visibility "protected"
                }
            """)

            assert result.num_rows > 0, "Protected attribute '_internal_state' should be detected"

            # Check _cache attribute
            result = reter_instance.reql("""
                SELECT ?attr
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr name "_cache" .
                    ?attr visibility "protected"
                }
            """)

            assert result.num_rows > 0, "Protected attribute '_cache' should be detected"

        finally:
            os.unlink(temp_path)

    def test_private_attributes_detected(self, reter_instance, sample_code_with_attributes):
        """Test that private attributes (double underscore) are correctly detected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_attributes)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Query for private attributes using REQL
            result = reter_instance.reql("""
                SELECT ?attr
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr name "__secret_key" .
                    ?attr visibility "private"
                }
            """)

            assert result.num_rows > 0, "Private attribute '__secret_key' should be detected"

            # Check __config attribute
            result = reter_instance.reql("""
                SELECT ?attr
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr name "__config" .
                    ?attr visibility "private"
                }
            """)

            assert result.num_rows > 0, "Private attribute '__config' should be detected"

        finally:
            os.unlink(temp_path)

    def test_attribute_types_detected(self, reter_instance, sample_code_with_attributes):
        """Test that attribute types are correctly inferred from constructor calls."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_attributes)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Query for attribute with specific type using REQL
            result = reter_instance.reql("""
                SELECT ?attr ?type
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr name "plugin_loader" .
                    ?attr hasType ?type
                }
            """)

            assert result.num_rows > 0, "Attribute 'plugin_loader' should have type"

            # Verify the type is correct (should be PluginLoader from same module)
            if result.num_rows > 0:
                type_value = result.column('?type')[0].as_py()
                assert "PluginLoader" in type_value, f"Expected PluginLoader type, got {type_value}"

        finally:
            os.unlink(temp_path)

    def test_attributes_have_class_association(self, reter_instance, sample_code_with_attributes):
        """Test that attributes are associated with their parent class."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_attributes)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Query for attribute with class association using definedIn property
            result = reter_instance.reql("""
                SELECT ?attr ?class
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr name "plugins" .
                    ?attr definedIn ?class
                }
            """)

            assert result.num_rows > 0, "Attribute should be associated with class"

            # Verify the class name
            if result.num_rows > 0:
                class_value = result.column('?class')[0].as_py()
                assert "PluginManager" in class_value, f"Expected PluginManager class, got {class_value}"

        finally:
            os.unlink(temp_path)


class TestMethodCallResolution:
    """Test method call resolution using type inference."""

    def test_method_to_method_calls(self, reter_instance, sample_code_with_method_calls):
        """Test that method-to-method calls within same class are resolved."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_method_calls)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Query for calls relationship
            result = reter_instance.reql("""
                SELECT ?caller ?callee
                WHERE {
                    ?caller calls ?callee
                }
            """)

            assert result.num_rows > 0, "Should find method calls"

        finally:
            os.unlink(temp_path)

    def test_cross_object_method_calls(self, reter_instance, sample_code_with_method_calls):
        """Test that method calls on other objects are resolved using type info."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_method_calls)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Look for calls from Server.initialize to PluginManager.load_all_plugins
            result = reter_instance.reql("""
                SELECT ?caller ?callee
                WHERE {
                    ?caller calls ?callee .
                    ?caller name "initialize" .
                    ?callee name "load_all_plugins"
                }
            """)

            assert result.num_rows > 0, "Should resolve cross-object method calls"

        finally:
            os.unlink(temp_path)

    def test_method_call_chain_resolution(self, reter_instance, sample_code_with_method_calls):
        """Test that chained method calls are resolved correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_method_calls)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Query for any calls from initialize method
            result = reter_instance.reql("""
                SELECT ?caller ?callee
                WHERE {
                    ?caller calls ?callee .
                    ?caller name "initialize"
                }
            """)

            # Should have multiple calls from initialize method
            assert result.num_rows >= 3, f"Expected at least 3 calls from initialize, got {result.num_rows}"

        finally:
            os.unlink(temp_path)


class TestTypeTracking:
    """Test type tracking across methods and scopes."""

    def test_type_persists_across_methods(self, reter_instance, sample_code_with_method_calls):
        """Test that types assigned in __init__ are visible in other methods."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_method_calls)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Look for calls that rely on types from __init__
            result = reter_instance.reql("""
                SELECT ?caller ?callee
                WHERE {
                    ?caller calls ?callee .
                    ?callee name "load_all_plugins"
                }
            """)

            # This call is in initialize() but type is set in __init__()
            assert result.num_rows > 0, "Type tracking should persist across methods"

        finally:
            os.unlink(temp_path)

    def test_multiple_attributes_same_method(self, reter_instance, sample_code_with_method_calls):
        """Test that multiple attributes in same method are tracked correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code_with_method_calls)
            f.flush()
            temp_path = f.name

        try:
            reter_instance.load_python_file(temp_path)

            # Check that both manager and config attributes exist using definedIn property
            result = reter_instance.reql("""
                SELECT ?attr
                WHERE {
                    ?attr concept "py:Attribute" .
                    ?attr definedIn ?class .
                    ?class name "Server"
                }
            """)

            # Should have at least manager and config attributes
            assert result.num_rows >= 2, f"Expected at least 2 attributes, got {result.num_rows}"

        finally:
            os.unlink(temp_path)
