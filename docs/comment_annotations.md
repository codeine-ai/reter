# Comment-Based Semantic Annotations

RETER supports extracting semantic facts from specially formatted comments in your code using the `@reter:` annotation syntax. This allows you to add architectural metadata, dependency information, and custom semantic relationships directly in your source code.

## Overview

Comment annotations let you define semantic facts that become queryable alongside the automatically extracted code structure. This is useful for:

- Documenting architectural layers (Presentation, Business, Data Access)
- Explicitly declaring dependencies between components
- Marking code with custom concepts (CriticalPath, SecuritySensitive, etc.)
- Adding metadata that can't be inferred from code structure

## Annotation Syntax

### Basic Format

```
@reter: Predicate(Argument1, Argument2, ...)
```

### Three Types of Annotations

| Type | Syntax | Description |
|------|--------|-------------|
| **Concept** | `@reter: Concept(Individual)` | Asserts that an entity belongs to a concept/class |
| **Object Role** | `@reter: role(Subject, Object)` | Relates two entities |
| **Data Role** | `@reter: role(Subject, "literal")` | Relates an entity to a literal value |

### Special References

- `self`, `this`, `.` - Resolved to the current class or method being documented

### Supported Prefixes

All of these work identically:
- `@reter:`
- `#reter:`
- `reter:`
- `@semantic:`
- `@owl:`
- `@fact:`

## Language Support

### Python

Use docstrings with `@reter:` annotations:

```python
class OrderService:
    """
    Handles order processing.

    @reter: BusinessLayer(self)
    @reter: dependsOn(self, services.PaymentService)
    @reter: hasOwner(self, "Team A")
    """

    def process_order(self, order):
        """
        @reter: UseCase(self)
        @reter: calls(self, services.PaymentService.charge)
        """
        pass
```

### JavaScript / TypeScript

Use JSDoc comments:

```javascript
/**
 * Authentication service.
 * @reter: SecurityLayer(AuthService)
 * @reter: dependsOn(AuthService, TokenStore)
 */
class AuthService {
    /**
     * @reter: CriticalPath(login)
     */
    login(credentials) {
        // ...
    }
}
```

### C#

Use XML documentation comments or regular comments:

```csharp
/// <summary>
/// Order repository.
/// @reter: DataAccessLayer(OrderRepository)
/// @reter: implements(OrderRepository, IOrderRepository)
/// </summary>
public class OrderRepository
{
    /// @reter: DatabaseOperation(Save)
    public void Save(Order order) { }
}
```

### C++

Use block comments or line comments:

```cpp
/**
 * Memory pool allocator.
 * @reter: InfrastructureLayer(MemoryPool)
 * @reter: hasComplexity(MemoryPool, "O(1)")
 */
class MemoryPool {
public:
    // @reter: PerformanceCritical(allocate)
    void* allocate(size_t size);
};
```

### HTML

Use HTML comments:

```html
<!DOCTYPE html>
<!-- @reter: WebPage(HomePage) -->
<!-- @reter: belongsTo(HomePage, MarketingSite) -->
<html>
<head>
    <!-- @reter: hasAuthor(HomePage, "Design Team") -->
    <title>Home</title>
</head>
<body>
    <!-- @reter: UIComponent(MainContent) -->
    <main id="content">...</main>
</body>
</html>
```

## Querying Annotations

### Pattern API

```python
from reter import Reter

r = Reter()
r.load_python_code(code, 'services.py')

# Find all BusinessLayer classes
results = r.pattern(('?class', 'type', 'user:BusinessLayer')).to_list()
for result in results:
    print(result['?class'])

# Find dependencies
deps = r.pattern(('?source', 'dependsOn', '?target')).to_list()
for dep in deps:
    print(f"{dep['?source']} depends on {dep['?target']}")
```

### REQL Queries

```python
# Find classes in BusinessLayer
results = r.reql('SELECT ?c WHERE { ?c type user:BusinessLayer }')
classes = results[0].to_pylist()

# Find what BusinessLayer depends on
results = r.reql('''
    SELECT ?source ?target WHERE {
        ?source type user:BusinessLayer .
        ?source dependsOn ?target
    }
''')

# Join with code structure - find BusinessLayer classes with their methods
results = r.reql('''
    SELECT ?class ?method WHERE {
        ?class type user:BusinessLayer .
        ?class type py:Class .
        ?method definedIn ?class .
        ?method type py:Method
    }
''')
```

