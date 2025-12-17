#!/usr/bin/env python3
"""
Test that C++ parser throws exceptions to Python for syntax errors
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter_core import owl_rete_cpp
import pytest


def test_missing_closing_paren():
    """Test that missing closing paren raises RuntimeError"""
    net = owl_rete_cpp.ReteNetwork()
    with pytest.raises(RuntimeError, match="Parse errors"):
        net.load_ontology_from_string("Dog ⊓（Animal")


def test_unmatched_parens():
    """Test that unmatched parens raises RuntimeError"""
    net = owl_rete_cpp.ReteNetwork()
    with pytest.raises(RuntimeError, match="Parse errors"):
        net.load_ontology_from_string("Dog（Animal")


def test_invalid_character_at():
    """Test that invalid character @ raises RuntimeError"""
    net = owl_rete_cpp.ReteNetwork()
    with pytest.raises(RuntimeError, match="Parse errors"):
        net.load_ontology_from_string("Dog @ Animal")


def test_invalid_character_hash():
    """Test that invalid character # raises RuntimeError"""
    net = owl_rete_cpp.ReteNetwork()
    with pytest.raises(RuntimeError, match="Parse errors"):
        net.load_ontology_from_string("Cat # Dog")


@pytest.mark.skip(reason="Requires ENABLE_OWL_THING_REASONING flag")
def test_valid_class_assertion():
    """Test that valid class assertion parses successfully"""
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Dog（Fido）")
    facts = net.get_all_facts()
    assert len(facts) == 2  # instance_of + owl:Thing


def test_empty_input():
    """Test that empty input is accepted (no statements is valid)"""
    net = owl_rete_cpp.ReteNetwork()
    # Empty input should be accepted without error
    net.load_ontology_from_string("")
    facts = net.get_all_facts()
    assert len(facts) == 0, "Empty input should create no facts"
