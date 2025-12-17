"""
Test same-as validation rules from same-as.owlrl.val.jena
All tests use LARK grammar syntax - NO add_fact() calls
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_eq_diff1_violation():
    """Test: eq-diff1 - Same and different conflict
    If X sameAs Y and X differentFrom Y, then violation"""
    print("=" * 60)
    print("TEST: eq-diff1 (Same and Different Conflict)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Alice ﹦ Bob
    Alice ≠ Bob
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violation
    violations = reasoner.query(type="violation", violation_type="same_and_different")
    print(f"Violations detected: {len(violations)}")
    if violations:
        for v in violations:
            print(f"  Individuals: {v.get('ind1')}, {v.get('ind2')}")
            print(f"  Message: {v.get('message')}")
            print(f"  Detected by: {v.get('detected_by')}")

    success = len(violations) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_eq_diff1_no_violation():
    """Test: No violation when individuals are only same or only different"""
    print("\n" + "=" * 60)
    print("TEST: eq-diff1 No Violation (Valid)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    Alice ﹦ Bob
    Alice ≠ Charlie
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violations
    violations = reasoner.query(type="violation", violation_type="same_and_different")
    print(f"Violations detected: {len(violations)}")

    success = len(violations) == 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_eq_diff1_transitive():
    """Test: eq-diff1 with transitivity
    If A = B and B = C and A ≠ C, then violation"""
    print("\n" + "=" * 60)
    print("TEST: eq-diff1 with Transitivity")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    Alice ﹦ Bob
    Bob ﹦ Charlie
    Alice ≠ Charlie
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violation (transitivity should infer Alice = Charlie)
    violations = reasoner.query(type="violation", violation_type="same_and_different")
    print(f"Violations detected: {len(violations)}")
    if violations:
        for v in violations:
            print(f"  Individuals: {v.get('ind1')}, {v.get('ind2')}")
            print(f"  Message: {v.get('message')}")

    success = len(violations) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_validationIndiv3_violation():
    """Test: validationIndiv3 - Individual member of Nothing
    If individual is member of owl:Nothing, then violation"""
    print("\n" + "=" * 60)
    print("TEST: validationIndiv3 (Nothing Member)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    owl:Nothing（Alice）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violation
    violations = reasoner.query(type="violation", violation_type="nothing_member")
    print(f"Violations detected: {len(violations)}")
    if violations:
        for v in violations:
            print(f"  Individual: {v.get('individual')}")
            print(f"  Message: {v.get('message')}")
            print(f"  Detected by: {v.get('detected_by')}")

    success = len(violations) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_validationIndiv3_inferred():
    """Test: validationIndiv3 with inferred Nothing membership
    If individual inferred to be member of Nothing, then violation"""
    print("\n" + "=" * 60)
    print("TEST: validationIndiv3 (Inferred Nothing)")
    print("=" * 60)

    reasoner = Reter()
    # Use bottom concept: C ⊑ ⊥ and C(Alice) implies Alice : ⊥
    ontology = """
    Person（Alice）
    EmptyClass ⊑ᑦ ⊥
    EmptyClass（Alice）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violation (should be inferred via subsumption)
    violations = reasoner.query(type="violation", violation_type="nothing_member")
    print(f"Violations detected: {len(violations)}")
    if violations:
        for v in violations:
            print(f"  Individual: {v.get('individual')}")
            print(f"  Message: {v.get('message')}")

    success = len(violations) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_validationIndiv3_no_violation():
    """Test: No violation when individual is not member of Nothing"""
    print("\n" + "=" * 60)
    print("TEST: validationIndiv3 No Violation (Valid)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Student（Alice）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violations
    violations = reasoner.query(type="violation", violation_type="nothing_member")
    print(f"Violations detected: {len(violations)}")

    success = len(violations) == 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_combined_violations():
    """Test: Multiple validation violations in same ontology"""
    print("\n" + "=" * 60)
    print("TEST: Combined Violations")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Alice ﹦ Bob
    Alice ≠ Bob
    owl:Nothing（Bob）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for all violations
    all_violations = reasoner.query(type="violation")
    same_diff_violations = reasoner.query(type="violation", violation_type="same_and_different")
    nothing_violations = reasoner.query(type="violation", violation_type="nothing_member")

    print(f"Total violations: {len(all_violations)}")
    print(f"  Same-and-different violations: {len(same_diff_violations)}")
    print(f"  Nothing member violations: {len(nothing_violations)}")

    success = len(same_diff_violations) > 0 and len(nothing_violations) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "eq-diff1 Violation": test_eq_diff1_violation(),
        "eq-diff1 No Violation": test_eq_diff1_no_violation(),
        "eq-diff1 Transitive": test_eq_diff1_transitive(),
        "validationIndiv3 Violation": test_validationIndiv3_violation(),
        "validationIndiv3 Inferred": test_validationIndiv3_inferred(),
        "validationIndiv3 No Violation": test_validationIndiv3_no_violation(),
        "Combined Violations": test_combined_violations()
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
