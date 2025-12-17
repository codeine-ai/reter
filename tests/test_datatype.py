"""
Test for cls-svf1b (datatype restriction) rule
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


def test_datatype_restriction():
    """Test datatype restriction (cls-svf1b) with type validation"""
    print("\n" + "=" * 60)
    print("TEST: Datatype Restriction (cls-svf1b)")
    print("=" * 60)

    reasoner = Reter()

    # Define Adult as: ∃hasAge.(≤ ⊔ ≥ xsd:integer)
    # Grammar: SOME node abstract_bound -> some_value_restriction
    # abstract_bound: LE OR GE ID -> dt_bound
    ontology = """
    Adult ≡ᑦ ∃hasAge （≤ ⊔ ≥ xsd:integer）
    Person（John）
    Person（Mary）
    Person（Bob）
    hasAge（John， 30）
    hasAge（Mary， 25）
    hasAge（Bob， 'twenty'）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check if John and Mary are instances of Adult restriction
    adults = reasoner.get_instances('Adult')
    print(f"\nInstances of Adult (hasAge with integer value): {adults}")

    assert 'John' in adults, "John should satisfy hasAge restriction (has hasAge with integer)"
    assert 'Mary' in adults, "Mary should satisfy hasAge restriction (has hasAge with integer)"
    assert 'Bob' not in adults, "Bob should NOT satisfy hasAge restriction (has string age, not integer)"

    print("✓ Test passed: Datatype restriction with type validation works correctly")


def test_datatype_with_literal():
    """Test datatype restriction with rdfs:Literal"""
    print("\n" + "=" * 60)
    print("TEST: Datatype Restriction with rdfs:Literal")
    print("=" * 60)

    reasoner = Reter()

    # Define NamedThing as: ∃hasName.Ω (any literal value)
    # Grammar: TOPBOUND -> top_bound for rdfs:Literal
    ontology = """
    NamedThing ≡ᑦ ∃hasName Ω
    hasName（Alice， 'Alice Smith'）
    hasName（Bob， 42）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Both should match rdfs:Literal (any literal)
    named_things = reasoner.get_instances('NamedThing')
    print(f"\nInstances with names: {named_things}")

    assert 'Alice' in named_things, "Alice should satisfy hasName restriction"
    assert 'Bob' in named_things, "Bob should satisfy hasName restriction (Ω matches any datatype)"

    print("✓ Test passed: Ω (rdfs:Literal) matches any datatype")


if __name__ == '__main__':
    test_datatype_restriction()
    test_datatype_with_literal()
