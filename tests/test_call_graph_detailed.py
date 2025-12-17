"""
Detailed analysis of call graph extraction

This test examines the exact WME structure created for function calls.
"""

from reter import Reter


def test_call_fact_structure():
    """Examine the detailed structure of call facts"""

    code = """
def foo():
    bar()

def bar():
    pass
"""

    r = Reter()
    r.load_python_code(code, "test")

    # Get ALL triples to see the structure
    query = """
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o
    }
    """

    result = r.reql(query)
    df = result.to_pandas()

    print(f"\n📊 Total WMEs: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head(10).to_string())

    # Filter for call-related facts
    call_facts = df[
        (df['?s'].str.contains('fact_', na=False)) &
        ((df['?p'] == 'caller') | (df['?p'] == 'callee') | (df['?p'] == 'concept') | (df['?p'] == 'type'))
    ]

    print(f"\n📋 Call-related WMEs:")
    print(call_facts.to_string())

    # Group by subject to see the structure of each call fact
    for fact_id in call_facts['?s'].unique():
        fact_wmes = call_facts[call_facts['?s'] == fact_id]
        print(f"\n🔹 Fact: {fact_id}")
        for _, row in fact_wmes.iterrows():
            print(f"  {row['?p']} → {row['?o']}")

    return call_facts


def test_query_variations():
    """Test different query patterns to understand the data model"""

    code = """
def caller_func():
    callee_func()
    another_func()

def callee_func():
    pass

def another_func():
    pass
"""

    r = Reter()
    r.load_python_code(code, "test")

    queries = [
        ("Direct properties", """
            SELECT ?call ?caller ?callee
            WHERE {
                ?call caller ?caller .
                ?call callee ?callee
            }
        """),
        ("With concept filter", """
            SELECT ?call ?caller ?callee
            WHERE {
                ?call concept "py:Call" .
                ?call caller ?caller .
                ?call callee ?callee
            }
        """),
        ("Find all calls from specific function", """
            SELECT ?callee
            WHERE {
                ?call caller "caller_func" .
                ?call callee ?callee
            }
        """),
        ("Find all calls to specific function", """
            SELECT ?caller
            WHERE {
                ?call caller ?caller .
                ?call callee "callee_func"
            }
        """),
        ("Transitive query (who calls who calls who)", """
            SELECT ?func1 ?func2 ?func3
            WHERE {
                ?call1 caller ?func1 .
                ?call1 callee ?func2 .
                ?call2 caller ?func2 .
                ?call2 callee ?func3
            }
        """),
    ]

    for name, query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {name}")
        print(f"{'='*60}")

        try:
            result = r.reql(query)
            df = result.to_pandas()
            print(f"Results: {len(df)} rows")
            if len(df) > 0:
                print(df.to_string())
            else:
                print("(empty)")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Detailed Call Graph Analysis")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("Part 1: Call Fact Structure")
    print("=" * 60)
    test_call_fact_structure()

    print("\n" + "=" * 60)
    print("Part 2: Query Variations")
    print("=" * 60)
    test_query_variations()
