"""Test what facts are created for simplification patterns"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_singleton_subsumption():
    print("\n=== Pattern 1: ｛Alice｝ ⊑ᑦ ｛Bob｝ ===")
    reasoner = Reter()
    ontology = "｛Alice｝ ⊑ᑦ ｛Bob｝"
    reasoner.load_ontology(ontology)
    facts = reasoner.query()
    for fact in facts:
        print(f"  {fact}")

def test_existential_singleton():
    print("\n=== Pattern 2: ｛Alice｝ ⊑ᑦ ∃hasParent․｛Bob｝ ===")
    reasoner = Reter()
    ontology = "｛Alice｝ ⊑ᑦ ∃hasParent․｛Bob｝"
    reasoner.load_ontology(ontology)
    facts = reasoner.query()
    for fact in facts:
        print(f"  {fact}")

def test_data_value():
    print("\n=== Pattern 3: ｛Alice｝ ⊑ᑦ ∃hasAge ﹦25 ===")
    reasoner = Reter()
    ontology = "｛Alice｝ ⊑ᑦ ∃hasAge ﹦25"
    reasoner.load_ontology(ontology)
    facts = reasoner.query()
    for fact in facts:
        print(f"  {fact}")

def test_inverse_role():
    print("\n=== Pattern 4: hasChild⁻（Alice， Bob） ===")
    reasoner = Reter()
    ontology = "hasChild⁻（Alice， Bob）"
    reasoner.load_ontology(ontology)
    facts = reasoner.query()
    for fact in facts:
        print(f"  {fact}")

if __name__ == '__main__':
    test_singleton_subsumption()
    test_existential_singleton()
    test_data_value()
    test_inverse_role()
