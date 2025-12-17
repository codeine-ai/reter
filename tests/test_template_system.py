#!/usr/bin/env python3
"""
Test the template rule system by demonstrating symmetric property template.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter_core import owl_rete_cpp

def test_symmetric_property_template():
    """
    Test that symmetric property template generates rules correctly.

    When we declare:
        marriedTo rdf:type owl:SymmetricProperty

    The template should generate a rule:
        IF ?x marriedTo ?y
        THEN ?y marriedTo ?x
    """
    print("=" * 80)
    print("TESTING TEMPLATE RULE SYSTEM: Symmetric Property")
    print("=" * 80)

    net = owl_rete_cpp.ReteNetwork()

    # Step 1: Declare marriedTo as symmetric property
    print("\n[Step 1] Declaring 'marriedTo' as symmetric property...")
    sym_fact = owl_rete_cpp.Fact()
    sym_fact.set("type", "symmetric")
    sym_fact.set("property", "marriedTo")
    net.add_fact(sym_fact)

    # Step 2: Add a role assertion
    print("[Step 2] Adding fact: Alice marriedTo Bob")
    role_fact = owl_rete_cpp.Fact()
    role_fact.set("type", "role_assertion")
    role_fact.set("subject", "Alice")
    role_fact.set("role", "marriedTo")
    role_fact.set("object", "Bob")
    net.add_fact(role_fact)

    # Step 3: Check if symmetric rule fired
    print("\n[Step 3] Checking if symmetric inference was made...")
    reverse_facts = net.query({
        "type": "role_assertion",
        "subject": "Bob",
        "role": "marriedTo",
        "object": "Alice"
    })

    if len(reverse_facts) > 0:
        print("✓ SUCCESS: Template rule fired!")
        print(f"  Found inferred fact: Bob marriedTo Alice")
        reverse_facts_list = reverse_facts.to_pylist()
        print(f"  Inferred by: {reverse_facts_list[0].get('inferred_by')}")
        return True
    else:
        print("✗ FAILED: Template rule did not fire")
        print("\n  All facts in network:")
        for fact in net.get_all_facts():
            print(f"    {fact.attributes}")
        return False

def test_transitive_property_template():
    """
    Test that transitive property template generates rules correctly.
    """
    print("\n" + "=" * 80)
    print("TESTING TEMPLATE RULE SYSTEM: Transitive Property")
    print("=" * 80)

    net = owl_rete_cpp.ReteNetwork()

    # Step 1: Declare ancestorOf as transitive property
    print("\n[Step 1] Declaring 'ancestorOf' as transitive property...")
    trans_fact = owl_rete_cpp.Fact()
    trans_fact.set("type", "transitive")
    trans_fact.set("property", "ancestorOf")
    net.add_fact(trans_fact)

    # Step 2: Add role assertions
    print("[Step 2] Adding facts:")
    print("  - Alice ancestorOf Bob")
    print("  - Bob ancestorOf Charlie")

    fact1 = owl_rete_cpp.Fact()
    fact1.set("type", "role_assertion")
    fact1.set("subject", "Alice")
    fact1.set("role", "ancestorOf")
    fact1.set("object", "Bob")
    net.add_fact(fact1)

    fact2 = owl_rete_cpp.Fact()
    fact2.set("type", "role_assertion")
    fact2.set("subject", "Bob")
    fact2.set("role", "ancestorOf")
    fact2.set("object", "Charlie")
    net.add_fact(fact2)

    # Step 3: Check if transitive rule fired
    print("\n[Step 3] Checking if transitive inference was made...")
    transitive_facts = net.query({
        "type": "role_assertion",
        "subject": "Alice",
        "role": "ancestorOf",
        "object": "Charlie"
    })

    if len(transitive_facts) > 0:
        print("✓ SUCCESS: Template rule fired!")
        print(f"  Found inferred fact: Alice ancestorOf Charlie")
        transitive_facts_list = transitive_facts.to_pylist()

        print(f"  Inferred by: {transitive_facts_list[0].get('inferred_by')}")
        return True
    else:
        print("✗ FAILED: Template rule did not fire")
        print("\n  All facts in network:")
        for fact in net.get_all_facts():
            if fact.get("type") == "role_assertion":
                print(f"    {fact.get('subject')} {fact.get('role')} {fact.get('object')}")
        return False

if __name__ == "__main__":
    success = True

    success &= test_symmetric_property_template()
    success &= test_transitive_property_template()

    print("\n" + "=" * 80)
    if success:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 80)

    sys.exit(0 if success else 1)
