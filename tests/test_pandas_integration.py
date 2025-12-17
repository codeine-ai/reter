"""
Test Pandas Integration
Week 2, Day 1-3 of IMPLEMENTATION_PLAN.md
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter import Reter

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not installed. Install with: pip install pandas")


def test_to_pandas_basic():
    """Test basic to_pandas conversion"""
    if not PANDAS_AVAILABLE:
        print("Skipping test_to_pandas_basic - pandas not available")
        return

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
    """)

    # Query all persons
    results = r.pattern(("?x", "type", "Person"))

    # Convert to pandas
    df = results.to_pandas()

    print("DataFrame from query:")
    print(df)
    print(f"\nShape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Verify
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "?x" in df.columns
    assert set(df["?x"].values) == {"john", "mary", "bob"}

    print("✓ Basic to_pandas conversion works")


def test_to_pandas_with_join():
    """Test to_pandas with joined patterns"""
    if not PANDAS_AVAILABLE:
        print("Skipping test_to_pandas_with_join - pandas not available")
        return

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    # Query persons with ages
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age")
    )

    # Convert to pandas
    df = results.to_pandas()

    print("\nDataFrame from join query:")
    print(df)
    print(f"\nShape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Verify
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "?x" in df.columns
    assert "?age" in df.columns

    # Check specific values
    john_row = df[df["?x"] == "john"]
    assert len(john_row) == 1
    assert john_row["?age"].values[0] == "30"

    mary_row = df[df["?x"] == "mary"]
    assert len(mary_row) == 1
    assert mary_row["?age"].values[0] == "25"

    print("✓ to_pandas with join works")


def test_to_pandas_empty():
    """Test to_pandas with no results"""
    if not PANDAS_AVAILABLE:
        print("Skipping test_to_pandas_empty - pandas not available")
        return

    r = Reter()
    r.load_ontology("""
        Person（john）
    """)

    # Query for something that doesn't exist
    results = r.pattern(("?x", "type", "Robot"))

    # Convert to pandas
    df = results.to_pandas()

    print("\nEmpty DataFrame:")
    print(df)
    print(f"Shape: {df.shape}")

    # Verify
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert "?x" in df.columns

    print("✓ Empty DataFrame works")


def test_pandas_operations():
    """Test pandas operations on query results"""
    if not PANDAS_AVAILABLE:
        print("Skipping test_pandas_operations - pandas not available")
        return

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasAge（john，30）
        hasAge（mary，25）
        hasAge（bob，35）
    """)

    # Query persons with ages
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age")
    )

    df = results.to_pandas()

    # Convert age to numeric for operations
    df["age_numeric"] = pd.to_numeric(df["?age"])

    print("\nDataFrame with operations:")
    print(df)
    print(f"\nDescriptive statistics:")
    print(df["age_numeric"].describe())

    # Verify statistics
    assert df["age_numeric"].mean() == 30.0
    assert df["age_numeric"].min() == 25.0
    assert df["age_numeric"].max() == 35.0

    # Test filtering
    adults_over_26 = df[df["age_numeric"] > 26]
    print(f"\nPeople over 26: {list(adults_over_26['?x'].values)}")
    assert len(adults_over_26) == 2

    print("✓ Pandas operations work correctly")


if __name__ == "__main__":
    print("Testing Pandas Integration...")
    print("=" * 50)

    test_to_pandas_basic()
    print("\n" + "=" * 50)

    test_to_pandas_with_join()
    print("\n" + "=" * 50)

    test_to_pandas_empty()
    print("\n" + "=" * 50)

    test_pandas_operations()
    print("\n" + "=" * 50)

    if PANDAS_AVAILABLE:
        print("\n✓ All pandas integration tests passed!")
        print("Next: Week 2, Day 4-7 - Filter Support (SWRL builtins)")
    else:
        print("\n⚠ Pandas not available - install with: pip install pandas")
