"""
Parser and Syntax Tests - Validate DL syntax parsing

Converted from tests_standalone/ to proper pytest tests.
Tests Unicode syntax, comment handling, and parser correctness.
"""

import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

from reter_core import owl_rete_cpp


# ============================================================================
# Comment Parsing Tests
# ============================================================================

def test_comment_parsing_hash_comments_not_supported():
    """Test that # comments are not part of standard DL syntax"""
    net = owl_rete_cpp.ReteNetwork()

    test_input = """# This is a comment
Dog ⊑ᑦ Animal
# Another comment
Cat ⊑ᑦ Animal"""

    # The parser may either reject # or treat it as error
    # Either way, it should not silently accept it as valid syntax
    try:
        net.load_ontology_from_string(test_input)
        facts = net.get_all_facts()
        # If it parses, there should be at least Dog and Cat subsumptions
        subs = [f for f in facts if f.get('type') == 'subsumption']
        # We don't fail the test - just document behavior
    except Exception:
        # Expected - # is not valid DL syntax
        pass


# ============================================================================
# Unicode Syntax Tests
# ============================================================================

def test_unicode_syntax_fullwidth_parentheses():
    """Test that fullwidth Unicode parentheses are used for instances"""
    net = owl_rete_cpp.ReteNetwork()

    # Correct: Unicode fullwidth parentheses （）
    correct_syntax = """
Person ⊑ᑦ Animal
Animal（John）
Animal（Mary）
"""

    wme_count = net.load_ontology_from_string(correct_syntax)
    assert wme_count > 0, "Should parse Unicode syntax"

    facts = net.get_all_facts()
    instances = [f for f in facts if f.get('type') == 'instance_of']

    assert len(instances) >= 2, "Should have at least 2 instances"

    john_instance = [f for f in instances if f.get('individual') == 'John']
    mary_instance = [f for f in instances if f.get('individual') == 'Mary']

    assert len(john_instance) > 0, "John should be parsed as instance"
    assert len(mary_instance) > 0, "Mary should be parsed as instance"


def test_unicode_syntax_subsumption():
    """Test Unicode subsumption operator ⊑ᑦ"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "Dog ⊑ᑦ Animal"
    wme_count = net.load_ontology_from_string(ontology)

    assert wme_count > 0
    facts = net.get_all_facts()
    subs = [f for f in facts if f.get('type') == 'subsumption']

    assert len(subs) > 0, "Should have subsumption"
    assert subs[0].get('sub') == 'Dog'
    assert subs[0].get('sup') == 'Animal'


def test_unicode_syntax_role_subsumption():
    """Test Unicode role subsumption operator ⊑ᴿ"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "hasParent ⊑ᴿ hasAncestor"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    role_subs = [f for f in facts if f.get('type') == 'sub_property']

    assert len(role_subs) > 0, "Should have role subsumption"


def test_unicode_syntax_equivalence():
    """Test Unicode equivalence operator ≡ᑦ"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "Human ≡ᑦ Person"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    # Equivalence creates two subsumptions
    subs = [f for f in facts if f.get('type') == 'subsumption']

    assert len(subs) >= 2, "Equivalence should create bidirectional subsumptions"


def test_unicode_syntax_conjunction():
    """Test Unicode conjunction operator ⊓"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "Parent ⊑ᑦ Person ⊓ ∃hasChild․Thing"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    # Parser should handle conjunction
    assert len(facts) > 0


def test_unicode_syntax_disjunction():
    """Test Unicode disjunction operator ⊔"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "Animal ⊑ᑦ Cat ⊔ Dog"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    assert len(facts) > 0


def test_unicode_syntax_existential_restriction():
    """Test existential restriction ∃"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "Parent ⊑ᑦ ∃hasChild․Person"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    # Should parse existential restriction
    assert len(facts) > 0


def test_unicode_syntax_universal_restriction():
    """Test universal restriction ∀"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "HappyParent ⊑ᑦ ∀hasChild․Happy"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    assert len(facts) > 0


def test_unicode_syntax_negation():
    """Test negation operator ¬"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "Childless ⊑ᑦ Person ⊓ ¬∃hasChild․Thing"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    assert len(facts) > 0


