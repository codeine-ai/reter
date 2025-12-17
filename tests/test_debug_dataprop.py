"""Debug test for data property assertions"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter import owl_rete_cpp

def test_dataprop_debug():
    """Debug: hasAge（Alice，30） fact type"""
    net = owl_rete_cpp.ReteNetwork()

    print("\n=== Loading hasAge（Alice，30） ===")
    net.load_ontology_from_string("hasAge（Alice，30）")

    # Get all facts
    fact_list = net.get_all_facts()
    print(f"\n=== All facts: {len(fact_list)} ===")

    for i, f in enumerate(fact_list):
        print(f"{i}: {f}")

    # Try different query types
    print("\n=== Try data_property_assertion ===")
    results = net.query({"type": "data_property_assertion"})
    print(f"Result: {len(results)} rows")
    if len(results) > 0:
        for i in range(len(results)):
            row = {col: results[col][i].as_py() for col in results.column_names if results[col][i].as_py() is not None}
            print(f"Row {i}: {row}")

if __name__ == "__main__":
    test_dataprop_debug()
