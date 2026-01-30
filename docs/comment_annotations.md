# Comment-Based Semantic Annotations

RETER supports extracting semantic facts from specially formatted comments in your code. Two syntax styles are available:

1. **CNL syntax** (`@reter-cnl:`) - **PREFERRED** - Natural language style using Controlled Natural Language
2. **Predicate syntax** (`@reter:`) - **DEPRECATED** - Compact, programmatic style (still supported for backwards compatibility)

This allows you to add architectural metadata, dependency information, and custom semantic relationships directly in your source code.

## Overview

Comment annotations let you define semantic facts that become queryable alongside the automatically extracted code structure. This is useful for:

- Documenting architectural layers (Presentation, Service, Infrastructure)
- Explicitly declaring dependencies between components
- Marking code with custom concepts (critical-path, security-sensitive, etc.)
- Adding metadata that can't be inferred from code structure

---

## CNL Annotations (`@reter-cnl:`) - PREFERRED

CNL (Controlled Natural Language) provides a readable, English-like syntax for semantic annotations.

### Basic Format

```
@reter-cnl: This is-in-layer Service-Layer.
@reter-cnl: This is a repository.
@reter-cnl: This depends-on `services.PaymentService`.
```

### Key Rules

- **Layers** use relations: `This is-in-layer <Layer-Name>.` (hyphenated, Title-Case)
- **Components** use concept assertions: `This is a <concept>.` (lowercase)
- **Relations** use predicates: `This depends-on <Target>.`
- **`This`** is automatically resolved to the current class/method as a fully qualified name
- Use **backticks** for qualified names: `` `module.ClassName` ``
- Sentences end with `.` or `?`
- No acronyms - use full words (e.g., `Domain-Specific-Language-Layer` not `DSL-Layer`)

### Supported Prefixes

- `@reter-cnl:`
- `#reter-cnl:`
- `reter-cnl:`

### CNL Sentence Patterns

| Pattern | Example | Meaning |
|---------|---------|---------|
| **Layer relation** | `This is-in-layer Service-Layer.` | Architectural layer |
| **Concept assertion** | `This is a repository.` | Functional role |
| **Role assertion** | `This depends-on Payment-Service.` | Object property |
| **Data property** | `This has-version "1.0".` | Data value |
| **Subsumption** | `Every controller is a component.` | Class hierarchy |
| **Restriction** | `Every service must have-logger.` | Existential restriction |

### Architectural Layers

| Layer | CNL Name |
|-------|----------|
| Presentation | `Presentation-Layer` |
| Service | `Service-Layer` |
| Domain-Specific-Language | `Domain-Specific-Language-Layer` |
| Infrastructure | `Infrastructure-Layer` |
| Core | `Core-Layer` |
| Test | `Test-Layer` |
| Utility | `Utility-Layer` |

### Functional Components (Concepts)

| Component | CNL Concept |
|-----------|-------------|
| Repository | `repository` |
| Service | `service` |
| Handler | `handler` |
| Manager | `manager` |
| Parser | `parser` |
| Compiler | `compiler` |
| Value-Object | `value-object` |
| Factory | `factory` |
| Builder | `builder` |

---

## Language Examples (CNL)

### Python

```python
class OrderService:
    """
    Handles order processing.

    @reter-cnl: This is-in-layer Service-Layer.
    @reter-cnl: This is a service.
    @reter-cnl: This depends-on `services.PaymentService`.
    @reter-cnl: This has-owner "Team A".
    """

    def process_order(self, order):
        """
        @reter-cnl: This is a critical-path.
        """
        pass
```

### JavaScript / TypeScript

```javascript
/**
 * Authentication service.
 * @reter-cnl: This is-in-layer Service-Layer.
 * @reter-cnl: This is a handler.
 * @reter-cnl: This depends-on `TokenStore`.
 */
class AuthService {
    /**
     * @reter-cnl: This is a critical-path.
     */
    login(credentials) {
        // ...
    }
}
```

### C#

```csharp
/// <summary>
/// Order repository.
/// @reter-cnl: This is-in-layer Infrastructure-Layer.
/// @reter-cnl: This is a repository.
/// @reter-cnl: This implements `IOrderRepository`.
/// </summary>
public class OrderRepository
{
    /// @reter-cnl: This is a database-operation.
    public void Save(Order order) { }
}
```

### C++

```cpp
/**
 * Memory pool allocator.
 * @reter-cnl: This is-in-layer Core-Layer.
 * @reter-cnl: This is a manager.
 * @reter-cnl: This has-complexity "O(1)".
 */
class MemoryPool {
public:
    // @reter-cnl: This is a performance-critical.
    void* allocate(size_t size);
};
```

### HTML

```html
<!DOCTYPE html>
<!-- @reter-cnl: This is a web-page. -->
<!-- @reter-cnl: This belongs-to Marketing-Site. -->
<html>
<head>
    <!-- @reter-cnl: This has-author "Design Team". -->
    <title>Home</title>
</head>
<body>
    <!-- @reter-cnl: This is a user-interface-component. -->
    <main id="content">...</main>
</body>
</html>
```

---