## Reference Naming

### Qualified Names

For annotations to join properly with extracted code facts, use **fully qualified names**:

```python
# Module: services.py

class PaymentService:
    pass

class OrderService:
    """
    # Use qualified name to match the extracted class
    @reter: dependsOn(self, services.PaymentService)
    """
    pass
```

The extractor creates class individuals like `services.PaymentService`, so your annotation references should match this format.

### Using `self`

The `self` reference is automatically resolved to the qualified name:

```python
# In services.py
class OrderService:
    """
    @reter: BusinessLayer(self)
    # Equivalent to: @reter: BusinessLayer(services.OrderService)
    """
```

## Common Use Cases

### Architectural Layers

```python
class UserController:
    """
    @reter: PresentationLayer(self)
    """

class UserService:
    """
    @reter: BusinessLayer(self)
    @reter: dependsOn(self, app.repositories.UserRepository)
    """

class UserRepository:
    """
    @reter: DataAccessLayer(self)
    """
```

Query layer violations:
```python
# Find if Presentation layer directly accesses Data layer
results = r.reql('''
    SELECT ?presentation ?data WHERE {
        ?presentation type user:PresentationLayer .
        ?data type user:DataAccessLayer .
        ?presentation dependsOn ?data
    }
''')
```

### Security Annotations

```python
class AuthService:
    """
    @reter: SecurityCritical(self)
    @reter: requiresAudit(self, "true")
    """

    def validate_token(self, token):
        """
        @reter: SecuritySensitive(self)
        @reter: handlesCredentials(self, "JWT")
        """
```

### Domain-Driven Design

```python
class Order:
    """
    @reter: AggregateRoot(self)
    @reter: inBoundedContext(self, OrderManagement)
    """

class OrderLine:
    """
    @reter: Entity(self)
    @reter: partOf(self, domain.Order)
    """

class OrderPlaced:
    """
    @reter: DomainEvent(self)
    @reter: raisedBy(self, domain.Order)
    """
```

### Cross-File Dependencies

```python
# file: services/order_service.py
class OrderService:
    """
    @reter: dependsOn(self, services.payment.PaymentGateway)
    @reter: dependsOn(self, services.inventory.StockService)
    @reter: publishes(self, events.OrderCreated)
    """
```

## Annotation Attributes

You can add key-value attributes to concept assertions:

```python
class CacheManager:
    """
    @reter: CriticalComponent(self, priority=high, team=infrastructure)
    """
```

These become additional attributes on the generated fact.

## Fact Types Generated

| Annotation Type | Generated Fact Type | Key Attributes |
|-----------------|---------------------|----------------|
| Concept | `instance_of` | `individual`, `concept` |
| Object Role | `role_assertion` | `subject`, `role`, `object` |
| Data Role | `role_assertion` | `subject`, `role`, `object`, `value`, `datatype` |

All facts include:
- `inFile` - Source file path
- `atLine` - Line number
- `source` - Always `"comment_annotation"`

## Best Practices

1. **Use qualified names** for cross-file references to ensure proper joins
2. **Use `self`** for the current class/method to avoid duplication
3. **Be consistent** with naming conventions across your codebase
4. **Document your custom concepts** so team members understand the ontology
5. **Query your annotations** to validate architectural rules in CI/CD

## Example: Complete Workflow

```python
from reter import Reter

# Load your codebase
r = Reter()
r.load_python_directory('src/', recursive=True)

# Find architectural violations
violations = r.reql('''
    SELECT ?controller ?repo WHERE {
        ?controller type user:PresentationLayer .
        ?repo type user:DataAccessLayer .
        ?controller calls ?method .
        ?method definedIn ?repo
    }
''')

if violations[0].to_pylist():
    print("Warning: Controllers directly accessing repositories!")
    for ctrl, repo in zip(violations[0].to_pylist(), violations[1].to_pylist()):
        print(f"  {ctrl} -> {repo}")
```
