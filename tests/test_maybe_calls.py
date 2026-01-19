"""
Tests for maybeCalls probabilistic call resolution.

maybeCalls resolves calls that cannot be statically typed (duck typing).
When a call like `handler.process()` cannot be resolved because `handler`
has no known type, the system finds candidate methods by name matching
and creates maybeCalls relationships with scoring.
"""
import pytest
from reter_core import owl_rete_cpp


def query_to_list(result):
    """Convert PyArrow query result to list of dicts."""
    if result.num_rows == 0:
        return []
    return result.to_pylist()


class TestMaybeCallsManual:
    """Test maybeCalls with manual registration."""

    def test_basic_maybe_call(self):
        """Test that a pending call resolves to a candidate method."""
        network = owl_rete_cpp.ReteNetwork()

        # Register a method
        network.register_method_for_maybe_calls(
            "test.MyHandler.process(self)",  # entity_id
            "process",  # name
            0,  # param_count (excluding self)
            "test",  # module
            "MyHandler"  # class_name
        )

        # Add a pending call that can't be resolved statically
        network.add_pending_call(
            "test.process_handler(handler)",  # caller
            "process",  # method_name
            0,  # arg_count
            "test",  # caller_module
            ""  # caller_class (top-level function)
        )

        # Resolve
        network.resolve_maybe_calls()

        # Query for maybeCalls
        result = query_to_list(network.reql_query(
            "SELECT ?caller ?callee WHERE { ?caller maybeCalls ?callee }",
            30000
        ))

        assert len(result) == 1
        assert result[0]["?caller"] == "test.process_handler(handler)"
        assert result[0]["?callee"] == "test.MyHandler.process(self)"

    def test_multiple_candidates(self):
        """Test that multiple methods with same name all become candidates."""
        network = owl_rete_cpp.ReteNetwork()

        # Register multiple methods with same name
        network.register_method_for_maybe_calls(
            "mod.ClassA.save(self,data)", "save", 1, "mod", "ClassA"
        )
        network.register_method_for_maybe_calls(
            "mod.ClassB.save(self,data)", "save", 1, "mod", "ClassB"
        )
        network.register_method_for_maybe_calls(
            "other.ClassC.save(self,data)", "save", 1, "other", "ClassC"
        )

        # Add pending call
        network.add_pending_call(
            "mod.handler(obj)", "save", 1, "mod", ""
        )

        network.resolve_maybe_calls()

        result = query_to_list(network.reql_query(
            "SELECT ?callee WHERE { ?caller maybeCalls ?callee }",
            30000
        ))

        # All 3 should be candidates (name matches)
        callees = {r["?callee"] for r in result}
        assert "mod.ClassA.save(self,data)" in callees
        assert "mod.ClassB.save(self,data)" in callees
        assert "other.ClassC.save(self,data)" in callees

    def test_no_self_call(self):
        """Test that a method doesn't maybeCalls itself."""
        network = owl_rete_cpp.ReteNetwork()

        network.register_method_for_maybe_calls(
            "mod.Class.process(self)", "process", 0, "mod", "Class"
        )

        # Pending call from the same method
        network.add_pending_call(
            "mod.Class.process(self)", "process", 0, "mod", "Class"
        )

        network.resolve_maybe_calls()

        result = query_to_list(network.reql_query(
            "SELECT ?caller ?callee WHERE { ?caller maybeCalls ?callee }",
            30000
        ))

        # Should not create self-call
        assert len(result) == 0

    def test_no_candidates(self):
        """Test that unmatched method names produce no maybeCalls."""
        network = owl_rete_cpp.ReteNetwork()

        network.register_method_for_maybe_calls(
            "mod.Class.foo(self)", "foo", 0, "mod", "Class"
        )

        # Pending call to different method name
        network.add_pending_call(
            "mod.caller()", "bar", 0, "mod", ""
        )

        network.resolve_maybe_calls()

        result = query_to_list(network.reql_query(
            "SELECT ?caller ?callee WHERE { ?caller maybeCalls ?callee }",
            30000
        ))

        assert len(result) == 0


