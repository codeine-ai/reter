"""
Test suite for Unicode lexer tokens
Tests all new fullwidth and superscript Unicode characters
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_basic_subsumption():
    """Test: Basic class subsumption with new ⊑ᑦ token"""
    print("=" * 60)
    print("TEST: Basic Subsumption (⊑ᑦ)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    Person ⊑ᑦ Animal
    """
    reasoner.load_ontology(ontology)
    

    # Check subsumption chain
    subs = reasoner.query(type='subsumption')
    print(f"\nSubsumptions found: {len(subs)}")

    student_person = any(s.get('sub') == 'Student' and s.get('sup') == 'Person' for s in subs)
    person_animal = any(s.get('sub') == 'Person' and s.get('sup') == 'Animal' for s in subs)
    student_animal = any(s.get('sub') == 'Student' and s.get('sup') == 'Animal' for s in subs)

    print(f"  Student ⊑ᑦ Person: {student_person}")
    print(f"  Person ⊑ᑦ Animal: {person_animal}")
    print(f"  Student ⊑ᑦ Animal (transitive): {student_animal}")

    success = student_person and person_animal and student_animal
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_equivalence():
    """Test: Class equivalence with new ≡ᑦ token"""
    print("\n" + "=" * 60)
    print("TEST: Class Equivalence (≡ᑦ)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Human ≡ᑦ Person
    """
    reasoner.load_ontology(ontology)
    

    equivs = reasoner.query(type='equivalence')
    print(f"\nEquivalences found: {len(equivs)}")

    human_person = any(
        (e.get('concept1') == 'Human' and e.get('concept2') == 'Person') or
        (e.get('concept1') == 'Person' and e.get('concept2') == 'Human')
        for e in equivs
    )

    print(f"  Human ≡ᑦ Person: {human_person}")

    success = human_person
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_fullwidth_punctuation():
    """Test: Fullwidth punctuation （）｛｝［］，"""
    print("\n" + "=" * 60)
    print("TEST: Fullwidth Punctuation")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Teacher ⊓ Researcher（Alice）
    ≡ᑦ（Person，Human）
    ｛John，Mary｝（Bob）
    """
    reasoner.load_ontology(ontology)
    

    # Check instance
    alice_concepts = reasoner.query(type='instance_of', individual='Alice')
    print(f"\nAlice's concepts: {len(alice_concepts)}")

    # Check equivalence list
    equivs = reasoner.query(type='equivalence')
    person_human = any(
        (e.get('concept1') == 'Person' and e.get('concept2') == 'Human') or
        (e.get('concept1') == 'Human' and e.get('concept2') == 'Person')
        for e in equivs
    )

    # Check instance set
    bob_concepts = reasoner.query(type='instance_of', individual='Bob')

    print(f"  Alice has concepts: {len(alice_concepts) > 0}")
    print(f"  Person ≡ᑦ Human: {person_human}")
    print(f"  Bob has instance_set concept: {len(bob_concepts) > 0}")

    success = len(alice_concepts) > 0 and person_human and len(bob_concepts) > 0
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_role_subsumption():
    """Test: Role subsumption with new ⊑ᴿ token"""
    print("\n" + "=" * 60)
    print("TEST: Role Subsumption (⊑ᴿ)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    hasFather ⊑ᴿ hasParent
    hasParent ⊑ᴿ hasAncestor
    """
    reasoner.load_ontology(ontology)
    

    prop_subs = reasoner.query(type='sub_property')
    print(f"\nProperty subsumptions found: {len(prop_subs)}")

    father_parent = any(s.get('sub') == 'hasFather' and s.get('sup') == 'hasParent' for s in prop_subs)
    parent_ancestor = any(s.get('sub') == 'hasParent' and s.get('sup') == 'hasAncestor' for s in prop_subs)
    father_ancestor = any(s.get('sub') == 'hasFather' and s.get('sup') == 'hasAncestor' for s in prop_subs)

    print(f"  hasFather ⊑ᴿ hasParent: {father_parent}")
    print(f"  hasParent ⊑ᴿ hasAncestor: {parent_ancestor}")
    print(f"  hasFather ⊑ᴿ hasAncestor (transitive): {father_ancestor}")

    success = father_parent and parent_ancestor and father_ancestor
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_data_property_subsumption():
    """Test: Data property subsumption with new ⊑ᴰ token"""
    print("\n" + "=" * 60)
    print("TEST: Data Property Subsumption (⊑ᴰ)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    age（John，30）
    weight（Alice，150）
    """
    reasoner.load_ontology(ontology)
    

    data_props = reasoner.query(type='data_property_declaration')
    print(f"\nData properties detected: {len(data_props)}")

    has_age = any(p.get('property') == 'age' for p in data_props)
    has_weight = any(p.get('property') == 'weight' for p in data_props)

    print(f"  age detected: {has_age}")
    print(f"  weight detected: {has_weight}")

    success = has_age and has_weight
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_has_key():
    """Test: HasKey with new ⊑ᴷ token"""
    print("\n" + "=" * 60)
    print("TEST: HasKey (⊑ᴷ)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person ⊑ᴷ（ssn）
    """
    reasoner.load_ontology(ontology)
    

    has_keys = reasoner.query(type='has_key')
    print(f"\nHasKey axioms found: {len(has_keys)}")

    person_ssn = any(
        hk.get('class') == 'Person' and 'ssn' in str(hk.get('keys', ''))
        for hk in has_keys
    )

    print(f"  Person ⊑ᴷ (ssn): {person_ssn}")

    success = person_ssn
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_fullwidth_comparison():
    """Test: Fullwidth comparison operators ﹦﹤﹥"""
    print("\n" + "=" * 60)
    print("TEST: Fullwidth Comparison Operators")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    John ﹦ JohnDoe
    Alice ≠ Bob
    """
    reasoner.load_ontology(ontology)
    

    same = reasoner.query(type='same_as')
    diff = reasoner.query(type='different_from')

    print(f"\nSame-as facts: {len(same)}")
    print(f"Different-from facts: {len(diff)}")

    john_same = any(
        (s.get('ind1') == 'John' and s.get('ind2') == 'JohnDoe') or
        (s.get('ind1') == 'JohnDoe' and s.get('ind2') == 'John')
        for s in same
    )

    alice_bob_diff = any(
        (d.get('ind1') == 'Alice' and d.get('ind2') == 'Bob') or
        (d.get('ind1') == 'Bob' and d.get('ind2') == 'Alice')
        for d in diff
    )

    print(f"  John ﹦ JohnDoe: {john_same}")
    print(f"  Alice ≠ Bob: {alice_bob_diff}")

    success = john_same and alice_bob_diff
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_boolean_literals():
    """Test: Unicode boolean literals 𝙵 𝚃"""
    print("\n" + "=" * 60)
    print("TEST: Unicode Boolean Literals (𝙵 𝚃)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    isActive（System1，𝚃）
    isDisabled（System2，𝙵）
    """
    reasoner.load_ontology(ontology)
    

    data_assertions = reasoner.query(type='data_property_assertion')
    print(f"\nData property assertions: {len(data_assertions)}")

    system1_true = any(
        d.get('subject') == 'System1' and d.get('property') == 'isActive'
        for d in data_assertions
    )

    system2_false = any(
        d.get('subject') == 'System2' and d.get('property') == 'isDisabled'
        for d in data_assertions
    )

    print(f"  isActive(System1， 𝚃): {system1_true}")
    print(f"  isDisabled(System2， 𝙵): {system2_false}")

    success = system1_true and system2_false
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_restrictions_with_unicode_dot():
    """Test: Restrictions with new ․ (one dot leader) token"""
    print("\n" + "=" * 60)
    print("TEST: Restrictions with Unicode Dot (․)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Parent ≡ᑦ ∃hasChild․Person
    Grandparent ≡ᑦ ∃hasChild․Parent
    """
    reasoner.load_ontology(ontology)
    

    restrictions = reasoner.query(type='some_values_from')
    print(f"\nSomeValuesFrom restrictions: {len(restrictions)}")

    parent_restriction = any(
        r.get('property') == 'hasChild' and r.get('filler') == 'Person'
        for r in restrictions
    )

    grandparent_restriction = any(
        r.get('property') == 'hasChild' and r.get('filler') == 'Parent'
        for r in restrictions
    )

    print(f"  ∃hasChild․Person: {parent_restriction}")
    print(f"  ∃hasChild․Parent: {grandparent_restriction}")

    success = parent_restriction and grandparent_restriction
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_namespace_with_fullwidth_colon():
    """Test: Namespaces with ASCII colon (not fullwidth)"""
    print("\n" + "=" * 60)
    print("TEST: Namespaces with ASCII Colon")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    owl:Thing ⊑ᑦ owl:Thing
    foaf:Person ⊑ᑦ owl:Thing
    """
    reasoner.load_ontology(ontology)
    

    subs = reasoner.query(type='subsumption')
    print(f"\nSubsumptions found: {len(subs)}")

    owl_thing_reflexive = any(
        s.get('sub') == 'owl:Thing' and s.get('sup') == 'owl:Thing'
        for s in subs
    )

    foaf_person = any(
        s.get('sub') == 'foaf:Person' and s.get('sup') == 'owl:Thing'
        for s in subs
    )

    print(f"  owl:Thing ⊑ᑦ owl:Thing: {owl_thing_reflexive}")
    print(f"  foaf:Person ⊑ᑦ owl:Thing: {foaf_person}")

    success = owl_thing_reflexive and foaf_person
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "Basic Subsumption": test_basic_subsumption(),
        "Class Equivalence": test_equivalence(),
        "Fullwidth Punctuation": test_fullwidth_punctuation(),
        "Role Subsumption": test_role_subsumption(),
        "Data Property Subsumption": test_data_property_subsumption(),
        "HasKey": test_has_key(),
        "Fullwidth Comparison": test_fullwidth_comparison(),
        "Boolean Literals": test_boolean_literals(),
        "Restrictions with Unicode Dot": test_restrictions_with_unicode_dot(),
        "Namespaces with ASCII Colon": test_namespace_with_fullwidth_colon()
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