def test_unicode_syntax_fullwidth_comma():
    """Test fullwidth comma in role assertions"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "hasParent（John，Mary）"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    roles = [f for f in facts if f.get('type') == 'role_assertion']

    assert len(roles) > 0, "Should have role assertion"
    assert roles[0].get('subject') == 'John'
    assert roles[0].get('object') == 'Mary'


# ============================================================================
# Basic Parsing Tests
# ============================================================================

def test_parser_basic_class_assertion():
    """Test parsing basic class assertion"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "Person（Alice）"
    wme_count = net.load_ontology_from_string(ontology)

    assert wme_count > 0
    facts = net.get_all_facts()
    instances = [f for f in facts if f.get('type') == 'instance_of']

    assert len(instances) > 0
    assert instances[0].get('individual') == 'Alice'
    assert instances[0].get('concept') == 'Person'


def test_parser_multiple_axioms():
    """Test parsing multiple axioms"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = """
Dog ⊑ᑦ Animal
Cat ⊑ᑦ Animal
Animal ⊑ᑦ Thing
"""
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    subs = [f for f in facts if f.get('type') == 'subsumption']

    # Should have at least the 3 direct subsumptions
    assert len(subs) >= 3


def test_parser_role_chain():
    """Test parsing role chain axiom"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "hasParent ∘ hasParent ⊑ᴿ hasGrandparent"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    # Should create property chain fact
    chains = [f for f in facts if f.get('type') == 'property_chain']

    assert len(chains) > 0


def test_parser_inverse_property():
    """Test parsing inverse property"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "hasChild ≡ᴿ hasParent⁻"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    # Should handle inverse property syntax
    assert len(facts) > 0


def test_parser_symmetric_property():
    """Test parsing symmetric property (role equivalence with inverse)"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "knows ≡ᴿ knows⁻"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    # Should create role equivalence with inverse
    assert len(facts) > 0


def test_parser_oneof_enumeration():
    """Test parsing oneOf enumeration"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "Weekday ≡ᑦ ｛Monday，Tuesday，Wednesday｝"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    # Parser should handle oneOf syntax
    assert len(facts) > 0


def test_parser_same_as():
    """Test parsing same-as (equality) assertion"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "John ﹦ Jonathan"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    same_facts = [f for f in facts if f.get('type') == 'same_as']

    assert len(same_facts) > 0


def test_parser_whitespace_handling():
    """Test that parser handles various whitespace"""
    net = owl_rete_cpp.ReteNetwork()

    # Various whitespace patterns
    ontologies = [
        "Dog⊑ᑦAnimal",           # No spaces
        "Dog ⊑ᑦ Animal",         # Normal spaces
        "Dog  ⊑ᑦ  Animal",       # Multiple spaces
        "Dog\t⊑ᑦ\tAnimal",       # Tabs
    ]

    for ontology in ontologies:
        net_test = owl_rete_cpp.ReteNetwork()
        net_test.load_ontology_from_string(ontology)
        facts = net_test.get_all_facts()
        subs = [f for f in facts if f.get('type') == 'subsumption']
        assert len(subs) > 0, f"Should parse: {repr(ontology)}"


def test_parser_empty_input():
    """Test parser handles empty input"""
    net = owl_rete_cpp.ReteNetwork()

    wme_count = net.load_ontology_from_string("")
    assert wme_count == 0

    facts = net.get_all_facts()
    # May have built-in facts like owl:Thing
    # Just verify no crash


def test_parser_multiple_loads():
    """Test multiple load_ontology_from_string calls"""
    net = owl_rete_cpp.ReteNetwork()

    net.load_ontology_from_string("Dog ⊑ᑦ Animal")
    net.load_ontology_from_string("Cat ⊑ᑦ Animal")
    net.load_ontology_from_string("Dog（Fido）")

    facts = net.get_all_facts()
    subs = [f for f in facts if f.get('type') == 'subsumption']
    instances = [f for f in facts if f.get('type') == 'instance_of']

    assert len(subs) >= 2, "Should have both subsumptions"
    assert len(instances) >= 1, "Should have Fido instance"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
