"""
Test restriction-based schema rules from schema.owlrl.jena
All tests use LARK grammar syntax - NO add_fact() calls
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_scm_svf1():
    """Test: scm-svf1 - someValuesFrom with filler subsumption
    If C1 has ∃P․Y1, C2 has ∃P․Y2, and Y1 ⊑ Y2, then C1 ⊑ C2"""
    print("=" * 60)
    print("TEST: scm-svf1 (someValuesFrom Filler Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    # We need to reference the restrictions, not assert their subsumption
    # Using subsumptions with restrictions as sub/sup concepts
    ontology = """
    Student ⊑ᑦ Person
    TeachesStudents ⊑ᑦ ∃teaches․Student
    TeachesPersons ⊑ᑦ ∃teaches․Person
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that the subsumption is inferred
    result = reasoner.query(type="subsumption")
    print(f"Total subsumptions: {len(result)}")

    # Find the inferred restriction subsumption
    inferred = [r for r in result if r.get('inferred_by') == 'scm-svf1']
    print(f"Subsumptions inferred by scm-svf1: {len(inferred)}")
    if inferred:
        for inf in inferred:
            print(f"  {inf.get('sub')} ⊑ {inf.get('sup')}")

    success = len(inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_svf2():
    """Test: scm-svf2 - someValuesFrom with property subsumption
    If C1 has ∃P1․Y, C2 has ∃P2․Y, and P1 ⊏ P2, then C1 ⊑ C2"""
    print("\n" + "=" * 60)
    print("TEST: scm-svf2 (someValuesFrom Property Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    likes ⊑ᴿ knows
    ∃likes․Person ⊑ᑦ ∃knows․Person
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that the restriction subsumption is inferred
    inferred = reasoner.query(type="subsumption", inferred_by="scm-svf2")
    print(f"Subsumptions inferred by scm-svf2: {len(inferred)}")
    if inferred:
        for inf in inferred:
            print(f"  {inf.get('sub')} ⊑ {inf.get('sup')}")

    success = len(inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_avf1():
    """Test: scm-avf1 - allValuesFrom with filler subsumption
    If C1 has ∀P․Y1, C2 has ∀P․Y2, and Y1 ⊑ Y2, then C1 ⊑ C2"""
    print("\n" + "=" * 60)
    print("TEST: scm-avf1 (allValuesFrom Filler Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    ∀teaches․Student ⊑ᑦ ∀teaches․Person
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that the subsumption is inferred
    inferred = reasoner.query(type="subsumption", inferred_by="scm-avf1")
    print(f"Subsumptions inferred by scm-avf1: {len(inferred)}")
    if inferred:
        for inf in inferred:
            print(f"  {inf.get('sub')} ⊑ {inf.get('sup')}")

    success = len(inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_avf2():
    """Test: scm-avf2 - allValuesFrom with property subsumption (REVERSED)
    If C1 has ∀P1․Y, C2 has ∀P2․Y, and P1 ⊏ P2, then C2 ⊑ C1"""
    print("\n" + "=" * 60)
    print("TEST: scm-avf2 (allValuesFrom Property Subsumption - Reversed)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    hasChild ⊑ᴿ hasDescendant
    ∀hasChild․Student ⊑ᑦ ∀hasDescendant․Student
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that the REVERSED subsumption is inferred
    # Should infer: ∀hasDescendant․Student ⊑ ∀hasChild․Student
    inferred = reasoner.query(type="subsumption", inferred_by="scm-avf2")
    print(f"Subsumptions inferred by scm-avf2: {len(inferred)}")
    if inferred:
        for inf in inferred:
            print(f"  {inf.get('sub')} ⊑ {inf.get('sup')} (note: reversed direction)")

    success = len(inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_combined_restrictions():
    """Test: Combined restriction reasoning
    Multiple restriction rules working together"""
    print("\n" + "=" * 60)
    print("TEST: Combined Restriction Reasoning")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    Person ⊑ᑦ Animal
    likes ⊑ᴿ knows
    ∃likes․Student ⊑ᑦ ∃knows․Animal
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer:
    # 1. Student ⊑ Animal (scm-sco transitivity)
    # 2. ∃likes․Student ⊑ ∃likes․Person (scm-svf1 from Student ⊑ Person)
    # 3. ∃likes․Person ⊑ ∃likes․Animal (scm-svf1 from Person ⊑ Animal)
    # 4. ∃likes․Student ⊑ ∃knows․Student (scm-svf2 from likes ⊏ knows)
    # 5. ∃knows․Student ⊑ ∃knows․Animal (scm-svf1 from Student ⊑ Animal)

    svf1_inferred = reasoner.query(type="subsumption", inferred_by="scm-svf1")
    svf2_inferred = reasoner.query(type="subsumption", inferred_by="scm-svf2")
    sco_inferred = reasoner.query(type="subsumption", inferred_by="scm-sco")

    print(f"Subsumptions by scm-sco: {len(sco_inferred)}")
    print(f"Subsumptions by scm-svf1: {len(svf1_inferred)}")
    print(f"Subsumptions by scm-svf2: {len(svf2_inferred)}")

    success = len(svf1_inferred) > 0 and len(svf2_inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_nested_restrictions():
    """Test: Nested restriction reasoning"""
    print("\n" + "=" * 60)
    print("TEST: Nested Restriction Reasoning")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    ∃owns․Dog ⊑ᑦ ∃owns․Animal
    ∀cares․Cat ⊑ᑦ ∀cares․Animal
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check multiple restriction inferences
    svf1_inferred = reasoner.query(type="subsumption", inferred_by="scm-svf1")
    avf1_inferred = reasoner.query(type="subsumption", inferred_by="scm-avf1")

    print(f"someValuesFrom inferences: {len(svf1_inferred)}")
    print(f"allValuesFrom inferences: {len(avf1_inferred)}")

    for inf in svf1_inferred:
        print(f"  ∃ restriction: {inf.get('sub')} ⊑ {inf.get('sup')}")
    for inf in avf1_inferred:
        print(f"  ∀ restriction: {inf.get('sub')} ⊑ {inf.get('sup')}")

    success = len(svf1_inferred) > 0 and len(avf1_inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "scm-svf1": test_scm_svf1(),
        "scm-svf2": test_scm_svf2(),
        "scm-avf1": test_scm_avf1(),
        "scm-avf2": test_scm_avf2(),
        "Combined Restrictions": test_scm_combined_restrictions(),
        "Nested Restrictions": test_scm_nested_restrictions()
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
