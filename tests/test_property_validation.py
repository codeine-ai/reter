"""
Test property validation rules from props.owlrl.val.jena
All tests use LARK grammar syntax - NO add_fact() calls
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_irreflexive_violation():
    """Test: prp-irp - Irreflexive property violation
    If P is irreflexive and x P x, then violation"""
    print("=" * 60)
    print("TEST: Irreflexive Violation (prp-irp)")
    print("=" * 60)

    reasoner = Reter()
    # Define irreflexive property using: ∃R․↶ ⊑ ⊥
    ontology = """
    Person（Alice）
    differentFrom（Alice， Alice）
    ∃differentFrom․↶ ⊑ᑦ ⊥
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violation
    violations = reasoner.query(type="violation", violation_type="irreflexive")
    print(f"Violations detected: {len(violations)}")
    if violations:
        for v in violations:
            print(f"  Property: {v.get('property')}")
            print(f"  Individual: {v.get('individual')}")
            print(f"  Message: {v.get('message')}")

    success = len(violations) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_asymmetric_violation():
    """Test: prp-asyp - Asymmetric property violation
    If P is asymmetric and x P y and y P x (x != y), then violation"""
    print("\n" + "=" * 60)
    print("TEST: Asymmetric Violation (prp-asyp)")
    print("=" * 60)

    reasoner = Reter()
    # Define asymmetric property using: ¬ ≣ (R, R⁻)
    ontology = """
    Person（Alice）
    Person（Bob）
    hasChild（Alice， Bob）
    hasChild（Bob， Alice）
    ¬ ≡ᴿ （hasChild， hasChild⁻）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violation
    violations = reasoner.query(type="violation", violation_type="asymmetric")
    print(f"Violations detected: {len(violations)}")
    if violations:
        for v in violations:
            print(f"  Property: {v.get('property')}")
            print(f"  Subject: {v.get('subject')}, Object: {v.get('object')}")
            print(f"  Message: {v.get('message')}")

    success = len(violations) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_no_violation_when_valid():
    """Test: No violations when constraints are satisfied"""
    print("\n" + "=" * 60)
    print("TEST: No Violations (Valid Ontology)")
    print("=" * 60)

    reasoner = Reter()
    # Asymmetric property used correctly (no bidirectional)
    ontology = """
    Person（Alice）
    Person（Bob）
    hasChild（Alice， Bob）
    ¬ ≡ᴿ （hasChild， hasChild⁻）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for any violations
    violations = reasoner.query(type="violation")
    print(f"Violations detected: {len(violations)}")

    success = len(violations) == 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_irreflexive_no_violation():
    """Test: Irreflexive property used correctly"""
    print("\n" + "=" * 60)
    print("TEST: Irreflexive No Violation (Valid Usage)")
    print("=" * 60)

    reasoner = Reter()
    # Irreflexive property used on different individuals
    ontology = """
    Person（Alice）
    Person（Bob）
    differentFrom（Alice， Bob）
    ∃differentFrom․↶ ⊑ᑦ ⊥
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for violations
    violations = reasoner.query(type="violation", violation_type="irreflexive")
    print(f"Violations detected: {len(violations)}")

    success = len(violations) == 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_multiple_violations():
    """Test: Multiple violations in same ontology"""
    print("\n" + "=" * 60)
    print("TEST: Multiple Violations")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）

    hasChild（Alice， Bob）
    hasChild（Bob， Alice）
    ¬ ≡ᴿ （hasChild， hasChild⁻）

    differentFrom（Charlie， Charlie）
    ∃differentFrom․↶ ⊑ᑦ ⊥
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for all violations
    violations = reasoner.query(type="violation")
    asymmetric_violations = reasoner.query(type="violation", violation_type="asymmetric")
    irreflexive_violations = reasoner.query(type="violation", violation_type="irreflexive")

    print(f"Total violations: {len(violations)}")
    print(f"  Asymmetric violations: {len(asymmetric_violations)}")
    print(f"  Irreflexive violations: {len(irreflexive_violations)}")

    success = len(asymmetric_violations) > 0 and len(irreflexive_violations) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "Irreflexive Violation": test_irreflexive_violation(),
        "Asymmetric Violation": test_asymmetric_violation(),
        "No Violation (Valid)": test_no_violation_when_valid(),
        "Irreflexive Valid": test_irreflexive_no_violation(),
        "Multiple Violations": test_multiple_violations()
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
