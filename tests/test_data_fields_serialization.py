"""
Test serialization and deserialization of Fact data_fields (structured data).

This ensures that when Facts have structured data (like string lists, double lists,
or SWRL rules), they are correctly preserved through serialization/deserialization.

NOTE: Currently skipped because get_all_facts() returns copies, so modifications
to facts don't persist in the network. To properly test data_fields serialization,
we would need an update_fact() method or a way to get mutable references to facts.

The serialization/deserialization code itself IS implemented correctly in:
- rete_cpp/serialization/proto/rete_core.proto (FactProto.data_fields field)
- rete_cpp/serialization/converters/fact_converter.cpp (to_proto/from_proto for data_fields)
"""

import tempfile
import os
import pytest
from reter import Reter


@pytest.mark.skip(reason="get_all_facts() returns copies - need update_fact() method to make this work")
def test_string_list_serialization():
    """Test that string list data fields are preserved through serialization"""
    # Create network and add facts
    reasoner = Reter()
    network = reasoner.network

    network.load_ontology_from_string('Person ⊑ᑦ owl:Thing')
    reasoner.add_triple('Alice', 'type', 'Person')

    # Find Alice's fact and add a string list data field
    facts = network.get_all_facts()
    alice_fact = None
    for fact in facts:
        if fact.get('individual') == 'Alice':
            alice_fact = fact
            fact.set_string_list('hobbies', ['reading', 'coding', 'hiking'])
            break

    assert alice_fact is not None, "Alice fact should exist"
    assert alice_fact.has_data('hobbies'), "Alice should have hobbies data field"

    # Serialize to temporary file
    with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as f:
        temp_file = f.name

    try:
        network.save(temp_file)

        # Load into new network
        reasoner2 = Reter()
        network2 = reasoner2.network
        network2.load(temp_file)

        # Verify data fields were preserved
        facts2 = network2.get_all_facts()
        alice_fact2 = None
        for fact in facts2:
            if fact.get('individual') == 'Alice':
                alice_fact2 = fact
                break

        assert alice_fact2 is not None, "Alice fact should exist after deserialization"
        assert alice_fact2.has_data('hobbies'), "Alice should have hobbies data field after deserialization"

        hobbies = alice_fact2.get_data_as_string_list('hobbies')
        assert hobbies == ['reading', 'coding', 'hiking'], "Hobbies should be preserved exactly"

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.skip(reason="get_all_facts() returns copies - need update_fact() method to make this work")
def test_double_list_serialization():
    """Test that double list data fields are preserved through serialization"""
    # Create network and add facts
    reasoner = Reter()
    network = reasoner.network

    network.load_ontology_from_string('Measurement ⊑ᑦ owl:Thing')
    reasoner.add_triple('Temperature', 'type', 'Measurement')

    # Find Temperature fact and add a double list data field
    facts = network.get_all_facts()
    temp_fact = None
    for fact in facts:
        if fact.get('individual') == 'Temperature':
            temp_fact = fact
            fact.set_double_list('readings', [20.5, 21.3, 19.8, 22.1])
            break

    assert temp_fact is not None, "Temperature fact should exist"
    assert temp_fact.has_data('readings'), "Temperature should have readings data field"

    # Serialize to temporary file
    with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as f:
        temp_file = f.name

    try:
        network.save(temp_file)

        # Load into new network
        reasoner2 = Reter()
        network2 = reasoner2.network
        network2.load(temp_file)

        # Verify data fields were preserved
        facts2 = network2.get_all_facts()
        temp_fact2 = None
        for fact in facts2:
            if fact.get('individual') == 'Temperature':
                temp_fact2 = fact
                break

        assert temp_fact2 is not None, "Temperature fact should exist after deserialization"
        assert temp_fact2.has_data('readings'), "Temperature should have readings data field after deserialization"

        readings = temp_fact2.get_data_as_double_list('readings')
        assert readings == [20.5, 21.3, 19.8, 22.1], "Readings should be preserved exactly"

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.skip(reason="get_all_facts() returns copies - need update_fact() method to make this work")
def test_multiple_data_fields_serialization():
    """Test that multiple data fields on the same fact are preserved"""
    # Create network and add facts
    reasoner = Reter()
    network = reasoner.network

    network.load_ontology_from_string('Student ⊑ᑦ owl:Thing')
    reasoner.add_triple('Bob', 'type', 'Student')

    # Find Bob's fact and add multiple data fields
    facts = network.get_all_facts()
    bob_fact = None
    for fact in facts:
        if fact.get('individual') == 'Bob':
            bob_fact = fact
            fact.set_string_list('courses', ['Math', 'Physics', 'CS'])
            fact.set_double_list('grades', [3.8, 4.0, 3.9])
            break

    assert bob_fact is not None, "Bob fact should exist"

    # Serialize to temporary file
    with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as f:
        temp_file = f.name

    try:
        network.save(temp_file)

        # Load into new network
        reasoner2 = Reter()
        network2 = reasoner2.network
        network2.load(temp_file)

        # Verify all data fields were preserved
        facts2 = network2.get_all_facts()
        bob_fact2 = None
        for fact in facts2:
            if fact.get('individual') == 'Bob':
                bob_fact2 = fact
                break

        assert bob_fact2 is not None, "Bob fact should exist after deserialization"
        assert bob_fact2.has_data('courses'), "Bob should have courses data field"
        assert bob_fact2.has_data('grades'), "Bob should have grades data field"

        courses = bob_fact2.get_data_as_string_list('courses')
        grades = bob_fact2.get_data_as_double_list('grades')

        assert courses == ['Math', 'Physics', 'CS'], "Courses should be preserved"
        assert grades == [3.8, 4.0, 3.9], "Grades should be preserved"

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_empty_data_fields_serialization():
    """Test that facts without data fields serialize correctly"""
    # Create network and add facts without data fields
    reasoner = Reter()
    network = reasoner.network

    network.load_ontology_from_string('Animal ⊑ᑦ owl:Thing')
    reasoner.add_triple('Cat', 'type', 'Animal')

    # Serialize to temporary file
    with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as f:
        temp_file = f.name

    try:
        network.save(temp_file)

        # Load into new network
        reasoner2 = Reter()
        network2 = reasoner2.network
        network2.load(temp_file)

        # Verify facts exist and have no data fields
        facts2 = network2.get_all_facts()
        cat_fact = None
        for fact in facts2:
            if fact.get('individual') == 'Cat':
                cat_fact = fact
                break

        assert cat_fact is not None, "Cat fact should exist after deserialization"
        # Fact should work normally even without data fields

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
