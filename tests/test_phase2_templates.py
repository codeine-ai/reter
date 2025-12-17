#!/usr/bin/env python3
"""
Test Phase 2 Templates from rigtmpl.md Implementation
Tests: cls-maxc1, cls-maxc2, cls-maxqc1, cls-maxqc2, cls-maxqc3, cls-maxqc4
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter_core import owl_rete_cpp as owl

def test_max_cardinality_0():
    """Test cls-maxc1: Max Cardinality 0"""
    print("\n" + "="*80)
    print("TEST: Max Cardinality 0 (cls-maxc1)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare a restriction: VegetarianPizza has maxCardinality 0 on property hasMeatTopping
    f1 = owl.Fact()
    f1.set("type", "max_cardinality")
    f1.set("cardinality", "0")
    f1.set("on_property", "hasMeatTopping")
    f1.set("restriction_class", "VegetarianPizza")
    net.add_fact(f1)

    # Assert: MargheritaPizza is a VegetarianPizza
    f2 = owl.Fact()
    f2.set("type", "concept_assertion")
    f2.set("individual", "MargheritaPizza")
    f2.set("concept", "VegetarianPizza")
    net.add_fact(f2)

    # Assert: MargheritaPizza hasMeatTopping Pepperoni (should trigger error!)
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "MargheritaPizza")
    f3.set("role", "hasMeatTopping")
    f3.set("object", "Pepperoni")
    net.add_fact(f3)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected max cardinality 0 violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected max cardinality 0 violation")
        return False

def test_max_cardinality_1():
    """Test cls-maxc2: Max Cardinality 1"""
    print("\n" + "="*80)
    print("TEST: Max Cardinality 1 (cls-maxc2)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare a restriction: Person has maxCardinality 1 on property hasBirthMother
    f1 = owl.Fact()
    f1.set("type", "max_cardinality")
    f1.set("cardinality", "1")
    f1.set("on_property", "hasBirthMother")
    f1.set("restriction_class", "Person")
    net.add_fact(f1)

    # Assert: Alice is a Person
    f2 = owl.Fact()
    f2.set("type", "concept_assertion")
    f2.set("individual", "Alice")
    f2.set("concept", "Person")
    net.add_fact(f2)

    # Assert: Alice hasBirthMother Mary
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "Alice")
    f3.set("role", "hasBirthMother")
    f3.set("object", "Mary")
    net.add_fact(f3)

    # Assert: Alice hasBirthMother Sue
    f4 = owl.Fact()
    f4.set("type", "role_assertion")
    f4.set("subject", "Alice")
    f4.set("role", "hasBirthMother")
    f4.set("object", "Sue")
    net.add_fact(f4)

    # Should infer: Mary sameAs Sue
    inferred = net.query({
        "type": "same_as",
        "inferred": "true"
    })

    if len(inferred) > 0:
        print(f"✓ PASS: Inferred sameAs relationship due to max cardinality 1")
        for inf in inferred.to_pylist():
            print(f"  Inferred: {inf.get('individual1')} sameAs {inf.get('individual2')}")
        return True
    else:
        print(f"✗ FAIL: Should have inferred sameAs relationship")
        return False

def test_max_qualified_cardinality_0_class():
    """Test cls-maxqc1: Max Qualified Cardinality 0 with Class"""
    print("\n" + "="*80)
    print("TEST: Max Qualified Cardinality 0 with Class (cls-maxqc1)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: VegetarianPizza has maxQualifiedCardinality 0 on hasMeatTopping for class MeatTopping
    f1 = owl.Fact()
    f1.set("type", "max_qualified_cardinality")
    f1.set("cardinality", "0")
    f1.set("on_property", "hasTopping")
    f1.set("on_class", "MeatTopping")
    f1.set("restriction_class", "VegetarianPizza")
    net.add_fact(f1)

    # Assert: MargheritaPizza is a VegetarianPizza
    f2 = owl.Fact()
    f2.set("type", "concept_assertion")
    f2.set("individual", "MargheritaPizza")
    f2.set("concept", "VegetarianPizza")
    net.add_fact(f2)

    # Assert: MargheritaPizza hasTopping Pepperoni
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "MargheritaPizza")
    f3.set("role", "hasTopping")
    f3.set("object", "Pepperoni")
    net.add_fact(f3)

    # Assert: Pepperoni is a MeatTopping (should trigger error!)
    f4 = owl.Fact()
    f4.set("type", "concept_assertion")
    f4.set("individual", "Pepperoni")
    f4.set("concept", "MeatTopping")
    net.add_fact(f4)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected max qualified cardinality 0 violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected max qualified cardinality 0 violation")
        return False

def test_max_qualified_cardinality_0_thing():
    """Test cls-maxqc2: Max Qualified Cardinality 0 with Thing"""
    print("\n" + "="*80)
    print("TEST: Max Qualified Cardinality 0 with Thing (cls-maxqc2)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: NullClass has maxQualifiedCardinality 0 on anyProperty for class Thing
    f1 = owl.Fact()
    f1.set("type", "max_qualified_cardinality")
    f1.set("cardinality", "0")
    f1.set("on_property", "hasAny")
    f1.set("on_class", "Thing")
    f1.set("restriction_class", "NullClass")
    net.add_fact(f1)

    # Assert: EmptyThing is a NullClass
    f2 = owl.Fact()
    f2.set("type", "concept_assertion")
    f2.set("individual", "EmptyThing")
    f2.set("concept", "NullClass")
    net.add_fact(f2)

    # Assert: EmptyThing hasAny Something (should trigger error!)
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "EmptyThing")
    f3.set("role", "hasAny")
    f3.set("object", "Something")
    net.add_fact(f3)

    # Check for validation error
    errors = net.query({"type": "inconsistency"}).to_pylist()

    if len(errors) > 0:
        print(f"✓ PASS: Detected max qualified cardinality 0 (Thing) violation")
        for err in errors:
            print(f"  Error: {err.get('message')}")
        return True
    else:
        print(f"✗ FAIL: Should have detected max qualified cardinality 0 (Thing) violation")
        return False

def test_max_qualified_cardinality_1_class():
    """Test cls-maxqc3: Max Qualified Cardinality 1 with Class"""
    print("\n" + "="*80)
    print("TEST: Max Qualified Cardinality 1 with Class (cls-maxqc3)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: Person has maxQualifiedCardinality 1 on hasParent for class Female
    f1 = owl.Fact()
    f1.set("type", "max_qualified_cardinality")
    f1.set("cardinality", "1")
    f1.set("on_property", "hasParent")
    f1.set("on_class", "Female")
    f1.set("restriction_class", "Person")
    net.add_fact(f1)

    # Assert: Bob is a Person
    f2 = owl.Fact()
    f2.set("type", "concept_assertion")
    f2.set("individual", "Bob")
    f2.set("concept", "Person")
    net.add_fact(f2)

    # Assert: Bob hasParent Mary
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "Bob")
    f3.set("role", "hasParent")
    f3.set("object", "Mary")
    net.add_fact(f3)

    # Assert: Mary is Female
    f4 = owl.Fact()
    f4.set("type", "concept_assertion")
    f4.set("individual", "Mary")
    f4.set("concept", "Female")
    net.add_fact(f4)

    # Assert: Bob hasParent Sue
    f5 = owl.Fact()
    f5.set("type", "role_assertion")
    f5.set("subject", "Bob")
    f5.set("role", "hasParent")
    f5.set("object", "Sue")
    net.add_fact(f5)

    # Assert: Sue is Female
    f6 = owl.Fact()
    f6.set("type", "concept_assertion")
    f6.set("individual", "Sue")
    f6.set("concept", "Female")
    net.add_fact(f6)

    # Should infer: Mary sameAs Sue
    inferred = net.query({
        "type": "same_as",
        "inferred": "true"
    })

    if len(inferred) > 0:
        print(f"✓ PASS: Inferred sameAs for qualified max cardinality 1 (class)")
        for inf in inferred.to_pylist():
            print(f"  Inferred: {inf.get('individual1')} sameAs {inf.get('individual2')}")
        return True
    else:
        print(f"✗ FAIL: Should have inferred sameAs relationship")
        return False

def test_max_qualified_cardinality_1_thing():
    """Test cls-maxqc4: Max Qualified Cardinality 1 with Thing"""
    print("\n" + "="*80)
    print("TEST: Max Qualified Cardinality 1 with Thing (cls-maxqc4)")
    print("="*80)

    net = owl.ReteNetwork()

    # Declare: Singleton has maxQualifiedCardinality 1 on hasElement for Thing
    f1 = owl.Fact()
    f1.set("type", "max_qualified_cardinality")
    f1.set("cardinality", "1")
    f1.set("on_property", "hasElement")
    f1.set("on_class", "Thing")
    f1.set("restriction_class", "Singleton")
    net.add_fact(f1)

    # Assert: MySet is a Singleton
    f2 = owl.Fact()
    f2.set("type", "concept_assertion")
    f2.set("individual", "MySet")
    f2.set("concept", "Singleton")
    net.add_fact(f2)

    # Assert: MySet hasElement A
    f3 = owl.Fact()
    f3.set("type", "role_assertion")
    f3.set("subject", "MySet")
    f3.set("role", "hasElement")
    f3.set("object", "A")
    net.add_fact(f3)

    # Assert: MySet hasElement B
    f4 = owl.Fact()
    f4.set("type", "role_assertion")
    f4.set("subject", "MySet")
    f4.set("role", "hasElement")
    f4.set("object", "B")
    net.add_fact(f4)

    # Should infer: A sameAs B
    inferred = net.query({
        "type": "same_as",
        "inferred": "true"
    })

    if len(inferred) > 0:
        print(f"✓ PASS: Inferred sameAs for qualified max cardinality 1 (Thing)")
        for inf in inferred.to_pylist():
            print(f"  Inferred: {inf.get('individual1')} sameAs {inf.get('individual2')}")
        return True
    else:
        print(f"✗ FAIL: Should have inferred sameAs relationship")
        return False

def main():
    """Run all Phase 2 template tests"""
    print("\n" + "#"*80)
    print("# PHASE 2 TEMPLATES TEST SUITE")
    print("# Testing: cls-maxc1, cls-maxc2, cls-maxqc1-4")
    print("#"*80)

    results = []

    # Run all tests
    results.append(("cls-maxc1 (Max Cardinality 0)", test_max_cardinality_0()))
    results.append(("cls-maxc2 (Max Cardinality 1)", test_max_cardinality_1()))
    results.append(("cls-maxqc1 (Max Qualified Cardinality 0 - Class)", test_max_qualified_cardinality_0_class()))
    results.append(("cls-maxqc2 (Max Qualified Cardinality 0 - Thing)", test_max_qualified_cardinality_0_thing()))
    results.append(("cls-maxqc3 (Max Qualified Cardinality 1 - Class)", test_max_qualified_cardinality_1_class()))
    results.append(("cls-maxqc4 (Max Qualified Cardinality 1 - Thing)", test_max_qualified_cardinality_1_thing()))

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
        print("\n🎉 ALL PHASE 2 TEMPLATES WORKING!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
