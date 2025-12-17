#!/usr/bin/env python3
"""
Test Phase 1 Templates from rigtmpl.md Implementation
Tests: prp-irp, prp-asyp, prp-eqp1/2, prp-pdw, prp-npa1, prp-npa2
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import owl_rete_cpp as owl

def test_irreflexive_property():
    """Test prp-irp: Irreflexive Property"""
    print("\n" + "="*80)
    print("TEST: Irreflexive Property (prp-irp)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare "differentFrom" as irreflexive
    f1 = owl.Fact()
    f1.set("type", "irreflexive")
    f1.set("property", "differentFrom")
    net.add_fact(f1)

    # This should trigger a validation error: x differentFrom x
    f2 = owl.Fact()
    f2.set("type", "role_assertion")
    f2.set("subject", "Alice")
    f2.set("role", "differentFrom")
    f2.set("object", "Alice")
    net.add_fact(f2)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected irreflexive property violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected irreflexive property violation")
        return False

def test_asymmetric_property():
    """Test prp-asyp: Asymmetric Property"""
    print("\n" + "="*80)
    print("TEST: Asymmetric Property (prp-asyp)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare "parentOf" as asymmetric
    f1 = owl.Fact()
    f1.set("type", "asymmetric")
    f1.set("property", "parentOf")
    net.add_fact(f1)

    # Add: Alice parentOf Bob
    f2 = owl.Fact()
    f2.set("type", "role_assertion")
    f2.set("subject", "Alice")
    f2.set("role", "parentOf")
    f2.set("object", "Bob")
    net.add_fact(f2)

    # Add: Bob parentOf Alice (should trigger error!)
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "Bob")
    f3.set("role", "parentOf")
    f3.set("object", "Alice")
    net.add_fact(f3)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected asymmetric property violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected asymmetric property violation")
        return False

def test_equivalent_property():
    """Test prp-eqp1/2: Equivalent Property"""
    print("\n" + "="*80)
    print("TEST: Equivalent Property (prp-eqp1/2)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare "spouse" and "marriedTo" as equivalent
    f1 = owl.Fact()
    f1.set("type", "equivalent_property")
    f1.set("property1", "spouse")
    f1.set("property2", "marriedTo")
    net.add_fact(f1)

    # Add: Alice spouse Bob
    f2 = owl.Fact()
    f2.set("type", "role_assertion")
    f2.set("subject", "Alice")
    f2.set("role", "spouse")
    f2.set("object", "Bob")
    net.add_fact(f2)

    # Should infer: Alice marriedTo Bob
    inferred = net.query({
        "type": "role_assertion",
        "subject": "Alice",
        "role": "marriedTo",
        "object": "Bob",
        "inferred": "true"
    })

    if len(inferred) > 0:
        print(f"✓ PASS: Inferred Alice marriedTo Bob from Alice spouse Bob")
        inferred_list = inferred.to_pylist()
        print(f"  Inferred by: {inferred_list[0].get('inferred_by')}")
    else:
        print(f"✗ FAIL: Should have inferred Alice marriedTo Bob")
        return False

    # Now test reverse direction
    net2 = owl.ReteNetwork()

    f1b = owl.Fact()
    f1b.set("type", "equivalent_property")
    f1b.set("property1", "spouse")
    f1b.set("property2", "marriedTo")
    net2.add_fact(f1b)

    # Add: Charlie marriedTo Dana
    f2b = owl.Fact()
    f2b.set("type", "role_assertion")
    f2b.set("subject", "Charlie")
    f2b.set("role", "marriedTo")
    f2b.set("object", "Dana")
    net2.add_fact(f2b)

    # Should infer: Charlie spouse Dana
    inferred2 = net2.query({
        "type": "role_assertion",
        "subject": "Charlie",
        "role": "spouse",
        "object": "Dana",
        "inferred": "true"
    })

    if len(inferred2) > 0:
        print(f"✓ PASS: Inferred Charlie spouse Dana from Charlie marriedTo Dana")
        inferred2_list = inferred2.to_pylist()
        print(f"  Inferred by: {inferred2_list[0].get('inferred_by')}")
        return True
    else:
        print(f"✗ FAIL: Should have inferred Charlie spouse Dana")
        return False

def test_property_disjoint_with():
    """Test prp-pdw: Property Disjoint With"""
    print("\n" + "="*80)
    print("TEST: Property Disjoint With (prp-pdw)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare "hasFather" and "hasMother" as disjoint
    f1 = owl.Fact()
    f1.set("type", "property_disjoint_with")
    f1.set("property1", "hasFather")
    f1.set("property2", "hasMother")
    net.add_fact(f1)

    # Add: Bob hasFather John
    f2 = owl.Fact()
    f2.set("type", "role_assertion")
    f2.set("subject", "Bob")
    f2.set("role", "hasFather")
    f2.set("object", "John")
    net.add_fact(f2)

    # Add: Bob hasMother John (should trigger error!)
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "Bob")
    f3.set("role", "hasMother")
    f3.set("object", "John")
    net.add_fact(f3)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected disjoint properties violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected disjoint properties violation")
        return False

def test_negative_property_assertion_individual():
    """Test prp-npa1: Negative Property Assertion (Individual)"""
    print("\n" + "="*80)
    print("TEST: Negative Property Assertion - Individual (prp-npa1)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: Alice NOT knows Bob
    f1 = owl.Fact()
    f1.set("type", "negative_property_assertion")
    f1.set("source_individual", "Alice")
    f1.set("assertion_property", "knows")
    f1.set("target_individual", "Bob")
    net.add_fact(f1)

    # Now assert: Alice knows Bob (should trigger error!)
    f2 = owl.Fact()
    f2.set("type", "role_assertion")
    f2.set("subject", "Alice")
    f2.set("role", "knows")
    f2.set("object", "Bob")
    net.add_fact(f2)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected negative property assertion violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected negative property assertion violation")
        return False

def test_negative_property_assertion_value():
    """Test prp-npa2: Negative Property Assertion (Value)"""
    print("\n" + "="*80)
    print("TEST: Negative Property Assertion - Value (prp-npa2)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: Alice NOT hasAge "25"
    f1 = owl.Fact()
    f1.set("type", "negative_property_assertion")
    f1.set("source_individual", "Alice")
    f1.set("assertion_property", "hasAge")
    f1.set("target_value", "25")
    net.add_fact(f1)

    # Now assert: Alice hasAge "25" (should trigger error!)
    f2 = owl.Fact()
    f2.set("type", "role_assertion")
    f2.set("subject", "Alice")
    f2.set("role", "hasAge")
    f2.set("object", "25")
    net.add_fact(f2)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected negative property assertion (value) violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected negative property assertion (value) violation")
        return False

def main():
    """Run all Phase 1 template tests"""
    print("\n" + "#"*80)
    print("# PHASE 1 TEMPLATES TEST SUITE")
    print("# Testing: prp-irp, prp-asyp, prp-eqp, prp-pdw, prp-npa1, prp-npa2")
    print("#"*80)

    results = []

    # Run all tests
    results.append(("prp-irp (Irreflexive Property)", test_irreflexive_property()))
    results.append(("prp-asyp (Asymmetric Property)", test_asymmetric_property()))
    results.append(("prp-eqp1/2 (Equivalent Property)", test_equivalent_property()))
    results.append(("prp-pdw (Property Disjoint With)", test_property_disjoint_with()))
    results.append(("prp-npa1 (Negative Property Assertion - Individual)", test_negative_property_assertion_individual()))
    results.append(("prp-npa2 (Negative Property Assertion - Value)", test_negative_property_assertion_value()))

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL PHASE 1 TEMPLATES WORKING!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