## Common Use Cases

### Architectural Layers

```python
class UserController:
    """
    @reter-cnl: This is-in-layer Presentation-Layer.
    @reter-cnl: This is a controller.
    """

class UserService:
    """
    @reter-cnl: This is-in-layer Service-Layer.
    @reter-cnl: This is a service.
    @reter-cnl: This depends-on `app.repositories.UserRepository`.
    """

class UserRepository:
    """
    @reter-cnl: This is-in-layer Infrastructure-Layer.
    @reter-cnl: This is a repository.
    """
```

### Security Annotations

```python
class AuthService:
    """
    @reter-cnl: This is a security-critical.
    @reter-cnl: This requires-audit "true".
    """

    def validate_token(self, token):
        """
        @reter-cnl: This is a security-sensitive.
        @reter-cnl: This handles-credentials "JSON-Web-Token".
        """
```

### Domain-Driven Design

```python
class Order:
    """
    @reter-cnl: This is a aggregate-root.
    @reter-cnl: This is-in-bounded-context Order-Management.
    """

class OrderLine:
    """
    @reter-cnl: This is a entity.
    @reter-cnl: This is-part-of `domain.Order`.
    """

class OrderPlaced:
    """
    @reter-cnl: This is a domain-event.
    @reter-cnl: This is-raised-by `domain.Order`.
    """
```

### Design Patterns

```python
class ConfigManager:
    """
    @reter-cnl: This is a singleton.
    """

class VehicleFactory:
    """
    @reter-cnl: This is a factory.
    @reter-cnl: This creates `domain.Vehicle`.
    """
```

### Cross-File Dependencies

```python
# file: services/order_service.py
class OrderService:
    """
    @reter-cnl: This depends-on `services.payment.PaymentGateway`.
    @reter-cnl: This depends-on `services.inventory.StockService`.
    @reter-cnl: This publishes `events.OrderCreated`.
    """
```

---

## Querying Annotations

### Pattern API

```python
from reter import Reter

r = Reter()
r.load_python_code(code, 'services.py')

# Find all Service-Layer classes
results = r.pattern(('?class', 'is-in-layer', 'Service-Layer')).to_list()
for result in results:
    print(result['?class'])

# Find dependencies
deps = r.pattern(('?source', 'depends-on', '?target')).to_list()
for dep in deps:
    print(f"{dep['?source']} depends on {dep['?target']}")
```

### REQL Queries

```python
# Find classes in Service-Layer
results = r.reql('SELECT ?c WHERE { ?c is-in-layer Service-Layer }')
classes = results[0].to_pylist()

# Find what Service-Layer depends on
results = r.reql('''
    SELECT ?source ?target WHERE {
        ?source is-in-layer Service-Layer .
        ?source depends-on ?target
    }
''')
```

---

## Predicate Annotations (`@reter:`) - DEPRECATED

> **Note:** This syntax is deprecated. Use `@reter-cnl:` instead.

The predicate syntax is still supported for backwards compatibility.

### Basic Format

```
@reter: Predicate(Argument1, Argument2, ...)
```

### Three Types

| Type | Syntax | Description |
|------|--------|-------------|
| **Concept** | `@reter: Concept(Individual)` | Asserts that an entity belongs to a concept/class |
| **Object Role** | `@reter: role(Subject, Object)` | Relates two entities |
| **Data Role** | `@reter: role(Subject, "literal")` | Relates an entity to a literal value |

### Supported Prefixes

- `@reter:`
- `#reter:`
- `reter:`
- `@semantic:`
- `@owl:`
- `@fact:`

### Migration to CNL

| Deprecated Predicate Syntax | Preferred CNL Syntax |
|----------------------------|----------------------|
| `@reter: ServiceLayer(self)` | `@reter-cnl: This is-in-layer Service-Layer.` |
| `@reter: Repository(self)` | `@reter-cnl: This is a repository.` |
| `@reter: dependsOn(self, services.X)` | ``@reter-cnl: This depends-on `services.X`.`` |
| `@reter: hasOwner(self, "Team A")` | `@reter-cnl: This has-owner "Team A".` |

---

## Best Practices

1. **Use `@reter-cnl:`** - The CNL syntax is preferred and more readable
2. **Use qualified names** for cross-file references with backticks
3. **Use `This`** for the current class/method to avoid duplication
4. **Be consistent** with naming conventions across your codebase
5. **No acronyms** - Use `Domain-Specific-Language-Layer` not `DSL-Layer`
6. **Lowercase concepts** - Use `This is a repository.` not `This is a Repository.`

## Fact Types Generated

| Annotation Type | Generated Fact Type | Key Attributes |
|-----------------|---------------------|----------------|
| Layer relation | `role_assertion` | `subject`, `role`, `object` |
| Concept assertion | `instance_of` | `individual`, `concept` |
| Object Role | `role_assertion` | `subject`, `role`, `object` |
| Data Role | `role_assertion` | `subject`, `role`, `value`, `datatype` |

All facts include:
- `inFile` - Source file path
- `atLine` - Line number
- `source` - `"cnl_annotation"` or `"comment_annotation"`
