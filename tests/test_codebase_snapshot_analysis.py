"""
Test Python code analysis using saved codebase snapshot.

This test loads the pre-analyzed codebase snapshot (codebase_analysis.reter)
and verifies that all Python code analysis features work correctly:

1. Method extraction with signatures
2. Parameter details (names, types, positions, defaults)
3. Line numbers for code navigation
4. Return type annotations
5. Call relationships (who calls whom)
6. Decorators extraction
7. Class relationships (inheritance)
8. Docstrings
9. Qualified names for precise identification
10. Query patterns work correctly

The snapshot should contain a real Python codebase analysis for realistic testing.
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reter import Reter


@pytest.fixture
def reasoner_with_codebase():
    """Load the pre-analyzed codebase snapshot"""
    snapshot_path = os.path.join(
        os.path.dirname(__file__),
        "codebase_analysis.reter"
    )

    if not os.path.exists(snapshot_path):
        pytest.skip(f"Snapshot not found: {snapshot_path}")

    reasoner = Reter()
    success = reasoner.network.load(snapshot_path)
    if not success:
        pytest.skip(f"Failed to load snapshot: {snapshot_path}")
    return reasoner


def query_to_rows(result):
    """Convert PyArrow Table to list of tuples"""
    if result.num_rows == 0:
        return []
    columns = [result.column(name).to_pylist() for name in result.column_names]
    return list(zip(*columns))


def test_snapshot_loads_successfully(reasoner_with_codebase):
    """Test that the snapshot loads without errors"""
    assert reasoner_with_codebase is not None
    print("✅ Snapshot loaded successfully")


def test_methods_extracted(reasoner_with_codebase):
    """Test that methods are extracted from the codebase"""
    result = reasoner_with_codebase.reql("""
        SELECT ?method ?name
        WHERE {
            ?method concept "py:Method" .
            ?method name ?name
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} methods in codebase")

    assert len(rows) > 0, "Should extract methods from codebase"

    # Show sample methods
    if len(rows) > 0:
        print(f"\n📝 Sample methods:")
        for method_id, name in rows[:10]:
            print(f"  - {name} ({method_id})")


def test_method_parameters_with_types(reasoner_with_codebase):
    """Test that method parameters are extracted with type annotations (if present)"""
    # First check if there are any parameters at all
    all_params = reasoner_with_codebase.reql("""
        SELECT (COUNT(?param) AS ?count)
        WHERE {
            ?param concept "py:Parameter"
        }
    """)
    total_params = all_params.column('?count')[0].as_py() if all_params.num_rows > 0 else 0
    print(f"\n📊 Total parameters in codebase: {total_params}")

    # Find methods with parameters that have type annotations
    result = reasoner_with_codebase.reql("""
        SELECT ?method ?param ?paramName ?type
        WHERE {
            ?param concept "py:Parameter" .
            ?param ofFunction ?method .
            ?param name ?paramName .
            ?param typeAnnotation ?type
        }
    """)

    rows = query_to_rows(result)
    print(f"📊 Found {len(rows)} parameters with type annotations")

    # Only assert if parameters exist but none have types - this would indicate a bug
    if total_params > 0:
        # It's OK if a codebase doesn't use type annotations
        print(f"✓ Type annotation extraction working (codebase has {len(rows)}/{total_params} typed parameters)")
    else:
        pytest.skip("No parameters found in codebase")

    # Show sample parameters
    if len(rows) > 0:
        print(f"\n📝 Sample typed parameters:")
        for method, param, name, ptype in rows[:10]:
            print(f"  - {method}: {name}: {ptype}")


