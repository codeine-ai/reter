#!/usr/bin/env python3
"""
Core Grammar Statement Tests
Tests the most important statement types from dl.lark using load_ontology_from_string()
Based on pattern from tests/test_tbox_with_1000_instances.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter import owl_rete_cpp

def test_subsumption():
    """Test 1.1: Subsumption (SubClassOf) - Dog ⊑ᑦ Animal"""
    print("\n" + "="*80)
    print("TEST 1: Subsumption (SubClassOf)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Dog ⊑ᑦ Animal")
    net.load_ontology_from_string("Dog（Fido）")

    # Check if Fido is inferred to be an Animal
    all_facts = net.get_all_facts()
    fido_animal = [f for f in all_facts if f.get('type') == 'instance_of'
                   and f.get('individual') == 'Fido'
                   and f.get('concept') == 'Animal']

    if len(fido_animal) > 0:
        print("✓ PASS: Fido inferred as Animal")
        return True
    else:
        print("✗ FAIL: Fido not inferred as Animal")
        print(f"  Total facts: {len(all_facts)}")
        print(f"  Fido facts: {[f for f in all_facts if 'Fido' in str(f)][:5]}")
        return False

def test_class_equivalence():
    """Test 1.3: Class Equivalence - Human ≡ᑦ Person"""
    print("\n" + "="*80)
    print("TEST 2: Class Equivalence")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Human ≡ᑦ Person")
    net.load_ontology_from_string("Human（Alice）")

    all_facts = net.get_all_facts()
    alice_person = [f for f in all_facts if f.get('type') == 'instance_of'
                    and f.get('individual') == 'Alice'
                    and f.get('concept') == 'Person']

    if len(alice_person) > 0:
        print("✓ PASS: Alice inferred as Person")
        return True
    else:
        print("✗ FAIL: Alice not inferred as Person")
        return False

def test_disjoint_classes():
    """Test 1.5: Disjoint Classes - ¬≡ᑦ（Male，Female）"""
    print("\n" + "="*80)
    print("TEST 3: Disjoint Classes")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("¬≡ᑦ（Male，Female）")
    net.load_ontology_from_string("Male（Charlie）")
    net.load_ontology_from_string("Female（Charlie）")

    all_facts = net.get_all_facts()
    errors = [f for f in all_facts if f.get('type') == 'inconsistency']

    if len(errors) > 0:
        print("✓ PASS: Detected disjoint classes violation")
        for err in errors[:3]:
            print(f"  Error: {err.get('message', '')}")
        return True
    else:
        print("✗ FAIL: Should detect disjoint classes violation")
        return False

def test_property_subsumption():
    """Test 3.1: Object Property Subsumption - hasParent ⊑ᴿ hasAncestor"""
    print("\n" + "="*80)
    print("TEST 4: Object Property Subsumption")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("hasParent ⊑ᴿ hasAncestor")
    net.load_ontology_from_string("hasParent（Alice，Bob）")

    all_facts = net.get_all_facts()
    alice_ancestor = [f for f in all_facts if f.get('type') == 'role_assertion'
                      and f.get('subject') == 'Alice'
                      and f.get('role') == 'hasAncestor'
                      and f.get('object') == 'Bob']

    if len(alice_ancestor) > 0:
        print("✓ PASS: hasAncestor inferred from hasParent")
        return True
    else:
        print("✗ FAIL: hasAncestor not inferred")
        return False

def test_property_chain():
    """Test 3.6: Property Chain - hasParent ∘ hasBrother ⊑ᴿ hasUncle"""
    print("\n" + "="*80)
    print("TEST 5: Property Chain")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("hasParent ∘ hasBrother ⊑ᴿ hasUncle")
    net.load_ontology_from_string("hasParent（Alice，Bob）")
    net.load_ontology_from_string("hasBrother（Bob，Charlie）")

    all_facts = net.get_all_facts()
    alice_uncle = [f for f in all_facts if f.get('type') == 'role_assertion'
                   and f.get('subject') == 'Alice'
                   and f.get('role') == 'hasUncle'
                   and f.get('object') == 'Charlie']

    if len(alice_uncle) > 0:
        print("✓ PASS: hasUncle inferred via property chain")
        return True
    else:
        print("✗ FAIL: hasUncle not inferred")
        return False

def test_class_assertion():
    """Test 5.1: Class Assertion - Person（Alice）"""
    print("\n" + "="*80)
    print("TEST 6: Class Assertion")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Person（Alice）")

    all_facts = net.get_all_facts()
    alice_person = [f for f in all_facts if f.get('type') == 'instance_of'
                    and f.get('individual') == 'Alice'
                    and f.get('concept') == 'Person']

    if len(alice_person) > 0:
        print("✓ PASS: Alice is Person")
        return True
    else:
        print("✗ FAIL: Alice not found as Person")
        return False

def test_property_assertion():
    """Test 5.2: Object Property Assertion - knows（Alice，Bob）"""
    print("\n" + "="*80)
    print("TEST 7: Object Property Assertion")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("knows（Alice，Bob）")

    all_facts = net.get_all_facts()
    alice_knows = [f for f in all_facts if f.get('type') == 'role_assertion'
                   and f.get('subject') == 'Alice'
                   and f.get('role') == 'knows'
                   and f.get('object') == 'Bob']

    if len(alice_knows) > 0:
        print("✓ PASS: Alice knows Bob")
        return True
    else:
        print("✗ FAIL: Alice knows Bob not found")
        return False

def test_data_property_assertion():
    """Test 5.3: Data Property Assertion - hasAge（Alice，30）"""
    print("\n" + "="*80)
    print("TEST 8: Data Property Assertion")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("hasAge（Alice，30）")

    all_facts = net.get_all_facts()
    alice_age = [f for f in all_facts if f.get('type') == 'data_assertion'
                 and f.get('subject') == 'Alice'
                 and f.get('property') == 'hasAge'
                 and f.get('value') == '30']

    if len(alice_age) > 0:
        print("✓ PASS: Alice has age 30")
        return True
    else:
        print("✗ FAIL: Alice age 30 not found")
        # Check what we got
        alice_facts = [f for f in all_facts if 'Alice' in str(f)]
        print(f"  Found {len(alice_facts)} facts containing Alice:")
        for fact in alice_facts[:3]:
            print(f"    {dict(fact.attributes)}")
        return False

def test_same_individuals():
    """Test 5.4: Same Individuals - Alice ﹦ AliceSmith"""
    print("\n" + "="*80)
    print("TEST 9: Same Individuals")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Alice ﹦ AliceSmith")

    all_facts = net.get_all_facts()
    same_as = [f for f in all_facts if f.get('type') == 'same_as'
               and ((f.get('ind1') == 'Alice' and f.get('ind2') == 'AliceSmith')
                    or (f.get('ind1') == 'AliceSmith' and f.get('ind2') == 'Alice'))]

    if len(same_as) > 0:
        print("✓ PASS: Alice sameAs AliceSmith")
        return True
    else:
        print("✗ FAIL: Same individuals assertion not found")
        return False

def test_class_union():
    """Test 8.7: Class Union - Parent ≡ᑦ Mother ⊔ Father"""
    print("\n" + "="*80)
    print("TEST 10: Class Union")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Parent ≡ᑦ Mother ⊔ Father")
    net.load_ontology_from_string("Mother（Alice）")

    all_facts = net.get_all_facts()
    alice_parent = [f for f in all_facts if f.get('type') == 'instance_of'
                    and f.get('individual') == 'Alice'
                    and f.get('concept') == 'Parent']

    if len(alice_parent) > 0:
        print("✓ PASS: Alice inferred as Parent via union")
        return True
    else:
        print("✗ FAIL: Alice not inferred as Parent")
        return False

def test_class_intersection():
    """Test 8.8: Class Intersection - WorkingParent ≡ᑦ Parent ⊓ Employee"""
    print("\n" + "="*80)
    print("TEST 11: Class Intersection")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("WorkingParent ≡ᑦ Parent ⊓ Employee")
    net.load_ontology_from_string("Parent（Bob）")
    net.load_ontology_from_string("Employee（Bob）")

    all_facts = net.get_all_facts()
    bob_working = [f for f in all_facts if f.get('type') == 'instance_of'
                   and f.get('individual') == 'Bob'
                   and f.get('concept') == 'WorkingParent']

    if len(bob_working) > 0:
        print("✓ PASS: Bob inferred as WorkingParent via intersection")
        return True
    else:
        print("✗ FAIL: Bob not inferred as WorkingParent")
        return False

def test_some_values_from():
    """Test 9.2: SomeValuesFrom - Parent ≡ᑦ ∃hasChild․Person"""
    print("\n" + "="*80)
    print("TEST 12: SomeValuesFrom Restriction")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Parent ≡ᑦ ∃hasChild․Person")
    net.load_ontology_from_string("Person（Child1）")
    net.load_ontology_from_string("hasChild（Alice，Child1）")

    all_facts = net.get_all_facts()
    alice_parent = [f for f in all_facts if f.get('type') == 'instance_of'
                    and f.get('individual') == 'Alice'
                    and f.get('concept') == 'Parent']

    if len(alice_parent) > 0:
        print("✓ PASS: Alice inferred as Parent via SomeValuesFrom")
        return True
    else:
        print("✗ FAIL: Alice not inferred as Parent")
        return False

def run_all_tests():
    """Run all core grammar statement tests"""
    print("\n" + "="*80)
    print("CORE GRAMMAR STATEMENT TEST SUITE")
    print("Testing most important statement types from dl.lark")
    print("="*80)

    tests = [
        test_subsumption,
        test_class_equivalence,
        test_disjoint_classes,
        test_property_subsumption,
        test_property_chain,
        test_class_assertion,
        test_property_assertion,
        test_data_property_assertion,
        test_same_individuals,
        test_class_union,
        test_class_intersection,
        test_some_values_from,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"\n>>> Starting: {test.__name__}")
            result = test()
            print(f">>> Finished: {test.__name__} - {'PASS' if result else 'FAIL'}")
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ EXCEPTION in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Final Summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {100 * passed / (passed + failed):.1f}%")

    if failed == 0:
        print("\n🎉 ALL CORE GRAMMAR TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(run_all_tests())
