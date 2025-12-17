#!/usr/bin/env python3
"""
Test Phase 5 Templates - List-based Templates
Templates: eq-diff2/3, cax-adc, prp-adp, prp-key
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import owl_rete_cpp as owl

def test_alldifferent():
    """Test eq-diff2: AllDifferent"""
    print("\n" + "="*80)
    print("TEST: AllDifferent (eq-diff2)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: ≠{Alice, Bob, Carol} - All different
    f1 = owl.Fact()
    f1.set("type", "all_different")
    f1.set("members", "Alice,Bob,Carol")
    net.add_fact(f1)

    # Assert: Alice sameAs Bob (should trigger error!)
    f2 = owl.Fact()
    f2.set("type", "same_as")
    f2.set("ind1", "Alice")
    f2.set("ind2", "Bob")
    net.add_fact(f2)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected AllDifferent violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected AllDifferent violation")
        return False

def test_alldisjoint_classes():
    """Test cax-adc: AllDisjointClasses"""
    print("\n" + "="*80)
    print("TEST: AllDisjointClasses (cax-adc)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: ¬≡(Male, Female, NonBinary) - All disjoint
    f1 = owl.Fact()
    f1.set("type", "all_disjoint_classes")
    f1.set("members", "Male,Female,NonBinary")
    net.add_fact(f1)

    # Assert: Alex is Male
    f2 = owl.Fact()
    f2.set("type", "instance_of")
    f2.set("individual", "Alex")
    f2.set("concept", "Male")
    net.add_fact(f2)

    # Assert: Alex is Female (should trigger error!)
    f3 = owl.Fact()
    f3.set("type", "instance_of")
    f3.set("individual", "Alex")
    f3.set("concept", "Female")
    net.add_fact(f3)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected AllDisjointClasses violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected AllDisjointClasses violation")
        return False

def test_alldisjoint_properties():
    """Test prp-adp: AllDisjointProperties"""
    print("\n" + "="*80)
    print("TEST: AllDisjointProperties (prp-adp)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: All properties disjoint
    f1 = owl.Fact()
    f1.set("type", "all_disjoint_properties")
    f1.set("members", "hasFather,hasMother,hasSpouse")
    net.add_fact(f1)

    # Assert: John hasFather Mike
    f2 = owl.Fact()
    f2.set("type", "role_assertion")
    f2.set("subject", "John")
    f2.set("role", "hasFather")
    f2.set("object", "Mike")
    net.add_fact(f2)

    # Assert: John hasMother Mike (should trigger error - same value for disjoint properties!)
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "John")
    f3.set("role", "hasMother")
    f3.set("object", "Mike")
    net.add_fact(f3)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected AllDisjointProperties violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected AllDisjointProperties violation")
        return False

def test_haskey():
    """Test prp-key: HasKey"""
    print("\n" + "="*80)
    print("TEST: HasKey (prp-key)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: Person hasKey (ssn)
    f1 = owl.Fact()
    f1.set("type", "has_key")
    f1.set("class", "Person")
    f1.set("keys", "ssn")
    net.add_fact(f1)

    # Assert: Alice is a Person
    f2 = owl.Fact()
    f2.set("type", "instance_of")
    f2.set("individual", "Alice")
    f2.set("concept", "Person")
    net.add_fact(f2)

    # Assert: Bob is a Person
    f3 = owl.Fact()
    f3.set("type", "instance_of")
    f3.set("individual", "Bob")
    f3.set("concept", "Person")
    net.add_fact(f3)

    # Assert: Alice ssn "123-45-6789"
    f4 = owl.Fact()
    f4.set("type", "role_assertion")
    f4.set("subject", "Alice")
    f4.set("role", "ssn")
    f4.set("object", "123-45-6789")
    net.add_fact(f4)

    # Assert: Bob ssn "123-45-6789" (same SSN!)
    f5 = owl.Fact()
    f5.set("type", "role_assertion")
    f5.set("subject", "Bob")
    f5.set("role", "ssn")
    f5.set("object", "123-45-6789")
    net.add_fact(f5)

    # Check for inferred sameAs
    sameas = net.query({"type": "same_as"})

    found = False
    for sa in sameas.to_pylist():
        ind1 = sa.get("ind1")
        ind2 = sa.get("ind2")
        if (ind1 == "Alice" and ind2 == "Bob") or (ind1 == "Bob" and ind2 == "Alice"):
            found = True
            break

    if found:
        print(f"✓ PASS: HasKey inferred Alice sameAs Bob (same SSN)")
        return True
    else:
        print(f"✗ FAIL: Should have inferred Alice sameAs Bob")
        print(f"  Found sameAs facts: {len(sameas)}")
        for sa in sameas.to_pylist():
            print(f"    {sa.get('ind1')} sameAs {sa.get('ind2')}")
        return False

def test_haskey_multi():
    """Test prp-key with multiple keys"""
    print("\n" + "="*80)
    print("TEST: HasKey Multi-Property (prp-key)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: Person hasKey (firstName, lastName)
    f1 = owl.Fact()
    f1.set("type", "has_key")
    f1.set("class", "Person")
    f1.set("keys", "firstName,lastName")
    net.add_fact(f1)

    # Person1 and Person2
    f2 = owl.Fact()
    f2.set("type", "instance_of")
    f2.set("individual", "Person1")
    f2.set("concept", "Person")
    net.add_fact(f2)

    f3 = owl.Fact()
    f3.set("type", "instance_of")
    f3.set("individual", "Person2")
    f3.set("concept", "Person")
    net.add_fact(f3)

    # Person1: firstName="John", lastName="Smith"
    f4 = owl.Fact()
    f4.set("type", "role_assertion")
    f4.set("subject", "Person1")
    f4.set("role", "firstName")
    f4.set("object", "John")
    net.add_fact(f4)

    f5 = owl.Fact()
    f5.set("type", "role_assertion")
    f5.set("subject", "Person1")
    f5.set("role", "lastName")
    f5.set("object", "Smith")
    net.add_fact(f5)

    # Person2: firstName="John", lastName="Smith" (same keys!)
    f6 = owl.Fact()
    f6.set("type", "role_assertion")
    f6.set("subject", "Person2")
    f6.set("role", "firstName")
    f6.set("object", "John")
    net.add_fact(f6)

    f7 = owl.Fact()
    f7.set("type", "role_assertion")
    f7.set("subject", "Person2")
    f7.set("role", "lastName")
    f7.set("object", "Smith")
    net.add_fact(f7)

    # Check for inferred sameAs
    sameas = net.query({"type": "same_as"})

    found = False
    for sa in sameas.to_pylist():
        ind1 = sa.get("ind1")
        ind2 = sa.get("ind2")
        if (ind1 == "Person1" and ind2 == "Person2") or (ind1 == "Person2" and ind2 == "Person1"):
            found = True
            break

    if found:
        print(f"✓ PASS: HasKey inferred Person1 sameAs Person2 (both keys match)")
        return True
    else:
        print(f"✗ FAIL: Should have inferred Person1 sameAs Person2")
        print(f"  Found sameAs facts: {len(sameas)}")
        return False

def main():
    """Run all Phase 5 template tests"""
    print("\n" + "#"*80)
    print("# PHASE 5 TEMPLATES TEST SUITE")
    print("# Templates: eq-diff2, cax-adc, prp-adp, prp-key")
    print("#"*80)

    results = []

    # Test all Phase 5 templates
    results.append(("eq-diff2 (AllDifferent)", test_alldifferent()))
    results.append(("cax-adc (AllDisjointClasses)", test_alldisjoint_classes()))
    results.append(("prp-adp (AllDisjointProperties)", test_alldisjoint_properties()))
    results.append(("prp-key (HasKey - single)", test_haskey()))
    results.append(("prp-key (HasKey - multi)", test_haskey_multi()))

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
        print("\n🎉 ALL PHASE 5 TEMPLATES WORKING!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
