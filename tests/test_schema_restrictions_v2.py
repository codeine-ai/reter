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
    If C1 has ∃P․Y1, C2 has ∃P․Y2, and Y1 ⊑ Y2, then C1 ⊑ C2

    Schema: TeachesStudents ≡ ∃teaches․Student
            TeachesPersons ≡ ∃teaches․Person
            Student ⊑ Person
    Inference: TeachesStudents ⊑ TeachesPersons"""
    print("=" * 60)
    print("TEST: scm-svf1 (someValuesFrom Filler Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    TeachesStudents ≡ᑦ ∃teaches․Student
    TeachesPersons ≡ᑦ ∃teaches․Person
    """
    reasoner.load_ontology(ontology)
    

    # The rule should infer: ∃teaches․Student ⊑ ∃teaches․Person
    # Which through equivalences gives: TeachesStudents ⊑ TeachesPersons
    inferred = reasoner.query(type="subsumption", inferred_by="scm-svf1")
    print(f"Subsumptions inferred by scm-svf1: {len(inferred)}")
    if inferred:
        for inf in inferred:
            print(f"  {inf.get('sub')} ⊑ {inf.get('sup')}")

    success = len(inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_svf2():
    """Test: scm-svf2 - someValuesFrom with property subsumption
    If C1 has ∃P1․Y, C2 has ∃P2․Y, and P1 ⊏ P2, then C1 ⊑ C2

    Schema: LikesPerson ≡ ∃likes․Person
            KnowsPerson ≡ ∃knows․Person
            likes ⊏ knows
    Inference: LikesPerson ⊑ KnowsPerson"""
    print("\n" + "=" * 60)
    print("TEST: scm-svf2 (someValuesFrom Property Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    likes ⊑ᴿ knows
    LikesPerson ≡ᑦ ∃likes․Person
    KnowsPerson ≡ᑦ ∃knows․Person
    """
    reasoner.load_ontology(ontology)
    

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
    TeachesOnlyStudents ≡ᑦ ∀teaches․Student
    TeachesOnlyPersons ≡ᑦ ∀teaches․Person
    """
    reasoner.load_ontology(ontology)
    

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
    If C1 has ∀P1․Y, C2 has ∀P2․Y, and P1 ⊏ P2, then C2 ⊑ C1 (reversed!)"""
    print("\n" + "=" * 60)
    print("TEST: scm-avf2 (allValuesFrom Property Subsumption - Reversed)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    hasChild ⊑ᴿ hasDescendant
    HasOnlyChildrenStudents ≡ᑦ ∀hasChild․Student
    HasOnlyDescendantsStudents ≡ᑦ ∀hasDescendant․Student
    """
    reasoner.load_ontology(ontology)
    

    inferred = reasoner.query(type="subsumption", inferred_by="scm-avf2")
    print(f"Subsumptions inferred by scm-avf2: {len(inferred)}")
    if inferred:
        for inf in inferred:
            print(f"  {inf.get('sub')} ⊑ {inf.get('sup')} (note: reversed direction)")

    success = len(inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_combined():
    """Test: Multiple restriction rules together

    To trigger restriction rules, we need BOTH restrictions to exist.
    This test creates three restrictions with the same property but different fillers,
    and two restrictions with different properties but same filler.
    """
    print("\n" + "=" * 60)
    print("TEST: Combined Restriction Rules")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    Person ⊑ᑦ Animal
    likes ⊑ᴿ knows

    LikesStudents ≡ᑦ ∃likes․Student
    LikesPersons ≡ᑦ ∃likes․Person
    KnowsStudents ≡ᑦ ∃knows․Student
    """
    reasoner.load_ontology(ontology)
    

    # Should infer:
    # ∃likes․Student ⊑ ∃likes․Person (scm-svf1: same property, Student ⊑ Person)
    # ∃likes․Student ⊑ ∃knows․Student (scm-svf2: same filler, likes ⊏ knows)

    svf1_inferred = reasoner.query(type="subsumption", inferred_by="scm-svf1")
    svf2_inferred = reasoner.query(type="subsumption", inferred_by="scm-svf2")
    sco_inferred = reasoner.query(type="subsumption", inferred_by="scm-sco")

    print(f"Subsumptions by scm-sco: {len(sco_inferred)}")
    print(f"Subsumptions by scm-svf1: {len(svf1_inferred)}")
    if svf1_inferred:
        for inf in svf1_inferred:
            print(f"  {inf.get('sub')} ⊑ {inf.get('sup')}")

    print(f"Subsumptions by scm-svf2: {len(svf2_inferred)}")
    if svf2_inferred:
        for inf in svf2_inferred:
            print(f"  {inf.get('sub')} ⊑ {inf.get('sup')}")

    success = len(svf1_inferred) > 0 and len(svf2_inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "scm-svf1": test_scm_svf1(),
        "scm-svf2": test_scm_svf2(),
        "scm-avf1": test_scm_avf1(),
        "scm-avf2": test_scm_avf2(),
        "Combined": test_scm_combined()
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
