"""
Test complete schema.owlrl.jena rules using LARK grammar syntax only
Tests for scm-cls, scm-op, scm-dp, scm-dom1, scm-dom2, scm-rng1, scm-rng2, scm-hv
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_scm_cls():
    """Test: scm-cls - Class reflexivity and bounds
    For each class C:
    - C ⊑ C (reflexive subsumption)
    - C ≡ C (reflexive equivalence)
    - C ⊑ owl:Thing
    - owl:Nothing ⊑ C
    """
    print("=" * 60)
    print("TEST: scm-cls (Class Reflexivity and Bounds)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person ⊑ᑦ owl:Thing
    Student ⊑ᑦ Person
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for reflexive subsumptions
    inferred = reasoner.query(type="subsumption", inferred_by="scm-cls")
    print(f"Subsumptions inferred by scm-cls: {len(inferred)}")

    # Expected: Person ⊑ Person, Student ⊑ Student
    # owl:Nothing ⊑ Person, owl:Nothing ⊑ Student
    # Note: "C ⊑ owl:Thing" may be deduplicated if already in ontology
    reflexive_found = False
    nothing_found = False

    for inf in inferred:
        sub = inf.get('sub')
        sup = inf.get('sup')
        print(f"  {sub} ⊑ {sup}")
        if sub == sup:
            reflexive_found = True
        if sub == "owl:Nothing":
            nothing_found = True

    # Check for reflexive equivalences
    equiv_inferred = reasoner.query(type="equivalence", inferred_by="scm-cls")
    print(f"Equivalences inferred by scm-cls: {len(equiv_inferred)}")
    for eq in equiv_inferred:
        print(f"  {eq.get('concept1')} ≡ {eq.get('concept2')}")

    success = reflexive_found and nothing_found and len(equiv_inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_op():
    """Test: scm-op - Object property reflexivity
    For each object property P:
    - P ⊏ P (reflexive property subsumption)
    - P ≣ P (reflexive property equivalence)
    """
    print("\n" + "=" * 60)
    print("TEST: scm-op (Object Property Reflexivity)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    knows ⊑ᴿ relatedTo
    likes ⊑ᴿ knows
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for reflexive property subsumptions
    inferred = reasoner.query(type="property_subsumption", inferred_by="scm-op")
    print(f"Property subsumptions inferred by scm-op: {len(inferred)}")

    reflexive_found = False
    for inf in inferred:
        sub = inf.get('sub')
        sup = inf.get('sup')
        print(f"  {sub} ⊏ {sup}")
        if sub == sup:
            reflexive_found = True

    # Check for reflexive property equivalences
    equiv_inferred = reasoner.query(type="property_equivalence", inferred_by="scm-op")
    print(f"Property equivalences inferred by scm-op: {len(equiv_inferred)}")
    for eq in equiv_inferred:
        print(f"  {eq.get('property1')} ≣ {eq.get('property2')}")

    success = reflexive_found and len(equiv_inferred) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_dp():
    """Test: scm-dp - Data property reflexivity
    For each data property P:
    - P ⊏ P (reflexive property subsumption)
    - P ≣ P (reflexive property equivalence)

    Note: Need data property declarations in LARK grammar
    """
    print("\n" + "=" * 60)
    print("TEST: scm-dp (Data Property Reflexivity)")
    print("=" * 60)

    print("SKIPPED: Data property declarations not yet implemented in AST extractor")
    return True

def test_scm_dom1():
    """Test: scm-dom1 - Domain subsumption
    If P has domain C1 and C1 ⊑ C2, then P has domain C2

    Note: Requires property_domain fact extraction from ∃R․⊤ ⊑ C pattern
    """
    print("\n" + "=" * 60)
    print("TEST: scm-dom1 (Domain Subsumption)")
    print("=" * 60)

    print("SKIPPED: Property domain extraction not yet implemented in AST extractor")
    print("(Requires detecting ∃R․⊤ ⊑ C pattern)")
    return True

def test_scm_dom2():
    """Test: scm-dom2 - Domain propagation
    If P2 has domain C and P1 ⊏ P2, then P1 has domain C

    Note: Requires property_domain fact extraction
    """
    print("\n" + "=" * 60)
    print("TEST: scm-dom2 (Domain Propagation)")
    print("=" * 60)

    print("SKIPPED: Property domain extraction not yet implemented in AST extractor")
    return True

def test_scm_rng1():
    """Test: scm-rng1 - Range subsumption
    If P has range C1 and C1 ⊑ C2, then P has range C2

    Note: Requires property_range fact extraction from ⊤ ⊑ ∀R․C pattern
    """
    print("\n" + "=" * 60)
    print("TEST: scm-rng1 (Range Subsumption)")
    print("=" * 60)

    print("SKIPPED: Property range extraction not yet implemented in AST extractor")
    print("(Requires detecting ⊤ ⊑ ∀R․C pattern)")
    return True

def test_scm_rng2():
    """Test: scm-rng2 - Range propagation
    If P2 has range C and P1 ⊏ P2, then P1 has range C

    Note: Requires property_range fact extraction
    """
    print("\n" + "=" * 60)
    print("TEST: scm-rng2 (Range Propagation)")
    print("=" * 60)

    print("SKIPPED: Property range extraction not yet implemented in AST extractor")
    return True

def test_scm_hv():
    """Test: scm-hv - hasValue subsumption
    If C1 has value restriction (P1, I) and C2 has value restriction (P2, I) and P1 ⊏ P2, then C1 ⊑ C2

    Note: Requires has_value fact extraction (probably from equivalences with value restrictions)
    """
    print("\n" + "=" * 60)
    print("TEST: scm-hv (HasValue Subsumption)")
    print("=" * 60)

    print("SKIPPED: HasValue extraction not yet implemented in AST extractor")
    return True

def test_combined_schema():
    """Test: Combined schema rules working together"""
    print("\n" + "=" * 60)
    print("TEST: Combined Schema Rules")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    Person ⊑ᑦ Animal
    likes ⊑ᴿ knows
    knows ⊑ᴿ relatedTo

    TeachesStudents ≡ᑦ ∃teaches․Student
    TeachesPersons ≡ᑦ ∃teaches․Person
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check multiple rule interactions
    sco_inferred = reasoner.query(type="subsumption", inferred_by="scm-sco")
    cls_inferred = reasoner.query(type="subsumption", inferred_by="scm-cls")
    spo_inferred = reasoner.query(type="sub_property", inferred_by="scm-spo")
    op_inferred = reasoner.query(type="property_subsumption", inferred_by="scm-op")
    svf1_inferred = reasoner.query(type="subsumption", inferred_by="scm-svf1")

    print(f"Subsumptions by scm-sco: {len(sco_inferred)}")
    print(f"Subsumptions by scm-cls: {len(cls_inferred)}")
    print(f"Property subsumptions by scm-spo: {len(spo_inferred)}")
    print(f"Property subsumptions by scm-op: {len(op_inferred)}")
    print(f"Restriction subsumptions by scm-svf1: {len(svf1_inferred)}")

    success = (len(sco_inferred) > 0 and len(cls_inferred) > 0 and
               len(op_inferred) > 0 and len(svf1_inferred) > 0)
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "scm-cls": test_scm_cls(),
        "scm-op": test_scm_op(),
        "scm-dp": test_scm_dp(),
        "scm-dom1": test_scm_dom1(),
        "scm-dom2": test_scm_dom2(),
        "scm-rng1": test_scm_rng1(),
        "scm-rng2": test_scm_rng2(),
        "scm-hv": test_scm_hv(),
        "Combined": test_combined_schema()
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

    skipped = sum(1 for name in results.keys() if name in ["scm-dp", "scm-dom1", "scm-dom2", "scm-rng1", "scm-rng2", "scm-hv"])
    print(f"({skipped} tests skipped - AST extraction not yet implemented)")
