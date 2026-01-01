# BUG-001: Double UNION in REQL Query Returns Empty Results

## Summary
When a REQL query contains two separate UNION blocks (e.g., one for caller type and one for callee type), the query returns empty results even though data exists.

## Severity
**High** - Affects complex queries that need to match multiple entity types on both sides of a relationship.

## Affected Components
- `reter_core/rete_cpp/sparql/ReqlExecutor.cpp`
- `reter_core/rete_cpp/sparql/HashIndexQueryExecutor.cpp`

## Reproduction

### Minimal Test Case
```python
from reter import Reter

r = Reter()
r.load_ontology("""
    py:Method(m1)
    py:Function(f1)
    name(m1, "test_method")
    name(f1, "test_func")
    calls(m1, f1)
""")

# This query returns EMPTY (BUG)
query = """
SELECT ?caller ?caller_name ?callee ?callee_name WHERE {
    { ?caller type py:Method } UNION { ?caller type py:Function }
    ?caller name ?caller_name .
    ?caller calls ?callee .
    { ?callee type py:Method } UNION { ?callee type py:Function }
    ?callee name ?callee_name .
}
"""
result = r.reql(query)
print(result.to_pylist())  # Returns [] - WRONG!

# Without second UNION - works correctly
query_single_union = """
SELECT ?caller ?caller_name ?callee WHERE {
    { ?caller type py:Method } UNION { ?caller type py:Function }
    ?caller name ?caller_name .
    ?caller calls ?callee .
}
"""
result = r.reql(query_single_union)
print(result.to_pylist())  # Returns data - CORRECT
```

### Expected Behavior
The query with two UNION blocks should return results where:
- `?caller` is either a Method or Function
- `?callee` is either a Method or Function
- The caller calls the callee

### Actual Behavior
The query returns an empty result set.

## Root Cause Analysis

The issue is in how multiple UNION blocks are processed. The current implementation:

1. Processes the first UNION block correctly
2. Joins with patterns outside the UNION (`?caller name ?caller_name`, `?caller calls ?callee`)
3. **FAILS** when encountering the second UNION block for `?callee`

The problem likely occurs because:
- After processing the first UNION and joining with additional patterns, the result table has specific columns
- The second UNION is processed independently and produces a different table structure
- The join between these tables fails silently or produces empty results

## Technical Details

### Query Parse Structure
```
SelectQuery:
  unions: [
    [  # First UNION block
      { whereTriples: [?caller type py:Method] },
      { whereTriples: [?caller type py:Function] }
    ],
    [  # Second UNION block
      { whereTriples: [?callee type py:Method] },
      { whereTriples: [?callee type py:Function] }
    ]
  ]
  whereTriples: [  # Patterns outside UNION
    ?caller name ?caller_name,
    ?caller calls ?callee,
    ?callee name ?callee_name
  ]
```

### Affected Code Paths
1. `ReqlExecutor::execute_union()` - handles UNION processing
2. `ReqlExecutor::execute_select()` - orchestrates query execution
3. `HashIndexQueryExecutor::execute_select_on_snapshot()` - timeout path

## Workaround

Use FILTER with CONTAINS instead of double UNION:

```sparql
SELECT ?caller ?caller_name ?callee ?callee_name WHERE {
    ?caller calls ?callee .
    ?caller name ?caller_name .
    ?caller concept ?caller_type .
    ?callee name ?callee_name .
    ?callee concept ?callee_type .
    FILTER(CONTAINS(?caller_type, "Method") || CONTAINS(?caller_type, "Function"))
    FILTER(CONTAINS(?callee_type, "Method") || CONTAINS(?callee_type, "Function"))
}
```

## Proposed Fix

### Option 1: Sequential UNION Processing
Process multiple UNION blocks sequentially, joining results at each step:

```cpp
std::shared_ptr<arrow::Table> execute_select(const SelectQuery& query) {
    std::shared_ptr<arrow::Table> result;

    // Process each UNION block sequentially
    for (const auto& union_block : query.unions) {
        auto union_result = execute_single_union(union_block);

        if (!result) {
            result = union_result;
        } else {
            // Join with previous results on shared variables
            result = join_tables(result, union_result, find_shared_variables(result, union_result));
        }
    }

    // Then join with whereTriples patterns
    if (!query.whereTriples.empty()) {
        auto patterns_result = execute_patterns(query.whereTriples);
        result = join_tables(result, patterns_result, find_shared_variables(result, patterns_result));
    }

    return result;
}
```

### Option 2: Flatten to Single UNION
Expand multiple UNION blocks into a single UNION with all combinations:

```
UNION1: {A} UNION {B}
UNION2: {C} UNION {D}
Patterns: P

Becomes:
{ A . C . P } UNION { A . D . P } UNION { B . C . P } UNION { B . D . P }
```

This is exponential but correct for small UNION blocks.

## Test Cases to Add

```python
# test_double_union.py

def test_double_union_basic():
    """Two UNION blocks should work together"""
    # ... setup ...
    result = r.reql("""
        SELECT ?a ?b WHERE {
            { ?a type X } UNION { ?a type Y }
            ?a rel ?b .
            { ?b type X } UNION { ?b type Y }
        }
    """)
    assert len(result) > 0

def test_triple_union():
    """Three UNION blocks should work"""
    # ... test with 3 UNION blocks ...

def test_union_with_optional():
    """UNION combined with OPTIONAL"""
    # ... test UNION + OPTIONAL interaction ...
```

## Related Issues
- Single UNION with patterns outside: FIXED in previous commit
- UNION inside subqueries: Not tested

## References
- SPARQL 1.1 UNION semantics: https://www.w3.org/TR/sparql11-query/#alternatives
- Arrow Acero join operations: https://arrow.apache.org/docs/cpp/compute.html
