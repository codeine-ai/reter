"""
Test for OWL 2 RL validation rules from more.owlrl.val.jena
All tests use DL syntax (LARK grammar) instead of add_fact()
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


def test_val_max1():
    """Test val-max1 rule (max cardinality 1 violation for literals)"""
    print("\n" + "=" * 60)
    print("TEST: Max Cardinality 1 Violation (val-max1)")
    print("=" * 60)

    reasoner = Reter()

    # Define RestrictedPerson as a class with subclass restriction  maxCard 1 on hasAge
    # Make John an instance and give him two different ages
    # Grammar: C ⊑ R where R is ≤1 hasAge
    ontology = """
    RestrictedPerson ⊑ᑦ ≤1 hasAge․⊤
    RestrictedPerson（John）
    hasAge（John， Age25）
    hasAge（John， Age30）
    """

    reasoner.load_ontology(ontology)
    

    # Check for inconsistency
    is_consistent, inconsistencies = reasoner.check_consistency()
    print(f"\nConsistent: {is_consistent}")
    print(f"Inconsistencies detected: {len(inconsistencies)}")
    for inc in inconsistencies:
        print(f"  - {inc}")

    assert not is_consistent, "Should detect inconsistency (max cardinality 1 violated)"
    assert len(inconsistencies) > 0, "Should detect inconsistency (max cardinality 1 violated)"

    # Check that val-max1 rule was triggered
    has_val_max1 = any('val-max1' in str(inc.get('inferred_by', '')) for inc in inconsistencies)
    assert has_val_max1, "Should have inconsistency from val-max1 rule"

    print("✓ Test passed: Max cardinality 1 violation detected (val-max1)")


def test_val_max1i():
    """Test val-max1i rule (max cardinality 1 violation with differentFrom)"""
    print("\n" + "=" * 60)
    print("TEST: Max Cardinality 1 Violation with DifferentFrom (val-max1i)")
    print("=" * 60)

    reasoner = Reter()

    # Define MonogamousPerson with max 1 hasSpouse
    # Make Alice married to both Bob and Charlie (who are different)
    # Grammar: different individuals using ≠
    ontology = """
    MonogamousPerson ⊑ᑦ ≤1 hasSpouse․⊤
    MonogamousPerson（Alice）
    hasSpouse（Alice， Bob）
    hasSpouse（Alice， Charlie）
    Bob ≠ Charlie
    """

    reasoner.load_ontology(ontology)
    

    # Check for inconsistency
    is_consistent, inconsistencies = reasoner.check_consistency()
    print(f"\nConsistent: {is_consistent}")
    print(f"Inconsistencies detected: {len(inconsistencies)}")
    for inc in inconsistencies:
        print(f"  - {inc}")

    assert not is_consistent, "Should detect inconsistency (max cardinality 1 violated with different individuals)"
    assert len(inconsistencies) > 0, "Should detect inconsistency"

    # Check that val-max1i rule was triggered
    has_val_max1i = any('val-max1i' in str(inc.get('inferred_by', '')) for inc in inconsistencies)
    assert has_val_max1i, "Should have inconsistency from val-max1i rule"

    print("✓ Test passed: Max cardinality 1 violation with differentFrom detected (val-max1i)")


def test_val_fp():
    """Test val-fp rule (functional property violation for literals)"""
    print("\n" + "=" * 60)
    print("TEST: Functional Property Violation (val-fp)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasBirthYear as functional property
    # Make David have two different birth years
    ontology = """
    Person（David）
    hasBirthYear（David， Year1990）
    hasBirthYear（David， Year1991）
    """

    reasoner.load_ontology(ontology)

    # Add functional property declaration
    reasoner.add_fact({
        "type": "functional",
        "property": "hasBirthYear"
    })

    

    # Check for inconsistency
    is_consistent, inconsistencies = reasoner.check_consistency()
    print(f"\nConsistent: {is_consistent}")
    print(f"Inconsistencies detected: {len(inconsistencies)}")
    for inc in inconsistencies:
        print(f"  - {inc}")

    assert not is_consistent, "Should detect inconsistency (functional property violated)"
    assert len(inconsistencies) > 0, "Should detect inconsistency"

    # Check that val-fp rule was triggered
    has_val_fp = any('val-fp' in str(inc.get('inferred_by', '')) for inc in inconsistencies)
    assert has_val_fp, "Should have inconsistency from val-fp rule"

    print("✓ Test passed: Functional property violation detected (val-fp)")


def test_val_fpi():
    """Test val-fpi rule (functional property violation with differentFrom)"""
    print("\n" + "=" * 60)
    print("TEST: Functional Property Violation with DifferentFrom (val-fpi)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasMother as functional property
    # Make Emma have two different mothers (who are explicitly different)
    ontology = """
    Person（Emma）
    Person（MotherA）
    Person（MotherB）
    hasMother（Emma， MotherA）
    hasMother（Emma， MotherB）
    MotherA ≠ MotherB
    """

    reasoner.load_ontology(ontology)

    # Add functional property declaration
    reasoner.add_fact({
        "type": "functional",
        "property": "hasMother"
    })

    

    # Check for inconsistency
    is_consistent, inconsistencies = reasoner.check_consistency()
    print(f"\nConsistent: {is_consistent}")
    print(f"Inconsistencies detected: {len(inconsistencies)}")
    for inc in inconsistencies:
        print(f"  - {inc}")

    assert not is_consistent, "Should detect inconsistency (functional property violated with different individuals)"
    assert len(inconsistencies) > 0, "Should detect inconsistency"

    # Check that val-fpi rule was triggered
    has_val_fpi = any('val-fpi' in str(inc.get('inferred_by', '')) for inc in inconsistencies)
    assert has_val_fpi, "Should have inconsistency from val-fpi rule"

    print("✓ Test passed: Functional property violation with differentFrom detected (val-fpi)")


def test_multiple_validation_rules():
    """Test multiple validation rules working together"""
    print("\n" + "=" * 60)
    print("TEST: Multiple Validation Rules Together")
    print("=" * 60)

    reasoner = Reter()

    # Complex scenario with multiple violations
    ontology = """
    RestrictedClass ⊑ᑦ ≤1 hasValue․⊤
    RestrictedClass（TestIndividual）
    hasValue（TestIndividual， Value1）
    hasValue（TestIndividual， Value2）
    hasValue（TestIndividual， Value3）
    """

    reasoner.load_ontology(ontology)
    

    # Check for inconsistencies
    is_consistent, inconsistencies = reasoner.check_consistency()
    print(f"\nConsistent: {is_consistent}")
    print(f"Inconsistencies detected: {len(inconsistencies)}")
    for inc in inconsistencies:
        print(f"  - {inc.get('message', str(inc))}")

    assert not is_consistent, "Should detect inconsistencies"
    assert len(inconsistencies) > 0, "Should detect multiple violations"

    print("✓ Test passed: Multiple validation rules working together")


def test_consistent_scenario():
    """Test that validation rules don't trigger on valid scenarios"""
    print("\n" + "=" * 60)
    print("TEST: Consistent Scenario (No False Positives)")
    print("=" * 60)

    reasoner = Reter()

    # Valid scenario: max cardinality 1 with only 1 value
    ontology = """
    RestrictedPerson ⊑ᑦ ≤1 hasAge․⊤
    RestrictedPerson（Frank）
    hasAge（Frank， Age40）
    """

    reasoner.load_ontology(ontology)

    # Add functional property that's not violated
    reasoner.add_fact({
        "type": "functional",
        "property": "hasNationalID"
    })

    reasoner.add_fact({
        "type": "role_assertion",
        "subject": "Frank",
        "role": "hasNationalID",
        "object": "ID123"
    })

    

    # Check for inconsistencies - should be none
    is_consistent, inconsistencies = reasoner.check_consistency()
    print(f"\nConsistent: {is_consistent}")
    print(f"Inconsistencies detected: {len(inconsistencies)}")

    assert is_consistent, "Should be consistent (no violations)"
    assert len(inconsistencies) == 0, "Should have no inconsistencies"

    print("✓ Test passed: No false positives in consistent scenario")


if __name__ == '__main__':
    test_val_max1()
    test_val_max1i()
    test_val_fp()
    test_val_fpi()
    test_multiple_validation_rules()
    test_consistent_scenario()

    print("\n" + "=" * 60)
    print("ALL MORE.OWLRL.VAL.JENA TESTS PASSED")
    print("=" * 60)
