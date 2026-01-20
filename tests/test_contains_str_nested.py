"""
Isolated test for CONTAINS(STR(?var), "substring") pattern.

This test demonstrates a bug in FilterEvaluator where CONTAINS() only
accepts Term arguments, but the grammar allows nested built-in functions
like STR() as the first argument.

Bug location: FilterEvaluator.cpp, evaluate_builtin(), CONTAINS case (lines ~647-675)

The grammar (ReqlParser.g4 line 214) correctly allows:
    CONTAINS L_PAREN expression COMMA expression R_PAREN

But the executor only handles Term, not nested BuiltIn like STR():
    if (std::holds_alternative<Term>(args[0]->content)) {
        ...
    } else {
        throw std::runtime_error("CONTAINS() first argument must be a term");
    }

Fix: Add handling for BuiltIn::STR in CONTAINS (similar to evaluate_comparison).
"""

import pytest
from reter import Reter


class TestContainsWithNestedStr:
    """Test CONTAINS with nested STR() function."""

    @pytest.fixture
    def reter_with_classes(self):
        """Create a Reter instance with Python classes loaded."""
        reter = Reter()
        reter.load_python_code("""
class UserService:
    def get_user(self):
        pass

    def create_user(self):
        pass

class OrderService:
    def get_order(self):
        pass

class UserRepository:
    def find_user(self):
        pass
""", "test_module")
        return reter

    def test_contains_with_variable_works(self, reter_with_classes):
        """Test that CONTAINS(?name, "User") works correctly.

        This should pass - CONTAINS with a variable as first arg is supported.
        """
        # First, verify classes are loaded correctly
        check_result = reter_with_classes.reql("""
            SELECT ?c ?name WHERE {
                ?c concept "py:Class" .
                ?c name ?name
            }
        """)
        print(f"Found {check_result.num_rows} classes")
        if check_result.num_rows > 0:
            print(check_result.to_pandas())

        # Now test CONTAINS filter
        result = reter_with_classes.reql("""
            SELECT ?name WHERE {
                ?c concept "py:Class" .
                ?c name ?name .
                FILTER(CONTAINS(?name, "User"))
            }
        """)

        df = result.to_pandas()
        assert result.num_rows >= 2  # UserService, UserRepository
        for name in df['?name']:
            assert "User" in str(name), f"Expected 'User' in {name}"

    def test_contains_with_str_variable(self, reter_with_classes):
        """Test that CONTAINS(STR(?c), "substring") works correctly.

        STR(?c) converts the variable to its string representation,
        allowing CONTAINS to match against entity identifiers.
        """
        result = reter_with_classes.reql("""
            SELECT ?c ?name WHERE {
                ?c concept "py:Class" .
                ?c name ?name .
                FILTER(CONTAINS(STR(?c), "UserService"))
            }
        """)

        # After the fix, this should return results where the class
        # identifier contains "UserService"
        assert result.num_rows >= 1
        df = result.to_pandas()
        for c_value in df['?c']:
            assert "UserService" in str(c_value)

    def test_contains_str_pattern_from_cadsl(self, reter_with_classes):
        """Test the exact pattern used in describe_class.cadsl.

        The CADSL describe_class tool uses:
            FILTER ( CONTAINS(STR(?c), "{target}") || ?name = "{target}" )

        This pattern should work for fuzzy matching on class identifiers.
        """
        # This is the pattern from describe_class.cadsl
        result = reter_with_classes.reql("""
            SELECT ?c ?name ?file ?line WHERE {
                ?c concept "py:Class" .
                ?c name ?name .
                ?c inFile ?file .
                ?c atLine ?line .
                FILTER ( CONTAINS(STR(?c), "UserService") || ?name = "UserService" )
            }
        """)

        assert result.num_rows >= 1
        df = result.to_pandas()
        # Should find UserService class
        assert any("UserService" in str(name) for name in df['?name'])


class TestOtherStringFunctionsWithNestedStr:
    """Test other string functions that may have the same issue."""

    @pytest.fixture
    def reter_with_classes(self):
        """Create a Reter instance with Python classes loaded."""
        reter = Reter()
        reter.load_python_code("""
class TestUserService:
    def test_method(self):
        pass

class ProductService:
    def get_product(self):
        pass
""", "test_module")
        return reter

    def test_strstarts_with_str_nested(self, reter_with_classes):
        """Test STRSTARTS(STR(?c), "Test") pattern."""
        result = reter_with_classes.reql("""
            SELECT ?c ?name WHERE {
                ?c concept "py:Class" .
                ?c name ?name .
                FILTER(STRSTARTS(STR(?c), "test_module"))
            }
        """)

        # After fix, should return classes whose qualified name starts with "test_module"
        assert result.num_rows >= 1

    def test_strends_with_str_nested(self, reter_with_classes):
        """Test STRENDS(STR(?c), "Service") pattern."""
        result = reter_with_classes.reql("""
            SELECT ?c ?name WHERE {
                ?c concept "py:Class" .
                ?c name ?name .
                FILTER(STRENDS(STR(?c), "Service"))
            }
        """)

        # After fix, should return classes whose qualified name ends with "Service"
        assert result.num_rows >= 1

    def test_regex_with_str_nested(self, reter_with_classes):
        """Test REGEX(STR(?c), ".*Service$") pattern."""
        result = reter_with_classes.reql("""
            SELECT ?c ?name WHERE {
                ?c concept "py:Class" .
                ?c name ?name .
                FILTER(REGEX(STR(?c), ".*Service$"))
            }
        """)

        # After fix, should return classes whose qualified name matches the regex
        assert result.num_rows >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])