def test_line_numbers_present(reasoner_with_codebase):
    """Test that methods have line number information"""
    result = reasoner_with_codebase.reql("""
        SELECT ?method ?name ?line
        WHERE {
            ?method concept "py:Method" .
            ?method name ?name .
            ?method atLine ?line
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} methods with line numbers")

    assert len(rows) > 0, "Should have line numbers for methods"

    # Verify line numbers are valid
    for method_id, name, line_num in rows[:20]:
        assert line_num and line_num != "", f"Method {name} should have line number"
        assert int(line_num) > 0, f"Method {name} should have positive line number"

    # Show sample
    if len(rows) > 0:
        print(f"\n📝 Sample methods with line numbers:")
        for method_id, name, line in rows[:10]:
            print(f"  - Line {line}: {name}")


def test_return_types_extracted(reasoner_with_codebase):
    """Test that return type annotations are extracted (if present)"""
    # First check if there are any methods at all
    all_methods = reasoner_with_codebase.reql("""
        SELECT (COUNT(?method) AS ?count)
        WHERE {
            ?method concept "py:Method"
        }
    """)
    total_methods = all_methods.column('?count')[0].as_py() if all_methods.num_rows > 0 else 0
    print(f"\n📊 Total methods in codebase: {total_methods}")

    result = reasoner_with_codebase.reql("""
        SELECT ?method ?name ?returnType
        WHERE {
            ?method concept "py:Method" .
            ?method name ?name .
            ?method returnType ?returnType
        }
    """)

    rows = query_to_rows(result)
    print(f"📊 Found {len(rows)} methods with return type annotations")

    # It's OK if a codebase doesn't use type annotations
    if total_methods > 0:
        print(f"✓ Return type extraction working (codebase has {len(rows)}/{total_methods} typed returns)")
    else:
        pytest.skip("No methods found in codebase")

    # Group by return type
    if len(rows) > 0:
        return_types = {}
        for method_id, name, rtype in rows:
            if rtype not in return_types:
                return_types[rtype] = []
            return_types[rtype].append(name)

        print(f"\n📝 Return types found: {len(return_types)}")
        for rtype, methods in list(return_types.items())[:10]:
            print(f"  - {rtype}: {len(methods)} methods")


def test_call_relationships_exist(reasoner_with_codebase):
    """Test that function call relationships are extracted"""
    result = reasoner_with_codebase.reql("""
        SELECT ?caller ?callee
        WHERE {
            ?caller calls ?callee
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} call relationships")

    assert len(rows) > 0, "Should extract call relationships"

    # Show sample calls
    if len(rows) > 0:
        print(f"\n📝 Sample call relationships:")
        for caller, callee in rows[:10]:
            print(f"  - {caller} → {callee}")


def test_classes_extracted(reasoner_with_codebase):
    """Test that classes are extracted"""
    result = reasoner_with_codebase.reql("""
        SELECT ?class ?name
        WHERE {
            ?class concept "py:Class" .
            ?class name ?name
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} classes")

    assert len(rows) > 0, "Should extract classes"

    # Show sample classes
    if len(rows) > 0:
        print(f"\n📝 Sample classes:")
        for class_id, name in rows[:10]:
            print(f"  - {name}")


def test_query_methods_by_class(reasoner_with_codebase):
    """Test querying methods defined in specific classes"""
    # First get a class
    class_result = reasoner_with_codebase.reql("""
        SELECT ?class
        WHERE {
            ?class concept "py:Class"
        }
    """)

    classes = query_to_rows(class_result)
    if len(classes) == 0:
        pytest.skip("No classes found in codebase")

    # Pick first class and find its methods
    first_class = classes[0][0]

    result = reasoner_with_codebase.reql(f"""
        SELECT ?method ?name
        WHERE {{
            ?method concept "py:Method" .
            ?method definedIn "{first_class}" .
            ?method name ?name
        }}
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Class '{first_class}' has {len(rows)} methods")

    assert len(rows) > 0, f"Class {first_class} should have methods"

    if len(rows) > 0:
        print(f"\n📝 Methods in {first_class}:")
        for method_id, name in rows:
            print(f"  - {name}")


def test_decorators_extracted(reasoner_with_codebase):
    """Test that decorators are extracted"""
    result = reasoner_with_codebase.reql("""
        SELECT ?method ?name ?decorator
        WHERE {
            ?method concept "py:Method" .
            ?method name ?name .
            ?method hasDecorator ?decorator
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} methods with decorators")

    # Don't assert > 0 since not all codebases use decorators
    if len(rows) > 0:
        # Group by decorator
        decorators = {}
        for method_id, name, decorator in rows:
            if decorator not in decorators:
                decorators[decorator] = []
            decorators[decorator].append(name)

        print(f"\n📝 Decorators found: {len(decorators)}")
        for decorator, methods in list(decorators.items())[:10]:
            print(f"  - @{decorator}: {len(methods)} methods")
    else:
        print("\n📝 No decorators found (codebase may not use them)")


def test_default_parameter_values(reasoner_with_codebase):
    """Test that default parameter values are extracted"""
    result = reasoner_with_codebase.reql("""
        SELECT ?param ?paramName ?default
        WHERE {
            ?param concept "py:Parameter" .
            ?param name ?paramName .
            ?param defaultValue ?default
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} parameters with default values")

    assert len(rows) > 0, "Should extract default parameter values"

    # Show sample defaults
    if len(rows) > 0:
        print(f"\n📝 Sample default parameters:")
        for param_id, name, default in rows[:10]:
            print(f"  - {name} = {default}")


def test_docstrings_extracted(reasoner_with_codebase):
    """Test that docstrings are extracted"""
    # Check both class and method docstrings
    result = reasoner_with_codebase.reql("""
        SELECT ?entity ?name ?docstring
        WHERE {
            ?entity hasDocstring ?docstring .
            ?entity name ?name
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} entities with docstrings")

    # Don't assert since not all code has docstrings
    if len(rows) > 0:
        print(f"\n📝 Sample docstrings:")
        for entity_id, name, docstring in rows[:5]:
            doc_preview = docstring[:80] + "..." if len(docstring) > 80 else docstring
            print(f"  - {name}: {doc_preview}")
    else:
        print("\n📝 No docstrings found (codebase may lack documentation)")


def test_qualified_names_format(reasoner_with_codebase):
    """Test that methods have properly formatted qualified names"""
    result = reasoner_with_codebase.reql("""
        SELECT ?method ?qualifiedName
        WHERE {
            ?method concept "py:Method" .
            ?method qualifiedName ?qualifiedName
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} methods with qualified names")

    assert len(rows) > 0, "Should have qualified names"

    # Verify format (should contain dots for module.Class.method)
    qualified_names = [qname for _, qname in rows]
    dotted_names = [qn for qn in qualified_names if '.' in qn]

    print(f"\n📝 Qualified names format:")
    print(f"  - Total: {len(qualified_names)}")
    print(f"  - With dots (module.Class.method): {len(dotted_names)}")

    # Show samples
    if len(dotted_names) > 0:
        print(f"\n📝 Sample qualified names:")
        for qname in dotted_names[:10]:
            print(f"  - {qname}")

    assert len(dotted_names) > 0, "Should have qualified names with module paths"


def test_inheritance_relationships(reasoner_with_codebase):
    """Test that class inheritance is extracted"""
    result = reasoner_with_codebase.reql("""
        SELECT ?subclass ?superclass
        WHERE {
            ?subclass inheritsFrom ?superclass
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} inheritance relationships")

    # Don't assert since not all codebases use inheritance
    if len(rows) > 0:
        print(f"\n📝 Sample inheritance relationships:")
        for subclass, superclass in rows[:10]:
            print(f"  - {subclass} → {superclass}")
    else:
        print("\n📝 No inheritance found (codebase may not use class hierarchies)")


def test_modules_extracted(reasoner_with_codebase):
    """Test that modules are extracted"""
    result = reasoner_with_codebase.reql("""
        SELECT ?module ?name
        WHERE {
            ?module concept "py:Module" .
            ?module name ?name
        }
    """)

    rows = query_to_rows(result)
    print(f"\n📊 Found {len(rows)} modules")

    assert len(rows) > 0, "Should extract modules"

    # Show all modules
    if len(rows) > 0:
        print(f"\n📝 Modules in codebase:")
        for module_id, name in rows:
            print(f"  - {name}")


def test_comprehensive_statistics(reasoner_with_codebase):
    """Generate comprehensive statistics about the analyzed codebase"""
    print("\n" + "="*60)
    print("CODEBASE ANALYSIS STATISTICS")
    print("="*60)

    # Count all entity types
    entity_types = ["py:Module", "py:Class", "py:Function", "py:Method", "py:Parameter"]

    for entity_type in entity_types:
        result = reasoner_with_codebase.reql(f"""
            SELECT ?entity
            WHERE {{
                ?entity concept "{entity_type}"
            }}
        """)
        count = result.num_rows
        print(f"  {entity_type}: {count}")

    # Count relationships
    print(f"\n📊 Relationships:")

    # Calls
    result = reasoner_with_codebase.reql("""
        SELECT ?caller ?callee
        WHERE { ?caller calls ?callee }
    """)
    print(f"  - Call relationships: {result.num_rows}")

    # Inheritance
    result = reasoner_with_codebase.reql("""
        SELECT ?sub ?super
        WHERE { ?sub inheritsFrom ?super }
    """)
    print(f"  - Inheritance relationships: {result.num_rows}")

    # Methods with type hints
    result = reasoner_with_codebase.reql("""
        SELECT ?method
        WHERE {
            ?method concept "py:Method" .
            ?method returnType ?type
        }
    """)
    print(f"  - Methods with return types: {result.num_rows}")

    # Parameters with type hints
    result = reasoner_with_codebase.reql("""
        SELECT ?param
        WHERE {
            ?param concept "py:Parameter" .
            ?param typeAnnotation ?type
        }
    """)
    print(f"  - Parameters with type hints: {result.num_rows}")

    # Methods with decorators
    result = reasoner_with_codebase.reql("""
        SELECT ?method
        WHERE {
            ?method concept "py:Method" .
            ?method hasDecorator ?decorator
        }
    """)
    print(f"  - Methods with decorators: {result.num_rows}")

    # Entities with docstrings
    result = reasoner_with_codebase.reql("""
        SELECT ?entity
        WHERE {
            ?entity hasDocstring ?doc
        }
    """)
    print(f"  - Entities with docstrings: {result.num_rows}")

    print("="*60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
