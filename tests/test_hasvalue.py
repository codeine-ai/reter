"""
Test hasValue restriction detection and reasoning
Tests for detect-hasvalue, cls-hv1, cls-hv2, scm-hv
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_hasvalue_detection():
    """Test: detect-hasvalue - Extract hasValue from C ≡ ∃R.{a} pattern"""
    print("=" * 60)
    print("TEST: detect-hasvalue (HasValue Detection)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    LikesJohn ≡ᑦ ∃likes․｛John｝
    HasMotherMary ≡ᑦ ∃hasMother․｛Mary｝
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for detected hasValue restrictions
    hasvalues = reasoner.query(type='has_value')
    print(f"\nHasValue restrictions detected: {len(hasvalues)}")

    expected_hasvalues = {
        ('LikesJohn', 'likes', 'John'),
        ('HasMotherMary', 'hasMother', 'Mary')
    }
    found_hasvalues = set()

    for hv in hasvalues:
        concept = hv.get('id')
        prop = hv.get('property')
        value = hv.get('value')
        inferred_by = hv.get('inferred_by', '')
        print(f"  {concept} ≡ ∃{prop}.{{{value}}} (by {inferred_by})")
        found_hasvalues.add((concept, prop, value))

    success = expected_hasvalues.issubset(found_hasvalues)
    print(f"\n✓ Expected: {expected_hasvalues}")
    print(f"✓ Found: {found_hasvalues}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_cls_hv1():
    """Test: cls-hv1 - If X is instance of hasValue restriction, infer property assertion
    If C ≡ ∃R.{a} and X:C, then R(X, a)
    """
    print("\n" + "=" * 60)
    print("TEST: cls-hv1 (HasValue Forward)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    LikesJohn ≡ᑦ ∃likes․｛John｝
    LikesJohn（Alice）
    LikesJohn（Bob）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for inferred property assertions
    likes_assertions = reasoner.query(type='role_assertion', role='likes', object='John')
    print(f"\nProperty assertions for likes(?, John): {len(likes_assertions)}")

    found_subjects = set()
    cls_hv1_found = False

    for assertion in likes_assertions:
        subj = assertion.get('subject')
        inferred_by = assertion.get('inferred_by', '')
        print(f"  likes({subj}, John) (by {inferred_by})")
        found_subjects.add(subj)
        if inferred_by == 'cls-hv1':
            cls_hv1_found = True

    expected = {'Alice', 'Bob'}
    success = expected.issubset(found_subjects) and cls_hv1_found

    print(f"\n✓ Expected subjects: {expected}")
    print(f"✓ Found subjects: {found_subjects}")
    print(f"✓ cls-hv1 fired: {cls_hv1_found}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_cls_hv2():
    """Test: cls-hv2 - If X has property assertion, infer instance of hasValue restriction
    If C ≡ ∃R.{a} and R(X, a), then X:C
    """
    print("\n" + "=" * 60)
    print("TEST: cls-hv2 (HasValue Backward)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    LikesJohn ≡ᑦ ∃likes․｛John｝
    likes（Alice， John）
    likes（Bob， John）
    likes（Charlie， Mary）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for inferred class memberships
    likes_john_instances = reasoner.query(type='instance_of', concept='LikesJohn')
    print(f"\nInstances of LikesJohn: {len(likes_john_instances)}")

    found_individuals = set()
    cls_hv2_found = False

    for inst in likes_john_instances:
        indiv = inst.get('individual')
        inferred_by = inst.get('inferred_by', '')
        print(f"  {indiv} : LikesJohn (by {inferred_by})")
        found_individuals.add(indiv)
        if inferred_by == 'cls-hv2':
            cls_hv2_found = True

    # Alice and Bob should be inferred as LikesJohn, but not Charlie
    expected = {'Alice', 'Bob'}
    success = expected.issubset(found_individuals) and cls_hv2_found and 'Charlie' not in found_individuals

    print(f"\n✓ Expected individuals: {expected}")
    print(f"✓ Found individuals: {found_individuals}")
    print(f"✓ cls-hv2 fired: {cls_hv2_found}")
    print(f"✓ Charlie not in LikesJohn: {'Charlie' not in found_individuals}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_hv():
    """Test: scm-hv - HasValue subsumption based on property subsumption
    If C1 ≡ ∃P1.{a}, C2 ≡ ∃P2.{a}, and P1 ⊏ P2, then C1 ⊑ C2
    """
    print("\n" + "=" * 60)
    print("TEST: scm-hv (HasValue Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    likes ⊑ᴿ knows
    LikesJohn ≡ᑦ ∃likes․｛John｝
    KnowsJohn ≡ᑦ ∃knows․｛John｝
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for inferred subsumption
    subsumptions = reasoner.query(type='subsumption', sub='LikesJohn', sup='KnowsJohn')
    print(f"\nSubsumptions LikesJohn ⊑ KnowsJohn: {len(subsumptions)}")

    scm_hv_found = False
    for sub in subsumptions:
        inferred_by = sub.get('inferred_by', '')
        print(f"  LikesJohn ⊑ KnowsJohn (by {inferred_by})")
        if inferred_by == 'scm-hv':
            scm_hv_found = True

    success = len(subsumptions) > 0 and scm_hv_found

    print(f"\n✓ Subsumption found: {len(subsumptions) > 0}")
    print(f"✓ scm-hv fired: {scm_hv_found}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_hasvalue_combined():
    """Test: Combined hasValue reasoning with multiple rules"""
    print("\n" + "=" * 60)
    print("TEST: Combined HasValue Reasoning")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    likes ⊑ᴿ knows
    LikesJohn ≡ᑦ ∃likes․｛John｝
    KnowsJohn ≡ᑦ ∃knows․｛John｝

    LikesJohn（Alice）
    likes（Bob， John）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check various inferences
    print("\n1. HasValue detection:")
    hasvalues = reasoner.query(type='has_value')
    for hv in hasvalues:
        print(f"   {hv.get('id')} ≡ ∃{hv.get('property')}.{{{hv.get('value')}}}")

    print("\n2. Property assertions (cls-hv1):")
    likes_assertions = reasoner.query(type='role_assertion', role='likes', object='John')
    for assertion in likes_assertions:
        print(f"   likes({assertion.get('subject')}, John)")

    print("\n3. Class memberships (cls-hv2):")
    likes_john_instances = reasoner.query(type='instance_of', concept='LikesJohn')
    for inst in likes_john_instances:
        print(f"   {inst.get('individual')} : LikesJohn")

    print("\n4. HasValue subsumptions (scm-hv):")
    subsumptions = reasoner.query(type='subsumption', sub='LikesJohn')
    for sub in subsumptions:
        if sub.get('inferred_by') == 'scm-hv':
            print(f"   LikesJohn ⊑ {sub.get('sup')}")

    # Verify all expected inferences
    has_detection = len(hasvalues) >= 2
    has_assertions = len(likes_assertions) >= 2
    has_instances = len(likes_john_instances) >= 2
    has_subsumption = any(s.get('inferred_by') == 'scm-hv' for s in subsumptions)

    success = has_detection and has_assertions and has_instances and has_subsumption

    print(f"\n✓ HasValue detected: {has_detection}")
    print(f"✓ Property assertions inferred: {has_assertions}")
    print(f"✓ Class memberships inferred: {has_instances}")
    print(f"✓ Subsumptions inferred: {has_subsumption}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "HasValue Detection": test_hasvalue_detection(),
        "cls-hv1": test_cls_hv1(),
        "cls-hv2": test_cls_hv2(),
        "scm-hv": test_scm_hv(),
        "Combined": test_hasvalue_combined()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(1 for p in results.values() if p)
    print(f"\nTotal: {passed}/{total} tests passed")
