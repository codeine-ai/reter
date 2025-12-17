#!/usr/bin/env python3
"""
Comprehensive test of all 10 template types.
Verifies that each template can be instantiated and produces correct inferences.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import owl_rete_cpp

def make_fact(**kwargs):
    """Helper to create a Fact from keyword arguments"""
    fact = owl_rete_cpp.Fact()
    for key, value in kwargs.items():
        fact.set(key, value)
    return fact

def test_symmetric_property():
    """Test prp-symp template"""
    print("\n" + "="*80)
    print("TEST 1: Symmetric Property Template (prp-symp)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="symmetric", property="marriedTo"))
    net.add_fact(make_fact(type="role_assertion", subject="Alice", role="marriedTo", object="Bob"))

    results = net.query({"subject": "Bob", "role": "marriedTo", "object": "Alice"})
    if len(results) > 0:
        print("✓ PASS: Found Bob marriedTo Alice")
        return True
    else:
        print("✗ FAIL: Symmetric inference not made")
        return False

def test_transitive_property():
    """Test prp-trp template"""
    print("\n" + "="*80)
    print("TEST 2: Transitive Property Template (prp-trp)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="transitive", property="ancestorOf"))
    net.add_fact(make_fact(type="role_assertion", subject="Alice", role="ancestorOf", object="Bob"))
    net.add_fact(make_fact(type="role_assertion", subject="Bob", role="ancestorOf", object="Charlie"))

    results = net.query({"subject": "Alice", "role": "ancestorOf", "object": "Charlie"})
    if len(results) > 0:
        print("✓ PASS: Found Alice ancestorOf Charlie")
        return True
    else:
        print("✗ FAIL: Transitive inference not made")
        return False

def test_subproperty():
    """Test prp-spo1 template"""
    print("\n" + "="*80)
    print("TEST 3: SubProperty Template (prp-spo1)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="sub_property", sub="hasFather", super="hasParent"))
    net.add_fact(make_fact(type="role_assertion", subject="Bob", role="hasFather", object="John"))

    results = net.query({"subject": "Bob", "role": "hasParent", "object": "John"})
    if len(results) > 0:
        print("✓ PASS: Found Bob hasParent John")
        return True
    else:
        print("✗ FAIL: SubProperty inference not made")
        return False

def test_inverse_property():
    """Test prp-inv1/inv2 template"""
    print("\n" + "="*80)
    print("TEST 4: Inverse Property Template (prp-inv1/inv2)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="inverse", property1="hasChild", property2="hasParent"))
    net.add_fact(make_fact(type="role_assertion", subject="John", role="hasChild", object="Bob"))

    results = net.query({"subject": "Bob", "role": "hasParent", "object": "John"})
    if len(results) > 0:
        print("✓ PASS: Found Bob hasParent John")
        return True
    else:
        print("✗ FAIL: Inverse property inference not made")
        return False

def test_functional_property():
    """Test prp-fp template"""
    print("\n" + "="*80)
    print("TEST 5: Functional Property Template (prp-fp)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="functional", property="hasBirthMother"))
    net.add_fact(make_fact(type="role_assertion", subject="Bob", role="hasBirthMother", object="Mary"))
    net.add_fact(make_fact(type="role_assertion", subject="Bob", role="hasBirthMother", object="Jane"))

    results = net.query({"type": "same_individual", "individual1": "Mary", "individual2": "Jane"})
    if len(results) == 0:
        results = net.query({"type": "same_individual", "individual1": "Jane", "individual2": "Mary"})
    if len(results) > 0:
        print("✓ PASS: Found Mary sameAs Jane")
        return True
    else:
        print("✗ FAIL: Functional property inference not made")
        return False

def test_inverse_functional_property():
    """Test prp-ifp template"""
    print("\n" + "="*80)
    print("TEST 6: Inverse Functional Property Template (prp-ifp)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="inverse_functional", property="hasSSN"))
    net.add_fact(make_fact(type="role_assertion", subject="Person1", role="hasSSN", object="123-45-6789"))
    net.add_fact(make_fact(type="role_assertion", subject="Person2", role="hasSSN", object="123-45-6789"))

    results = net.query({"type": "same_individual", "individual1": "Person1", "individual2": "Person2"})
    if len(results) == 0:
        results = net.query({"type": "same_individual", "individual1": "Person2", "individual2": "Person1"})
    if len(results) > 0:
        print("✓ PASS: Found Person1 sameAs Person2")
        return True
    else:
        print("✗ FAIL: Inverse functional property inference not made")
        return False

def test_some_values_from():
    """Test cls-svf1/svf2 template"""
    print("\n" + "="*80)
    print("TEST 7: SomeValuesFrom Restriction Template (cls-svf)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="some_values_from", restriction="Parent", property="hasChild", **{"class": "Person"}))
    net.add_fact(make_fact(type="role_assertion", subject="John", role="hasChild", object="Bob"))
    net.add_fact(make_fact(type="class_assertion", individual="Bob", **{"class": "Person"}))

    results = net.query({"type": "class_assertion", "individual": "John", "class": "Parent"})
    if len(results) > 0:
        print("✓ PASS: Found John type Parent")
        return True
    else:
        print("✗ FAIL: SomeValuesFrom inference not made")
        return False

def test_all_values_from():
    """Test cls-avf template"""
    print("\n" + "="*80)
    print("TEST 8: AllValuesFrom Restriction Template (cls-avf)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="all_values_from", restriction="VegetarianPizza", property="hasTopping", **{"class": "VegetarianTopping"}))
    net.add_fact(make_fact(type="class_assertion", individual="Pizza1", **{"class": "VegetarianPizza"}))
    net.add_fact(make_fact(type="role_assertion", subject="Pizza1", role="hasTopping", object="Mushrooms"))

    results = net.query({"type": "class_assertion", "individual": "Mushrooms", "class": "VegetarianTopping"})
    if len(results) > 0:
        print("✓ PASS: Found Mushrooms type VegetarianTopping")
        return True
    else:
        print("✗ FAIL: AllValuesFrom inference not made")
        return False

def test_has_value():
    """Test cls-hv1/hv2 template"""
    print("\n" + "="*80)
    print("TEST 9: HasValue Restriction Template (cls-hv)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="has_value", restriction="ItalianPizza", property="hasCountryOfOrigin", value="Italy"))
    net.add_fact(make_fact(type="class_assertion", individual="Pizza1", **{"class": "ItalianPizza"}))

    results = net.query({"type": "role_assertion", "subject": "Pizza1", "role": "hasCountryOfOrigin", "object": "Italy"})
    if len(results) > 0:
        print("✓ PASS: Found Pizza1 hasCountryOfOrigin Italy")
        return True
    else:
        print("✗ FAIL: HasValue inference not made")
        return False

def test_property_chain():
    """Test prp-spo2 template"""
    print("\n" + "="*80)
    print("TEST 10: Property Chain Template (prp-spo2)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.add_fact(make_fact(type="property_chain", property="hasUncle", chain="hasParent,hasBrother"))
    net.add_fact(make_fact(type="role_assertion", subject="Bob", role="hasParent", object="John"))
    net.add_fact(make_fact(type="role_assertion", subject="John", role="hasBrother", object="Mike"))

    results = net.query({"subject": "Bob", "role": "hasUncle", "object": "Mike"})
    if len(results) > 0:
        print("✓ PASS: Found Bob hasUncle Mike")
        return True
    else:
        print("✗ FAIL: Property chain inference not made")
        return False

def main():
    print("\n" + "="*80)
    print("COMPREHENSIVE TEMPLATE SYSTEM TEST")
    print("Testing all 10 template types")
    print("="*80)

    tests = [
        test_symmetric_property,
        test_transitive_property,
        test_subproperty,
        test_inverse_property,
        test_functional_property,
        test_inverse_functional_property,
        test_some_values_from,
        test_all_values_from,
        test_has_value,
        test_property_chain
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ FAIL: Exception occurred: {e}")
            results.append(False)

    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ ALL TEMPLATES WORKING!")
    else:
        print(f"\n✗ {total - passed} template(s) failed")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
