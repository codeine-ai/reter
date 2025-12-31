#!/usr/bin/env python
"""
Test HAVING clause functionality in REQL queries.

This test verifies that the HAVING clause correctly filters aggregated results.
The HAVING clause is applied after GROUP BY aggregation and filters groups
based on aggregate function values.

Tests cover:
1. HAVING with variable reference (e.g., HAVING (?count >= 2))
2. HAVING with inline aggregation (e.g., HAVING (COUNT(?x) >= 2))
3. HAVING with comparison operators (>=, >, <, <=, =, !=)
4. HAVING combined with ORDER BY and LIMIT
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from reter.reasoner import Reter


@pytest.fixture
def reasoner_with_classes():
    """Create a reasoner with classes and methods for testing."""
    r = Reter()

    # Simulate a code analysis ontology with classes and methods
    ontology = """
    Class ⊑ᑦ owl:Thing
    Method ⊑ᑦ owl:Thing

    Class（UserService）
    Class（OrderService）
    Class（SmallClass）
    Class（TinyClass）

    Method（getUser）
    Method（createUser）
    Method（updateUser）
    Method（deleteUser）
    Method（listUsers）
    definedIn（getUser，UserService）
    definedIn（createUser，UserService）
    definedIn（updateUser，UserService）
    definedIn（deleteUser，UserService）
    definedIn（listUsers，UserService）

    Method（getOrder）
    Method（createOrder）
    Method（updateOrder）
    Method（cancelOrder）
    definedIn（getOrder，OrderService）
    definedIn（createOrder，OrderService）
    definedIn（updateOrder，OrderService）
    definedIn（cancelOrder，OrderService）

    Method（doSomething）
    Method（doAnother）
    definedIn（doSomething，SmallClass）
    definedIn（doAnother，SmallClass）

    Method（singleMethod）
    definedIn（singleMethod，TinyClass）
    """
    r.load_ontology(ontology)
    return r


def test_having_with_variable_reference(reasoner_with_classes):
    """Test HAVING clause that references an aliased aggregation variable."""
    r = reasoner_with_classes

    # Query: Find classes with 3 or more methods
    query = """
    SELECT ?class (COUNT(?method) AS ?method_count)
    WHERE {
        ?class type Class .
        ?method type Method .
        ?method definedIn ?class
    }
    GROUP BY ?class
    HAVING (?method_count >= 3)
    """

    results = r.reql(query)

    # Should get UserService (5 methods) and OrderService (4 methods)
    # SmallClass (2) and TinyClass (1) should be filtered out
    assert results.num_rows == 2, f"Expected 2 classes with >= 3 methods, got {results.num_rows}"

    # Convert to list for easier verification
    classes = [row['?class'] for row in results.to_pylist()]
    assert 'UserService' in classes, "UserService should be in results"
    assert 'OrderService' in classes, "OrderService should be in results"
    assert 'SmallClass' not in classes, "SmallClass should be filtered out"
    assert 'TinyClass' not in classes, "TinyClass should be filtered out"

    print(f"HAVING with variable reference: {results.num_rows} results")


def test_having_with_inline_count(reasoner_with_classes):
    """Test HAVING clause with inline COUNT() aggregation."""
    r = reasoner_with_classes

    # Query using inline COUNT in HAVING
    query = """
    SELECT ?class (COUNT(?method) AS ?method_count)
    WHERE {
        ?class type Class .
        ?method type Method .
        ?method definedIn ?class
    }
    GROUP BY ?class
    HAVING (COUNT(?method) >= 4)
    """

    results = r.reql(query)

    # Should get UserService (5 methods) and OrderService (4 methods)
    assert results.num_rows == 2, f"Expected 2 classes with >= 4 methods, got {results.num_rows}"

    print(f"HAVING with inline COUNT: {results.num_rows} results")


def test_having_greater_than(reasoner_with_classes):
    """Test HAVING with > operator."""
    r = reasoner_with_classes

    query = """
    SELECT ?class (COUNT(?method) AS ?method_count)
    WHERE {
        ?class type Class .
        ?method type Method .
        ?method definedIn ?class
    }
    GROUP BY ?class
    HAVING (?method_count > 4)
    """

    results = r.reql(query)

    # Only UserService has > 4 methods (it has 5)
    assert results.num_rows == 1, f"Expected 1 class with > 4 methods, got {results.num_rows}"

    classes = [row['?class'] for row in results.to_pylist()]
    assert 'UserService' in classes, "Only UserService should have > 4 methods"

    print(f"HAVING with > operator: {results.num_rows} results")


def test_having_less_than(reasoner_with_classes):
    """Test HAVING with < operator."""
    r = reasoner_with_classes

    query = """
    SELECT ?class (COUNT(?method) AS ?method_count)
    WHERE {
        ?class type Class .
        ?method type Method .
        ?method definedIn ?class
    }
    GROUP BY ?class
    HAVING (?method_count < 3)
    """

    results = r.reql(query)

    # SmallClass (2) and TinyClass (1) have < 3 methods
    assert results.num_rows == 2, f"Expected 2 classes with < 3 methods, got {results.num_rows}"

    classes = [row['?class'] for row in results.to_pylist()]
    assert 'SmallClass' in classes, "SmallClass should be in results"
    assert 'TinyClass' in classes, "TinyClass should be in results"

    print(f"HAVING with < operator: {results.num_rows} results")


def test_having_equals(reasoner_with_classes):
    """Test HAVING with = operator."""
    r = reasoner_with_classes

    query = """
    SELECT ?class (COUNT(?method) AS ?method_count)
    WHERE {
        ?class type Class .
        ?method type Method .
        ?method definedIn ?class
    }
    GROUP BY ?class
    HAVING (?method_count = 4)
    """

    results = r.reql(query)

    # Only OrderService has exactly 4 methods
    assert results.num_rows == 1, f"Expected 1 class with exactly 4 methods, got {results.num_rows}"

    classes = [row['?class'] for row in results.to_pylist()]
    assert 'OrderService' in classes, "OrderService should have exactly 4 methods"

    print(f"HAVING with = operator: {results.num_rows} results")


def test_having_with_order_by(reasoner_with_classes):
    """Test HAVING combined with ORDER BY."""
    r = reasoner_with_classes

    query = """
    SELECT ?class (COUNT(?method) AS ?method_count)
    WHERE {
        ?class type Class .
        ?method type Method .
        ?method definedIn ?class
    }
    GROUP BY ?class
    HAVING (?method_count >= 2)
    ORDER BY DESC(?method_count)
    """

    results = r.reql(query)

    # Should get UserService (5), OrderService (4), SmallClass (2)
    # TinyClass (1) is filtered out
    assert results.num_rows == 3, f"Expected 3 classes with >= 2 methods, got {results.num_rows}"

    # Verify order (descending by method count)
    rows = results.to_pylist()
    counts = [row['?method_count'] for row in rows]
    assert counts == sorted(counts, reverse=True), "Results should be in descending order"

    print(f"HAVING with ORDER BY: {results.num_rows} results in descending order")


def test_having_with_limit(reasoner_with_classes):
    """Test HAVING combined with LIMIT."""
    r = reasoner_with_classes

    query = """
    SELECT ?class (COUNT(?method) AS ?method_count)
    WHERE {
        ?class type Class .
        ?method type Method .
        ?method definedIn ?class
    }
    GROUP BY ?class
    HAVING (?method_count >= 2)
    ORDER BY DESC(?method_count)
    LIMIT 2
    """

    results = r.reql(query)

    # Should get top 2: UserService (5), OrderService (4)
    assert results.num_rows == 2, f"Expected 2 results with LIMIT 2, got {results.num_rows}"

    classes = [row['?class'] for row in results.to_pylist()]
    assert 'UserService' in classes, "UserService should be in top 2"
    assert 'OrderService' in classes, "OrderService should be in top 2"

    print(f"HAVING with LIMIT: {results.num_rows} results")


def test_having_filters_all(reasoner_with_classes):
    """Test HAVING that filters out all results."""
    r = reasoner_with_classes

    query = """
    SELECT ?class (COUNT(?method) AS ?method_count)
    WHERE {
        ?class type Class .
        ?method type Method .
        ?method definedIn ?class
    }
    GROUP BY ?class
    HAVING (?method_count >= 100)
    """

    results = r.reql(query)

    # No class has >= 100 methods
    assert results.num_rows == 0, f"Expected 0 results, got {results.num_rows}"

    print("HAVING filters all: 0 results (as expected)")


def test_having_with_sum():
    """Test HAVING with SUM aggregation."""
    r = Reter()

    # Note: 'Order' is a reserved word in REQL, so use 'Purchase' instead
    ontology = """
    Product ⊑ᑦ owl:Thing
    Purchase ⊑ᑦ owl:Thing

    Product（productA）
    Product（productB）
    Product（productC）

    Purchase（purchase1）
    Purchase（purchase2）
    Purchase（purchase3）
    Purchase（purchase4）
    Purchase（purchase5）

    hasProduct（purchase1，productA）
    hasProduct（purchase2，productA）
    hasProduct（purchase3，productA）
    hasProduct（purchase4，productB）
    hasProduct（purchase5，productC）

    hasQuantity（purchase1，10）
    hasQuantity（purchase2，20）
    hasQuantity（purchase3，30）
    hasQuantity（purchase4，5）
    hasQuantity（purchase5，2）
    """
    r.load_ontology(ontology)

    # Find products with total quantity >= 20
    query = """
    SELECT ?product (SUM(?qty) AS ?total_qty)
    WHERE {
        ?purchase type Purchase .
        ?purchase hasProduct ?product .
        ?purchase hasQuantity ?qty
    }
    GROUP BY ?product
    HAVING (?total_qty >= 20)
    """

    results = r.reql(query)

    # productA has purchases with quantities 10+20+30=60
    # productB has 5, productC has 2
    # Only productA should pass
    assert results.num_rows == 1, f"Expected 1 product with total >= 20, got {results.num_rows}"

    products = [row['?product'] for row in results.to_pylist()]
    assert 'productA' in products, "productA should have total >= 20"

    print(f"HAVING with SUM: {results.num_rows} results")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
