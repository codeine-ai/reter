"""
Test edge-case validation rules
Tests for cls-int2 (intersection decomposition) and cls-nothing2 (empty intersection)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_cls_int2_decomposition():
    """Test: cls-int2 - Intersection decomposition
    If X : (A ⊓ B), then X : A and X : B
    """
    print("=" * 60)
    print("TEST: cls-int2 (Intersection Decomposition)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Teacher ⊓ Researcher（Alice）
    Student ⊓ Employee（Bob）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice is instance of both Teacher and Researcher
    alice_concepts = reasoner.query(type='instance_of', individual='Alice')
    print(f"\nAlice's concepts: {len(alice_concepts)}")
    alice_concept_names = set()
    cls_int2_found = False

    for concept in alice_concepts:
        name = concept.get('concept')
        inferred_by = concept.get('inferred_by', '')
        print(f"  Alice : {name} (by {inferred_by})")
        alice_concept_names.add(name)
        if inferred_by == 'cls-int2':
            cls_int2_found = True

    # Check that Bob is instance of both Student and Employee
    bob_concepts = reasoner.query(type='instance_of', individual='Bob')
    print(f"\nBob's concepts: {len(bob_concepts)}")
    bob_concept_names = set()

    for concept in bob_concepts:
        name = concept.get('concept')
        inferred_by = concept.get('inferred_by', '')
        print(f"  Bob : {name} (by {inferred_by})")
        bob_concept_names.add(name)
        if inferred_by == 'cls-int2':
            cls_int2_found = True

    success = (
        'Teacher' in alice_concept_names and
        'Researcher' in alice_concept_names and
        'Student' in bob_concept_names and
        'Employee' in bob_concept_names and
        cls_int2_found
    )

    print(f"\n✓ Alice is Teacher: {'Teacher' in alice_concept_names}")
    print(f"✓ Alice is Researcher: {'Researcher' in alice_concept_names}")
    print(f"✓ Bob is Student: {'Student' in bob_concept_names}")
    print(f"✓ Bob is Employee: {'Employee' in bob_concept_names}")
    print(f"✓ cls-int2 fired: {cls_int2_found}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_cls_int2_with_subsumption():
    """Test: cls-int2 works with subsumption reasoning"""
    print("\n" + "=" * 60)
    print("TEST: cls-int2 with Subsumption")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Teacher ⊑ᑦ Person
    Researcher ⊑ᑦ Person
    Teacher ⊓ Researcher（Alice）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Alice should be: Teacher ⊓ Researcher, Teacher, Researcher, Person, owl:Thing
    alice_concepts = reasoner.query(type='instance_of', individual='Alice')
    print(f"\nAlice's concepts: {len(alice_concepts)}")
    alice_concept_names = set()

    for concept in alice_concepts:
        name = concept.get('concept')
        inferred_by = concept.get('inferred_by', '')
        if not name.startswith('_:'):  # Skip blank nodes
            print(f"  Alice : {name} (by {inferred_by})")
            alice_concept_names.add(name)

    success = (
        'Teacher' in alice_concept_names and
        'Researcher' in alice_concept_names and
        'Person' in alice_concept_names and
        'owl:Thing' in alice_concept_names
    )

    print(f"\n✓ Alice is Teacher: {'Teacher' in alice_concept_names}")
    print(f"✓ Alice is Researcher: {'Researcher' in alice_concept_names}")
    print(f"✓ Alice is Person: {'Person' in alice_concept_names}")
    print(f"✓ Alice is owl:Thing: {'owl:Thing' in alice_concept_names}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_cls_nothing2_contradiction():
    """Test: cls-nothing2 - Detects contradictory intersections
    Person ⊓ ¬Person should be equivalent to owl:Nothing
    """
    print("\n" + "=" * 60)
    print("TEST: cls-nothing2 (Empty Intersection - Complement)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    BadConcept ≡ᑦ Person ⊓ ¬Person
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check if BadConcept is inferred to be equivalent to owl:Nothing
    equivalences = reasoner.query(type='equivalence')
    print(f"\nEquivalences found: {len(equivalences)}")

    cls_nothing2_found = False
    badconcept_is_nothing = False

    for equiv in equivalences:
        c1 = equiv.get('concept1')
        c2 = equiv.get('concept2')
        inferred_by = equiv.get('inferred_by', '')

        if inferred_by == 'cls-nothing2':
            cls_nothing2_found = True
            # Check if one side is the intersection and other is owl:Nothing
            if (c1.startswith('_:') and c2 == 'owl:Nothing') or (c2.startswith('_:') and c1 == 'owl:Nothing'):
                badconcept_is_nothing = True
                print(f"  {c1} ≡ {c2} (by {inferred_by})")

    # Also check subsumptions
    subsumptions = reasoner.query(type='subsumption')
    print(f"\nSubsumptions found: {len(subsumptions)}")

    for sub in subsumptions:
        s = sub.get('sub')
        sup = sub.get('sup')
        inferred_by = sub.get('inferred_by', '')

        if inferred_by == 'cls-nothing2':
            print(f"  {s} ⊑ {sup} (by {inferred_by})")

    success = cls_nothing2_found and badconcept_is_nothing

    print(f"\n✓ cls-nothing2 fired: {cls_nothing2_found}")
    print(f"✓ Contradictory intersection detected: {badconcept_is_nothing}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_cls_nothing2_with_nothing():
    """Test: cls-nothing2 - Intersection with owl:Nothing
    Any intersection with owl:Nothing should be equivalent to owl:Nothing
    """
    print("\n" + "=" * 60)
    print("TEST: cls-nothing2 (Intersection with Nothing)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    EmptyConcept ≡ᑦ Person ⊓ owl:Nothing
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check if the intersection is inferred to be equivalent to owl:Nothing
    equivalences = reasoner.query(type='equivalence')
    print(f"\nEquivalences found: {len(equivalences)}")

    cls_nothing2_found = False

    for equiv in equivalences:
        c1 = equiv.get('concept1')
        c2 = equiv.get('concept2')
        inferred_by = equiv.get('inferred_by', '')

        if inferred_by == 'cls-nothing2':
            cls_nothing2_found = True
            print(f"  {c1} ≡ {c2} (by {inferred_by})")

    success = cls_nothing2_found

    print(f"\n✓ cls-nothing2 fired: {cls_nothing2_found}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_cls_int2_and_nothing2_combined():
    """Test: Combined cls-int2 and cls-nothing2 reasoning"""
    print("\n" + "=" * 60)
    print("TEST: Combined cls-int2 and cls-nothing2")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    ValidPerson ≡ᑦ Teacher ⊓ Researcher
    InvalidPerson ≡ᑦ Person ⊓ ¬Person

    ValidPerson（Alice）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check Alice's concepts (should have Teacher and Researcher from cls-int2)
    alice_concepts = reasoner.query(type='instance_of', individual='Alice')
    print(f"\nAlice's concepts: {len(alice_concepts)}")
    alice_has_teacher = False
    alice_has_researcher = False

    for concept in alice_concepts:
        name = concept.get('concept')
        if name == 'Teacher':
            alice_has_teacher = True
        if name == 'Researcher':
            alice_has_researcher = True
        if not name.startswith('_:'):
            print(f"  Alice : {name}")

    # Check for contradictory concept detection
    equivalences = reasoner.query(type='equivalence')
    print(f"\nEquivalences with cls-nothing2:")
    nothing2_found = False

    for equiv in equivalences:
        if equiv.get('inferred_by') == 'cls-nothing2':
            nothing2_found = True
            print(f"  {equiv.get('concept1')} ≡ {equiv.get('concept2')}")

    success = alice_has_teacher and alice_has_researcher and nothing2_found

    print(f"\n✓ Alice decomposed to Teacher: {alice_has_teacher}")
    print(f"✓ Alice decomposed to Researcher: {alice_has_researcher}")
    print(f"✓ Contradiction detected: {nothing2_found}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "cls-int2 Decomposition": test_cls_int2_decomposition(),
        "cls-int2 with Subsumption": test_cls_int2_with_subsumption(),
        "cls-nothing2 Complement": test_cls_nothing2_contradiction(),
        "cls-nothing2 with Nothing": test_cls_nothing2_with_nothing(),
        "Combined cls-int2 and cls-nothing2": test_cls_int2_and_nothing2_combined()
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
