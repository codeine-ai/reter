"""
Test same-as equality rules from same-as.owlrl.jena
All tests use LARK grammar syntax - NO add_fact() calls
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_eq_all():
    """Test: eq-all - NamedIndividual gets sameAs itself and Thing membership"""
    print("=" * 60)
    print("TEST: eq-all (Reflexivity + Thing)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    owl:NamedIndividual（Alice）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice is sameAs herself
    same_as_facts = reasoner.query(type="same_as", ind1="Alice", ind2="Alice")
    print(f"Same-as facts (Alice = Alice): {len(same_as_facts)}")

    # Check that Alice is a Thing
    thing_facts = reasoner.query(type="instance_of", individual="Alice", concept="owl:Thing")
    print(f"Thing membership (Alice : Thing): {len(thing_facts)}")

    success = len(same_as_facts) > 0 and len(thing_facts) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_eq_sym():
    """Test: eq-sym - Symmetry of sameAs"""
    print("\n" + "=" * 60)
    print("TEST: eq-sym (Symmetry)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Alice ﹦ Bob
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Bob = Alice is inferred
    reverse_same = reasoner.query(type="same_as", ind1="Bob", ind2="Alice")
    print(f"Reverse same-as (Bob = Alice): {len(reverse_same)}")
    if reverse_same:
        print(f"  Inferred by: {reverse_same[0].get('inferred_by')}")

    success = len(reverse_same) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_eq_trans():
    """Test: eq-trans - Transitivity of sameAs"""
    print("\n" + "=" * 60)
    print("TEST: eq-trans (Transitivity)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    Alice ﹦ Bob
    Bob ﹦ Charlie
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice = Charlie is inferred
    trans_same = reasoner.query(type="same_as", ind1="Alice", ind2="Charlie")
    print(f"Transitive same-as (Alice = Charlie): {len(trans_same)}")
    if trans_same:
        print(f"  Inferred by: {trans_same[0].get('inferred_by')}")

    success = len(trans_same) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_eq_rep_s():
    """Test: eq-rep-s - Subject replacement"""
    print("\n" + "=" * 60)
    print("TEST: eq-rep-s (Subject Replacement)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（AliceSmith）
    Person（Bob）
    Alice ﹦ AliceSmith
    knows（Alice， Bob）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that knows(AliceSmith, Bob) is inferred
    replaced = reasoner.query(type="role_assertion", subject="AliceSmith", role="knows", object="Bob")
    print(f"Subject replaced (AliceSmith knows Bob): {len(replaced)}")
    if replaced:
        print(f"  Inferred by: {replaced[0].get('inferred_by')}")

    success = len(replaced) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_eq_rep_o():
    """Test: eq-rep-o - Object replacement"""
    print("\n" + "=" * 60)
    print("TEST: eq-rep-o (Object Replacement)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Robert）
    Bob ﹦ Robert
    knows（Alice， Bob）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that knows(Alice, Robert) is inferred
    replaced = reasoner.query(type="role_assertion", subject="Alice", role="knows", object="Robert")
    print(f"Object replaced (Alice knows Robert): {len(replaced)}")
    if replaced:
        print(f"  Inferred by: {replaced[0].get('inferred_by')}")

    success = len(replaced) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_eq_rep_p():
    """Test: eq-rep-p - Property replacement"""
    print("\n" + "=" * 60)
    print("TEST: eq-rep-p (Property Replacement)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    knows（Alice， Bob）
    acquaintedWith ﹦ knows
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that acquaintedWith(Alice, Bob) is inferred
    replaced = reasoner.query(type="role_assertion", subject="Alice", role="acquaintedWith", object="Bob")
    print(f"Property replaced (Alice acquaintedWith Bob): {len(replaced)}")
    if replaced:
        print(f"  Inferred by: {replaced[0].get('inferred_by')}")

    success = len(replaced) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_eq_rep_c():
    """Test: eq-rep-c - Class membership replacement"""
    print("\n" + "=" * 60)
    print("TEST: eq-rep-c (Class Membership Replacement)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（AliceSmith）
    Alice ﹦ AliceSmith
    Student（Alice）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Student(AliceSmith) is inferred
    replaced = reasoner.query(type="instance_of", individual="AliceSmith", concept="Student")
    print(f"Class membership replaced (AliceSmith : Student): {len(replaced)}")
    if replaced:
        print(f"  Inferred by: {replaced[0].get('inferred_by')}")

    success = len(replaced) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_same_instances_list():
    """Test: = {a, b, c} - all individuals are same"""
    print("\n" + "=" * 60)
    print("TEST: Same Instances List")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（AliceSmith）
    Person（AliceJ）
    ﹦ ｛Alice， AliceSmith， AliceJ｝
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that all pairwise same_as facts exist
    same_facts = reasoner.query(type="same_as")
    print(f"Total same-as facts: {len(same_facts)}")

    # Check specific pairs
    alice_alicesmith = reasoner.query(type="same_as", ind1="Alice", ind2="AliceSmith")
    alice_alicej = reasoner.query(type="same_as", ind1="Alice", ind2="AliceJ")
    alicesmith_alicej = reasoner.query(type="same_as", ind1="AliceSmith", ind2="AliceJ")

    print(f"  Alice = AliceSmith: {len(alice_alicesmith) > 0}")
    print(f"  Alice = AliceJ: {len(alice_alicej) > 0}")
    print(f"  AliceSmith = AliceJ: {len(alicesmith_alicej) > 0}")

    success = len(alice_alicesmith) > 0 and len(alice_alicej) > 0 and len(alicesmith_alicej) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_different_instances_list():
    """Test: ≠ {a, b, c} - all individuals are different"""
    print("\n" + "=" * 60)
    print("TEST: Different Instances List")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    ≠ ｛Alice， Bob， Charlie｝
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that all pairwise different_from facts exist
    diff_facts = reasoner.query(type="different_from")
    print(f"Total different-from facts: {len(diff_facts)}")

    # Check specific pairs
    alice_bob = reasoner.query(type="different_from", ind1="Alice", ind2="Bob")
    alice_charlie = reasoner.query(type="different_from", ind1="Alice", ind2="Charlie")
    bob_charlie = reasoner.query(type="different_from", ind1="Bob", ind2="Charlie")

    print(f"  Alice ≠ Bob: {len(alice_bob) > 0}")
    print(f"  Alice ≠ Charlie: {len(alice_charlie) > 0}")
    print(f"  Bob ≠ Charlie: {len(bob_charlie) > 0}")

    success = len(alice_bob) > 0 and len(alice_charlie) > 0 and len(bob_charlie) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "eq-all": test_eq_all(),
        "eq-sym": test_eq_sym(),
        "eq-trans": test_eq_trans(),
        "eq-rep-s": test_eq_rep_s(),
        "eq-rep-o": test_eq_rep_o(),
        "eq-rep-p": test_eq_rep_p(),
        "eq-rep-c": test_eq_rep_c(),
        "Same Instances List": test_same_instances_list(),
        "Different Instances List": test_different_instances_list()
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
