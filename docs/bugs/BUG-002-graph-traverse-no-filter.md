# BUG-002: CADSL graph_traverse Returns All Edges Instead of Subgraph

## Summary
The `graph_traverse` operator in CADSL pipelines returns the entire graph instead of filtering to just the connected subgraph rooted at the specified `root` node.

## Severity
**Medium** - Diagrams are generated but contain unnecessary nodes, making them too large to be useful.

## Affected Components
- `reter_code/src/reter_code/dsl/arrow_pipeline.py` - ArrowGraphTraverseStep
- `reter_code/src/reter_code/cadsl/tools/diagrams/call_graph.cadsl`

## Reproduction

### Test Case
```python
# Using the call_graph CADSL tool
from reter_code.cadsl.tools_bridge import execute_tool

result = execute_tool("call_graph", {
    "target": "owl_rete::JoinReorderer::reorder_type_last",
    "max_depth": 3
})

# Expected: Small diagram with ~10-20 nodes reachable from target
# Actual: Huge diagram with 1000+ nodes (entire codebase call graph)
print(len(result["diagram"]))  # 212,320 characters!
```

### Expected Behavior
Given a call graph and target node `A`:
```
A -> B -> C
     B -> D
E -> F -> G
```

With `root: A` and `max_depth: 2`, should return:
```
A -> B
B -> C
B -> D
```

### Actual Behavior
Returns all edges in the graph, including unconnected subgraphs (E -> F -> G).

## Root Cause Analysis

Looking at the `graph_traverse` implementation in `arrow_pipeline.py`:

```python
class ArrowGraphTraverseStep(ArrowStep):
    def execute(self, table: pa.Table, context: Dict[str, Any]) -> pa.Table:
        # ... setup ...

        # BUG: The traversal logic may not be filtering correctly
        # or the root matching fails due to name format mismatch

        if self.algorithm == "bfs":
            visited = self._bfs_traverse(edges, root, max_depth)
        else:
            visited = self._dfs_traverse(edges, root, max_depth)

        # Filter to only visited edges
        # BUG: This filter may not be working correctly
        return self._filter_to_visited(table, visited)
```

Possible causes:
1. **Root node not found**: The `root` parameter format doesn't match the `from_node` values in the data
2. **Traversal returns all**: The BFS/DFS implementation may have a bug that marks all nodes as visited
3. **Filter not applied**: The filtering step after traversal may not be working

## Debugging Steps

### 1. Check Root Node Matching
```python
# The call_graph.cadsl uses qualified names as from_node
# e.g., "owl_rete::JoinReorderer::reorder_type_last"

# Check if target exactly matches from_node values
query = """
SELECT DISTINCT ?caller WHERE {
    ?caller calls ?callee .
    FILTER(?caller = "owl_rete::JoinReorderer::reorder_type_last")
}
"""
```

### 2. Verify Edge Data Structure
```python
# Check the from_node/to_node column values
edges_df = result_table.to_pandas()
print(edges_df[["from_node", "to_node"]].head(20))
print(f"Root '{target}' in from_node: {target in edges_df['from_node'].values}")
```

### 3. Test Traversal Logic
```python
# Test with a simple known graph
test_edges = [
    ("A", "B"), ("B", "C"), ("B", "D"),
    ("E", "F"), ("F", "G")
]
# BFS from "A" with depth 2 should return {"A", "B", "C", "D"}
```

## Proposed Fix

### Option 1: Fix Root Matching
Ensure the root parameter is matched correctly, possibly with case-insensitive or partial matching:

```python
def _find_root_node(self, edges: Dict[str, List[str]], root: str) -> Optional[str]:
    """Find the actual root node in the graph, handling format differences."""
    # Exact match
    if root in edges:
        return root

    # Try without namespace prefix
    short_name = root.split("::")[-1]
    for node in edges:
        if node.endswith(short_name):
            return node

    # Try partial match
    for node in edges:
        if root in node or node in root:
            return node

    return None
```

### Option 2: Fix BFS Implementation
Ensure BFS properly limits traversal:

```python
def _bfs_traverse(self, edges: Dict[str, List[str]], root: str, max_depth: int) -> Set[str]:
    """BFS traversal with proper depth limiting."""
    if root not in edges:
        logger.warning(f"Root node '{root}' not found in graph with {len(edges)} nodes")
        return set()  # Return empty, not all nodes!

    visited = set()
    queue = [(root, 0)]  # (node, depth)

    while queue:
        node, depth = queue.pop(0)

        if node in visited:
            continue
        if depth > max_depth:
            continue

        visited.add(node)

        for neighbor in edges.get(node, []):
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))

    return visited
```

### Option 3: Fix Edge Filtering
Ensure the filter step only keeps visited edges:

```python
def _filter_to_visited(self, table: pa.Table, visited: Set[str]) -> pa.Table:
    """Filter table to only edges where both endpoints are visited."""
    if not visited:
        # No nodes visited = root not found, return empty table
        return table.slice(0, 0)

    from_col = table.column(self.from_field).to_pylist()
    to_col = table.column(self.to_field).to_pylist()

    mask = [
        from_node in visited and to_node in visited
        for from_node, to_node in zip(from_col, to_col)
    ]

    return table.filter(pa.array(mask))
```

## Test Cases to Add

```python
# test_graph_traverse.py

def test_graph_traverse_filters_to_subgraph():
    """graph_traverse should only return reachable nodes"""
    edges = pa.table({
        "from": ["A", "B", "B", "E", "F"],
        "to": ["B", "C", "D", "F", "G"]
    })

    step = ArrowGraphTraverseStep(
        from_field="from",
        to_field="to",
        algorithm="bfs",
        max_depth=10,
        root="A"
    )

    result = step.execute(edges, {})

    # Should only have A->B, B->C, B->D
    assert len(result) == 3
    assert "E" not in result.column("from").to_pylist()
    assert "G" not in result.column("to").to_pylist()

def test_graph_traverse_respects_max_depth():
    """max_depth should limit traversal"""
    # A -> B -> C -> D -> E
    edges = pa.table({
        "from": ["A", "B", "C", "D"],
        "to": ["B", "C", "D", "E"]
    })

    step = ArrowGraphTraverseStep(
        from_field="from", to_field="to",
        algorithm="bfs", max_depth=2, root="A"
    )

    result = step.execute(edges, {})

    # With max_depth=2: A->B (depth 1), B->C (depth 2)
    # D->E should NOT be included (depth 3)
    assert len(result) == 2

def test_graph_traverse_root_not_found():
    """Should return empty when root not in graph"""
    edges = pa.table({
        "from": ["A", "B"],
        "to": ["B", "C"]
    })

    step = ArrowGraphTraverseStep(
        from_field="from", to_field="to",
        algorithm="bfs", max_depth=10, root="NONEXISTENT"
    )

    result = step.execute(edges, {})
    assert len(result) == 0
```

## Workaround

Until fixed, manually filter the diagram output or use code_inspection tools:

```python
# Use find_callees with depth limit instead
result = code_inspection(
    action="find_callees",
    target="reorder_type_last",
    params={"max_depth": 3}
)
```

## Related Issues
- call_graph.cadsl double UNION issue (BUG-001) - needed workaround before this could be tested
- Large diagram output causes token limit issues

## References
- Mermaid flowchart syntax: https://mermaid.js.org/syntax/flowchart.html
- BFS algorithm: https://en.wikipedia.org/wiki/Breadth-first_search
