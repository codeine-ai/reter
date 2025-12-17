"""
Test schema rules from schema.owlrl.jena
All tests use LARK grammar syntax - NO add_fact() calls
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_scm_sco():
    """Test: scm-sco - Subsumption transitivity
    If A ⊑ B and B ⊑ C, then A ⊑ C"""
    print("=" * 60)
    print("TEST: scm-sco (Subsumption Transitivity)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    Person ⊑ᑦ Animal
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Student ⊑ Animal is inferred
    trans_sub = reasoner.query(type="subsumption", sub="Student", sup="Animal")
    print(f"Transitive subsumption (Student ⊑ Animal): {len(trans_sub)}")
    if trans_sub:
        print(f"  Inferred by: {trans_sub[0].get('inferred_by')}")

    success = len(trans_sub) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_eqc1():
    """Test: scm-eqc1 - Equivalence to mutual subsumption
    If C1 ≡ C2 and C1 != C2, then C1 ⊑ C2 and C2 ⊑ C1"""
    print("\n" + "=" * 60)
    print("TEST: scm-eqc1 (Equivalence to Mutual Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ≡ᑦ Pupil
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Student ⊑ Pupil and Pupil ⊑ Student are inferred
    student_pupil = reasoner.query(type="subsumption", sub="Student", sup="Pupil")
    pupil_student = reasoner.query(type="subsumption", sub="Pupil", sup="Student")

    print(f"Student ⊑ Pupil: {len(student_pupil) > 0}")
    print(f"Pupil ⊑ Student: {len(pupil_student) > 0}")
    if student_pupil:
        print(f"  Inferred by: {student_pupil[0].get('inferred_by')}")

    success = len(student_pupil) > 0 and len(pupil_student) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_eqc2():
    """Test: scm-eqc2 - Mutual subsumption to equivalence
    If C1 ⊑ C2 and C2 ⊑ C1 and C1 != C2, then C1 ≡ C2"""
    print("\n" + "=" * 60)
    print("TEST: scm-eqc2 (Mutual Subsumption to Equivalence)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Pupil
    Pupil ⊑ᑦ Student
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Student ≡ Pupil is inferred
    equiv = reasoner.query(type="equivalence", concept1="Student", concept2="Pupil")
    print(f"Equivalence (Student ≡ Pupil): {len(equiv)}")
    if equiv:
        print(f"  Inferred by: {equiv[0].get('inferred_by')}")

    success = len(equiv) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_eqc_roundtrip():
    """Test: scm-eqc1 + scm-eqc2 roundtrip
    Equivalence ↔ Mutual subsumption"""
    print("\n" + "=" * 60)
    print("TEST: scm-eqc Roundtrip")
    print("=" * 60)

    reasoner = Reter()
    # Start with equivalence
    ontology = """
    Adult ≡ᑦ Grownup
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check mutual subsumption from equivalence
    adult_grownup = reasoner.query(type="subsumption", sub="Adult", sup="Grownup")
    grownup_adult = reasoner.query(type="subsumption", sub="Grownup", sup="Adult")

    print(f"From equivalence to mutual subsumption:")
    print(f"  Adult ⊑ Grownup: {len(adult_grownup) > 0}")
    print(f"  Grownup ⊑ Adult: {len(grownup_adult) > 0}")

    success = len(adult_grownup) > 0 and len(grownup_adult) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_eqp1():
    """Test: scm-eqp1 - Property equivalence to mutual subsumption
    If P1 ≣ P2 and P1 != P2, then P1 ⊏ P2 and P2 ⊏ P1"""
    print("\n" + "=" * 60)
    print("TEST: scm-eqp1 (Property Equivalence to Mutual Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    knows ≡ᴿ acquaintedWith
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that knows ⊏ acquaintedWith and acquaintedWith ⊏ knows are inferred
    knows_acq = reasoner.query(type="sub_property", sub="knows", sup="acquaintedWith")
    acq_knows = reasoner.query(type="sub_property", sub="acquaintedWith", sup="knows")

    print(f"knows ⊏ acquaintedWith: {len(knows_acq) > 0}")
    print(f"acquaintedWith ⊏ knows: {len(acq_knows) > 0}")
    if knows_acq:
        print(f"  Inferred by: {knows_acq[0].get('inferred_by')}")

    success = len(knows_acq) > 0 and len(acq_knows) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_eqp2():
    """Test: scm-eqp2 - Mutual property subsumption to equivalence
    If P1 ⊏ P2 and P2 ⊏ P1 and P1 != P2, then P1 ≣ P2"""
    print("\n" + "=" * 60)
    print("TEST: scm-eqp2 (Mutual Property Subsumption to Equivalence)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    hasParent ⊑ᴿ hasAncestor
    hasAncestor ⊑ᴿ hasParent
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that hasParent ≣ hasAncestor is inferred
    equiv = reasoner.query(type="equivalent_property", property1="hasParent", property2="hasAncestor")
    print(f"Property equivalence (hasParent ≣ hasAncestor): {len(equiv)}")
    if equiv:
        print(f"  Inferred by: {equiv[0].get('inferred_by')}")

    success = len(equiv) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_spo():
    """Test: scm-spo - Property subsumption transitivity
    If P1 ⊏ P2 and P2 ⊏ P3, then P1 ⊏ P3"""
    print("\n" + "=" * 60)
    print("TEST: scm-spo (Property Subsumption Transitivity)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    hasSon ⊑ᴿ hasChild
    hasChild ⊑ᴿ hasDescendant
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that hasSon ⊏ hasDescendant is inferred
    trans_sub = reasoner.query(type="sub_property", sub="hasSon", sup="hasDescendant")
    print(f"Transitive property subsumption (hasSon ⊏ hasDescendant): {len(trans_sub)}")
    if trans_sub:
        print(f"  Inferred by: {trans_sub[0].get('inferred_by')}")

    success = len(trans_sub) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_combined():
    """Test: Combined schema reasoning
    Multiple schema rules working together"""
    print("\n" + "=" * 60)
    print("TEST: Combined Schema Reasoning")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ≡ᑦ Pupil
    Pupil ⊑ᑦ Person
    Person ⊑ᑦ Animal
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check combined reasoning:
    # 1. Student ≡ Pupil should give Student ⊑ Pupil (scm-eqc1)
    # 2. Student ⊑ Pupil and Pupil ⊑ Person should give Student ⊑ Person (scm-sco)
    # 3. Student ⊑ Person and Person ⊑ Animal should give Student ⊑ Animal (scm-sco)

    student_pupil = reasoner.query(type="subsumption", sub="Student", sup="Pupil")
    student_person = reasoner.query(type="subsumption", sub="Student", sup="Person")
    student_animal = reasoner.query(type="subsumption", sub="Student", sup="Animal")

    print(f"Student ⊑ Pupil (from equivalence): {len(student_pupil) > 0}")
    print(f"Student ⊑ Person (transitivity): {len(student_person) > 0}")
    print(f"Student ⊑ Animal (long chain): {len(student_animal) > 0}")

    success = len(student_pupil) > 0 and len(student_person) > 0 and len(student_animal) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "scm-sco": test_scm_sco(),
        "scm-eqc1": test_scm_eqc1(),
        "scm-eqc2": test_scm_eqc2(),
        "scm-eqc Roundtrip": test_scm_eqc_roundtrip(),
        "scm-eqp1": test_scm_eqp1(),
        "scm-eqp2": test_scm_eqp2(),
        "scm-spo": test_scm_spo(),
        "Combined Schema": test_scm_combined()
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