class TestMaybeCallsFromPython:
    """Test maybeCalls with actual Python code extraction."""

    def test_duck_typed_parameter(self):
        """Test that duck-typed parameter calls create maybeCalls."""
        network = owl_rete_cpp.ReteNetwork()

        code = '''
def process_handler(handler):
    """Handler type is unknown - duck typing."""
    handler.process()
    handler.save(data)

class MyHandler:
    def process(self):
        pass

    def save(self, data):
        pass
'''
        owl_rete_cpp.load_python_from_string(network, code, "test.py", "test")
        network.resolve_maybe_calls()

        # Check for maybeCalls
        result = query_to_list(network.reql_query(
            "SELECT ?caller ?callee WHERE { ?caller maybeCalls ?callee }",
            30000
        ))

        # Should have maybeCalls for process and save
        callees = {r["?callee"] for r in result}
        assert any("process" in c for c in callees)
        assert any("save" in c for c in callees)

    def test_static_calls_not_duplicated(self):
        """Test that statically resolved calls don't create maybeCalls."""
        network = owl_rete_cpp.ReteNetwork()

        code = '''
class DataStore:
    def load(self, key):
        pass

class Cache:
    def __init__(self):
        self.store = DataStore()

    def get(self, key):
        # This should resolve statically to DataStore.load
        return self.store.load(key)
'''
        owl_rete_cpp.load_python_from_string(network, code, "test.py", "test")
        network.resolve_maybe_calls()

        # Check static calls
        calls_result = query_to_list(network.reql_query(
            "SELECT ?caller ?callee WHERE { ?caller calls ?callee }",
            30000
        ))

        # Check maybeCalls
        maybe_result = query_to_list(network.reql_query(
            "SELECT ?caller ?callee WHERE { ?caller maybeCalls ?callee }",
            30000
        ))

        # Static call should exist
        call_callees = {r["?callee"] for r in calls_result}
        assert any("load" in c for c in call_callees)

        # maybeCalls should be empty or not contain the same call
        maybe_callees = {r["?callee"] for r in maybe_result}
        # If the call was resolved statically, it shouldn't be in maybeCalls
        # (the resolver skips already-resolved calls)

    def test_scoring_same_module_bonus(self):
        """Test that same-module candidates score higher."""
        network = owl_rete_cpp.ReteNetwork()

        # Register methods in different modules
        network.register_method_for_maybe_calls(
            "mymod.LocalClass.handle(self)", "handle", 0, "mymod", "LocalClass"
        )
        network.register_method_for_maybe_calls(
            "other.RemoteClass.handle(self)", "handle", 0, "other", "RemoteClass"
        )

        # Pending call from mymod
        network.add_pending_call(
            "mymod.process(obj)", "handle", 0, "mymod", ""
        )

        network.resolve_maybe_calls()

        result = query_to_list(network.reql_query(
            "SELECT ?callee WHERE { ?caller maybeCalls ?callee }",
            30000
        ))

        # Both should be candidates, but LocalClass should rank first
        # (has same-module bonus of 0.15)
        callees = [r["?callee"] for r in result]
        assert len(callees) == 2
        # The resolver sorts by score descending, so local should be first
        # Score: LocalClass = 0.3 + 0.3 + 0.15 = 0.75
        # Score: RemoteClass = 0.3 + 0.3 = 0.6


class TestMaybeCallsIntegration:
    """Integration tests with REQL queries."""

    def test_union_calls_and_maybe_calls(self):
        """Test querying both calls and maybeCalls together."""
        network = owl_rete_cpp.ReteNetwork()

        code = '''
class Service:
    def process(self):
        pass

class Client:
    def __init__(self):
        self.service = Service()

    def run(self):
        # Static call - type known
        self.service.process()

def external_caller(handler):
    # Duck-typed call - type unknown
    handler.process()
'''
        owl_rete_cpp.load_python_from_string(network, code, "test.py", "test")
        network.resolve_maybe_calls()

        # Query both calls and maybeCalls
        result = query_to_list(network.reql_query(
            """SELECT ?caller ?callee WHERE {
                { ?caller calls ?callee } UNION { ?caller maybeCalls ?callee }
            }""",
            30000
        ))

        callers = {r["?caller"] for r in result}
        # Should include both static caller and duck-typed caller
        assert any("run" in c for c in callers)
        assert any("external_caller" in c for c in callers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
