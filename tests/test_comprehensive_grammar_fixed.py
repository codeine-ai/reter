#!/usr/bin/env python3
"""
Comprehensive Grammar Test Suite - FIXED VERSION
Tests ALL major statement types from dl.lark grammar
Uses correct query pattern: get_all_facts() + filter
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter_core import owl_rete_cpp

def test_class_axioms():
    """Test Class Axioms (Subsumption & Equivalence)"""
    print("\n" + "="*80)
    print("CATEGORY 1: CLASS AXIOMS")
    print("="*80)

    passed = 0
    total = 0

    # 1.1 Subsumption (SubClassOf)
    total += 1
    print("\n1.1 Subsumption: Dog ⊑ᑦ Animal")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Dog ⊑ᑦ Animal")
        net.load_ontology_from_string("Dog（Fido）")
        all_facts = net.get_all_facts()
        fido_animal = [f for f in all_facts if f.get('type') == 'instance_of'
                       and f.get('individual') == 'Fido' and f.get('concept') == 'Animal']
        if len(fido_animal) > 0:
            print("✓ PASS: Fido inferred as Animal")
            passed += 1
        else:
            print("✗ FAIL: Fido not inferred as Animal")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 1.2 Inverse Subsumption
    total += 1
    print("\n1.2 Inverse Subsumption: Animal ⊒ᑦ Cat")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Animal ⊒ᑦ Cat")
        net.load_ontology_from_string("Cat（Whiskers）")
        all_facts = net.get_all_facts()
        whiskers_animal = [f for f in all_facts if f.get('type') == 'instance_of'
                          and f.get('individual') == 'Whiskers' and f.get('concept') == 'Animal']
        if len(whiskers_animal) > 0:
            print("✓ PASS: Whiskers inferred as Animal")
            passed += 1
        else:
            print("✗ FAIL: Whiskers not inferred as Animal")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 1.3 Class Equivalence
    total += 1
    print("\n1.3 Class Equivalence: Human ≡ᑦ Person")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Human ≡ᑦ Person")
        net.load_ontology_from_string("Human（Alice）")
        all_facts = net.get_all_facts()
        alice_person = [f for f in all_facts if f.get('type') == 'instance_of'
                       and f.get('individual') == 'Alice' and f.get('concept') == 'Person']
        if len(alice_person) > 0:
            print("✓ PASS: Alice inferred as Person")
            passed += 1
        else:
            print("✗ FAIL: Alice not inferred as Person")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 1.4 Class Equivalence List
    total += 1
    print("\n1.4 Class Equivalence List: ≡ᑦ（Human，Person，Individual）")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("≡ᑦ（Human，Person，Individual）")
        net.load_ontology_from_string("Human（Bob）")
        all_facts = net.get_all_facts()
        bob_individual = [f for f in all_facts if f.get('type') == 'instance_of'
                         and f.get('individual') == 'Bob' and f.get('concept') == 'Individual']
        if len(bob_individual) > 0:
            print("✓ PASS: Bob inferred as Individual")
            passed += 1
        else:
            print("✗ FAIL: Bob not inferred as Individual")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 1.5 Disjoint Classes
    total += 1
    print("\n1.5 Disjoint Classes: ¬≡ᑦ（Male，Female）")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("¬≡ᑦ（Male，Female）")
        net.load_ontology_from_string("Male（Charlie）")
        net.load_ontology_from_string("Female（Charlie）")
        all_facts = net.get_all_facts()
        errors = [f for f in all_facts if f.get('type') == 'inconsistency']
        if len(errors) > 0:
            print(f"✓ PASS: Detected disjoint classes violation ({len(errors)} errors)")
            passed += 1
        else:
            print("✗ FAIL: Should detect disjoint classes violation")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 1.6 Disjoint Union
    total += 1
    print("\n1.6 Disjoint Union: Parent ¬≡ᑦ（Mother，Father）")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Parent ¬≡ᑦ（Mother，Father）")
        net.load_ontology_from_string("Mother（Alice）")
        all_facts = net.get_all_facts()
        alice_parent = [f for f in all_facts if f.get('type') == 'instance_of'
                       and f.get('individual') == 'Alice' and f.get('concept') == 'Parent']
        if len(alice_parent) > 0:
            print("✓ PASS: Alice inferred as Parent from disjoint union")
            passed += 1
        else:
            print("✗ FAIL: Alice not inferred as Parent")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    print(f"\n{'='*80}")
    print(f"CLASS AXIOMS: {passed}/{total} passed")
    return passed, total


def test_property_axioms():
    """Test Object and Data Property Axioms"""
    print("\n" + "="*80)
    print("CATEGORY 2: PROPERTY AXIOMS")
    print("="*80)

    passed = 0
    total = 0

    # 3.1 Object Property Subsumption
    total += 1
    print("\n3.1 Object Property Subsumption: hasParent ⊑ᴿ hasAncestor")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("hasParent ⊑ᴿ hasAncestor")
        net.load_ontology_from_string("hasParent（Alice，Bob）")
        all_facts = net.get_all_facts()
        alice_ancestor = [f for f in all_facts if f.get('type') == 'role_assertion'
                         and f.get('subject') == 'Alice' and f.get('role') == 'hasAncestor'
                         and f.get('object') == 'Bob']
        if len(alice_ancestor) > 0:
            print("✓ PASS: hasAncestor inferred from hasParent")
            passed += 1
        else:
            print("✗ FAIL: hasAncestor not inferred")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 3.3 Object Property Equivalence
    total += 1
    print("\n3.3 Object Property Equivalence: spouse ≡ᴿ marriedTo")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("spouse ≡ᴿ marriedTo")
        net.load_ontology_from_string("spouse（Alice，Bob）")
        all_facts = net.get_all_facts()
        alice_married = [f for f in all_facts if f.get('type') == 'role_assertion'
                        and f.get('subject') == 'Alice' and f.get('role') == 'marriedTo'
                        and f.get('object') == 'Bob']
        if len(alice_married) > 0:
            print("✓ PASS: marriedTo inferred from spouse")
            passed += 1
        else:
            print("✗ FAIL: marriedTo not inferred")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 3.6 Property Chain
    total += 1
    print("\n3.6 Property Chain: hasParent ∘ hasBrother ⊑ᴿ hasUncle")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("hasParent ∘ hasBrother ⊑ᴿ hasUncle")
        net.load_ontology_from_string("hasParent（Alice，Bob）")
        net.load_ontology_from_string("hasBrother（Bob，Charlie）")
        all_facts = net.get_all_facts()
        alice_uncle = [f for f in all_facts if f.get('type') == 'role_assertion'
                      and f.get('subject') == 'Alice' and f.get('role') == 'hasUncle'
                      and f.get('object') == 'Charlie']
        if len(alice_uncle) > 0:
            print("✓ PASS: hasUncle inferred via property chain")
            passed += 1
        else:
            print("✗ FAIL: hasUncle not inferred")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    print(f"\n{'='*80}")
    print(f"PROPERTY AXIOMS: {passed}/{total} passed")
    return passed, total


def test_assertions():
    """Test Individual Assertions"""
    print("\n" + "="*80)
    print("CATEGORY 3: ASSERTIONS")
    print("="*80)

    passed = 0
    total = 0

    # 5.1 Class Assertion
    total += 1
    print("\n5.1 Class Assertion: Person（Alice）")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Person（Alice）")
        all_facts = net.get_all_facts()
        alice_person = [f for f in all_facts if f.get('type') == 'instance_of'
                       and f.get('individual') == 'Alice' and f.get('concept') == 'Person']
        if len(alice_person) > 0:
            print("✓ PASS: Alice is Person")
            passed += 1
        else:
            print("✗ FAIL: Alice not found as Person")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 5.2 Object Property Assertion
    total += 1
    print("\n5.2 Object Property Assertion: knows（Alice，Bob）")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("knows（Alice，Bob）")
        all_facts = net.get_all_facts()
        alice_knows = [f for f in all_facts if f.get('type') == 'role_assertion'
                      and f.get('subject') == 'Alice' and f.get('role') == 'knows'
                      and f.get('object') == 'Bob']
        if len(alice_knows) > 0:
            print("✓ PASS: Alice knows Bob")
            passed += 1
        else:
            print("✗ FAIL: Alice knows Bob not found")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 5.3 Data Property Assertion
    total += 1
    print("\n5.3 Data Property Assertion: hasAge（Alice，30）")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("hasAge（Alice，30）")
        all_facts = net.get_all_facts()
        alice_age = [f for f in all_facts if f.get('type') == 'data_assertion'
                    and f.get('subject') == 'Alice' and f.get('property') == 'hasAge'
                    and f.get('value') == '30']
        if len(alice_age) > 0:
            print("✓ PASS: Alice has age 30")
            passed += 1
        else:
            print("✗ FAIL: Alice age 30 not found")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 5.4 Same Individuals
    total += 1
    print("\n5.4 Same Individuals: Alice ﹦ AliceSmith")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Alice ﹦ AliceSmith")
        all_facts = net.get_all_facts()
        same_as = [f for f in all_facts if f.get('type') == 'same_as'
                  and ((f.get('ind1') == 'Alice' and f.get('ind2') == 'AliceSmith')
                       or (f.get('ind1') == 'AliceSmith' and f.get('ind2') == 'Alice'))]
        if len(same_as) > 0:
            print("✓ PASS: Alice sameAs AliceSmith")
            passed += 1
        else:
            print("✗ FAIL: Same individuals assertion not found")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 5.5 Different Individuals
    total += 1
    print("\n5.5 Different Individuals: Alice ≠ Bob")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Alice ≠ Bob")
        all_facts = net.get_all_facts()
        different = [f for f in all_facts if f.get('type') == 'different_from'
                    and ((f.get('ind1') == 'Alice' and f.get('ind2') == 'Bob')
                         or (f.get('ind1') == 'Bob' and f.get('ind2') == 'Alice'))]
        if len(different) > 0:
            print("✓ PASS: Alice different from Bob")
            passed += 1
        else:
            print("✗ FAIL: Different individuals assertion not found")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    print(f"\n{'='*80}")
    print(f"ASSERTIONS: {passed}/{total} passed")
    return passed, total


def test_class_expressions():
    """Test Class Expressions (Boolean Operators)"""
    print("\n" + "="*80)
    print("CATEGORY 4: CLASS EXPRESSIONS")
    print("="*80)

    passed = 0
    total = 0

    # 8.7 Class Union
    total += 1
    print("\n8.7 Class Union: Parent ≡ᑦ Mother ⊔ Father")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Parent ≡ᑦ Mother ⊔ Father")
        net.load_ontology_from_string("Mother（Alice）")
        all_facts = net.get_all_facts()
        alice_parent = [f for f in all_facts if f.get('type') == 'instance_of'
                       and f.get('individual') == 'Alice' and f.get('concept') == 'Parent']
        if len(alice_parent) > 0:
            print("✓ PASS: Alice inferred as Parent via union")
            passed += 1
        else:
            print("✗ FAIL: Alice not inferred as Parent")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 8.8 Class Intersection
    total += 1
    print("\n8.8 Class Intersection: WorkingParent ≡ᑦ Parent ⊓ Employee")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("WorkingParent ≡ᑦ Parent ⊓ Employee")
        net.load_ontology_from_string("Parent（Bob）")
        net.load_ontology_from_string("Employee（Bob）")
        all_facts = net.get_all_facts()
        bob_working = [f for f in all_facts if f.get('type') == 'instance_of'
                      and f.get('individual') == 'Bob' and f.get('concept') == 'WorkingParent']
        if len(bob_working) > 0:
            print("✓ PASS: Bob inferred as WorkingParent via intersection")
            passed += 1
        else:
            print("✗ FAIL: Bob not inferred as WorkingParent")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 8.9 Class Complement
    total += 1
    print("\n8.9 Class Complement: NonPerson ≡ᑦ ¬Person")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("NonPerson ≡ᑦ ¬Person")
        net.load_ontology_from_string("Person（Alice）")
        all_facts = net.get_all_facts()
        alice_nonperson = [f for f in all_facts if f.get('type') == 'instance_of'
                          and f.get('individual') == 'Alice' and f.get('concept') == 'NonPerson']
        if len(alice_nonperson) == 0:
            print("✓ PASS: Alice not inferred as NonPerson (correct)")
            passed += 1
        else:
            print("✗ FAIL: Alice incorrectly inferred as NonPerson")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    print(f"\n{'='*80}")
    print(f"CLASS EXPRESSIONS: {passed}/{total} passed")
    return passed, total


def test_restrictions():
    """Test Property Restrictions"""
    print("\n" + "="*80)
    print("CATEGORY 5: RESTRICTIONS")
    print("="*80)

    passed = 0
    total = 0

    # 9.2 SomeValuesFrom
    total += 1
    print("\n9.2 SomeValuesFrom: Parent ≡ᑦ ∃hasChild․Person")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("Parent ≡ᑦ ∃hasChild․Person")
        net.load_ontology_from_string("Person（Child1）")
        net.load_ontology_from_string("hasChild（Alice，Child1）")
        all_facts = net.get_all_facts()
        alice_parent = [f for f in all_facts if f.get('type') == 'instance_of'
                       and f.get('individual') == 'Alice' and f.get('concept') == 'Parent']
        if len(alice_parent) > 0:
            print("✓ PASS: Alice inferred as Parent via SomeValuesFrom")
            passed += 1
        else:
            print("✗ FAIL: Alice not inferred as Parent")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    # 9.1 AllValuesFrom
    total += 1
    print("\n9.1 AllValuesFrom: HappyParent ≡ᑦ ∀hasChild․Happy")
    try:
        net = owl_rete_cpp.ReteNetwork()
        net.load_ontology_from_string("HappyParent ≡ᑦ ∀hasChild․Happy")
        net.load_ontology_from_string("HappyParent（Alice）")
        net.load_ontology_from_string("hasChild（Alice，Child1）")
        all_facts = net.get_all_facts()
        child_happy = [f for f in all_facts if f.get('type') == 'instance_of'
                      and f.get('individual') == 'Child1' and f.get('concept') == 'Happy']
        if len(child_happy) > 0:
            print("✓ PASS: Child1 inferred as Happy via AllValuesFrom")
            passed += 1
        else:
            print("✗ FAIL: Child1 not inferred as Happy")
    except Exception as e:
        print(f"✗ ERROR: {e}")

    print(f"\n{'='*80}")
    print(f"RESTRICTIONS: {passed}/{total} passed")
    return passed, total


def run_all_tests():
    """Run all comprehensive grammar tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE GRAMMAR TEST SUITE")
    print("Testing major statement types from dl.lark")
    print("="*80)

    results = []

    results.append(test_class_axioms())
    results.append(test_property_axioms())
    results.append(test_assertions())
    results.append(test_class_expressions())
    results.append(test_restrictions())

    total_passed = sum(r[0] for r in results)
    total_tests = sum(r[1] for r in results)

    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {100 * total_passed / total_tests:.1f}%")

    if total_passed == total_tests:
        print("\n🎉 ALL COMPREHENSIVE GRAMMAR TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {total_tests - total_passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
