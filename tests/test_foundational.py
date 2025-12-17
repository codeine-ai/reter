"""
Test foundational OWL facts: owl:Thing and owl:Nothing
These are automatically added to every ontology
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_foundational_facts():
    """Test that owl:Thing and owl:Nothing are always declared"""
    print("=" * 60)
    print("TEST: Foundational Facts (owl:Thing and owl:Nothing)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person ⊑ᑦ Animal
    Student ⊑ᑦ Person
    """
    reasoner.load_ontology(ontology)

    # Check that owl:Thing and owl:Nothing are declared
    decls = reasoner.query(type='concept_declaration')
    concepts = [d.get('concept') for d in decls]

    print(f"\nConcept declarations: {len(decls)}")
    for concept in sorted(concepts):
        print(f"  {concept}")

    has_thing = 'owl:Thing' in concepts
    has_nothing = 'owl:Nothing' in concepts
    has_user_concepts = 'Person' in concepts and 'Animal' in concepts and 'Student' in concepts

    print(f"\n✓ owl:Thing declared: {has_thing}")
    print(f"✓ owl:Nothing declared: {has_nothing}")
    print(f"✓ User concepts declared: {has_user_concepts}")

    success = has_thing and has_nothing and has_user_concepts
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_thing_subsumptions():
    """Test that all concepts are subsumed by owl:Thing"""
    print("\n" + "=" * 60)
    print("TEST: All Concepts Subsumed by owl:Thing")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person ⊑ᑦ Animal
    Student ⊑ᑦ Person
    Cat ⊑ᑦ Animal
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Find all subsumptions to owl:Thing
    thing_subs = reasoner.query(type='subsumption', sup='owl:Thing')
    print(f"\nSubsumptions to owl:Thing: {len(thing_subs)}")

    concepts_under_thing = set()
    for sub in thing_subs:
        sub_concept = sub.get('sub')
        print(f"  {sub_concept} ⊑ owl:Thing")
        concepts_under_thing.add(sub_concept)

    # Check that all user concepts are subsumed by Thing
    expected = {'Person', 'Animal', 'Student', 'Cat', 'owl:Thing', 'owl:Nothing'}
    success = expected.issubset(concepts_under_thing)

    print(f"\n✓ Expected concepts: {expected}")
    print(f"✓ Found concepts: {concepts_under_thing}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_nothing_subsumptions():
    """Test that owl:Nothing is subsumed by all concepts"""
    print("\n" + "=" * 60)
    print("TEST: owl:Nothing Subsumed by All Concepts")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person ⊑ᑦ Animal
    Student ⊑ᑦ Person
    Cat ⊑ᑦ Animal
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Find all subsumptions from owl:Nothing
    nothing_subs = reasoner.query(type='subsumption', sub='owl:Nothing')
    print(f"\nSubsumptions from owl:Nothing: {len(nothing_subs)}")

    concepts_above_nothing = set()
    for sub in nothing_subs:
        sup_concept = sub.get('sup')
        print(f"  owl:Nothing ⊑ {sup_concept}")
        concepts_above_nothing.add(sup_concept)

    # Check that all user concepts subsume Nothing
    expected = {'Person', 'Animal', 'Student', 'Cat', 'owl:Thing', 'owl:Nothing'}
    success = expected.issubset(concepts_above_nothing)

    print(f"\n✓ Expected concepts: {expected}")
    print(f"✓ Found concepts: {concepts_above_nothing}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_reflexivity():
    """Test that owl:Thing and owl:Nothing are reflexive"""
    print("\n" + "=" * 60)
    print("TEST: Reflexivity of owl:Thing and owl:Nothing")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person ⊑ᑦ Animal
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check reflexive subsumptions
    thing_refl = reasoner.query(type='subsumption', sub='owl:Thing', sup='owl:Thing')
    nothing_refl = reasoner.query(type='subsumption', sub='owl:Nothing', sup='owl:Nothing')

    print(f"\nowl:Thing ⊑ owl:Thing: {len(thing_refl) > 0}")
    print(f"owl:Nothing ⊑ owl:Nothing: {len(nothing_refl) > 0}")

    # Check reflexive equivalences
    thing_equiv = reasoner.query(type='equivalence', concept1='owl:Thing', concept2='owl:Thing')
    nothing_equiv = reasoner.query(type='equivalence', concept1='owl:Nothing', concept2='owl:Nothing')

    print(f"\nowl:Thing ≡ owl:Thing: {len(thing_equiv) > 0}")
    print(f"owl:Nothing ≡ owl:Nothing: {len(nothing_equiv) > 0}")

    success = (len(thing_refl) > 0 and len(nothing_refl) > 0 and
               len(thing_equiv) > 0 and len(nothing_equiv) > 0)

    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "Foundational Facts": test_foundational_facts(),
        "Thing Subsumptions": test_thing_subsumptions(),
        "Nothing Subsumptions": test_nothing_subsumptions(),
        "Reflexivity": test_reflexivity()
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
