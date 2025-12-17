"""
Test cases for Unify Interfaces pattern detection.

This file contains examples of class hierarchies where methods exist
in multiple subclasses but not in their superclass, indicating
opportunities to unify interfaces by adding these methods to the superclass.
"""

# Example 1: Animal hierarchy missing common sound methods
class Animal:
    """Base class missing make_sound() that all subclasses have."""

    def move(self):
        """All animals can move."""
        pass

    def eat(self):
        """All animals eat."""
        pass

    # Missing: make_sound() - all subclasses have this


class Dog(Animal):
    """Dog with make_sound method."""

    def move(self):
        return "runs on four legs"

    def eat(self):
        return "chomps food"

    def make_sound(self):
        """Dogs bark."""
        return "woof"

    def wag_tail(self):
        """Dog-specific behavior."""
        return "wagging"


class Cat(Animal):
    """Cat with make_sound method."""

    def move(self):
        return "prowls silently"

    def eat(self):
        return "nibbles delicately"

    def make_sound(self):
        """Cats meow."""
        return "meow"

    def purr(self):
        """Cat-specific behavior."""
        return "purring"


class Bird(Animal):
    """Bird with make_sound method."""

    def move(self):
        return "flies through air"

    def eat(self):
        return "pecks at food"

    def make_sound(self):
        """Birds chirp."""
        return "chirp"

    def build_nest(self):
        """Bird-specific behavior."""
        return "building nest"


# Example 2: Shape hierarchy missing area and perimeter
class Shape:
    """Base shape class missing common calculation methods."""

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    # Missing: calculate_area() and calculate_perimeter()


class Rectangle(Shape):
    """Rectangle with area and perimeter methods."""

    def __init__(self, width, height):
        super().__init__("Rectangle")
        self.width = width
        self.height = height

    def calculate_area(self):
        """Calculate rectangle area."""
        return self.width * self.height

    def calculate_perimeter(self):
        """Calculate rectangle perimeter."""
        return 2 * (self.width + self.height)


class Circle(Shape):
    """Circle with area and perimeter methods."""

    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius

    def calculate_area(self):
        """Calculate circle area."""
        import math
        return math.pi * self.radius ** 2

    def calculate_perimeter(self):
        """Calculate circle perimeter (circumference)."""
        import math
        return 2 * math.pi * self.radius


class Triangle(Shape):
    """Triangle with area and perimeter methods."""

    def __init__(self, base, height, side1, side2, side3):
        super().__init__("Triangle")
        self.base = base
        self.height = height
        self.sides = [side1, side2, side3]

    def calculate_area(self):
        """Calculate triangle area."""
        return 0.5 * self.base * self.height

    def calculate_perimeter(self):
        """Calculate triangle perimeter."""
        return sum(self.sides)


# Example 3: Document processor missing validation and export
class DocumentProcessor:
    """Base processor missing common operations."""

    def __init__(self):
        self.content = None

    def load(self, path):
        """Load document from path."""
        pass

    # Missing: validate() and export_to_json() methods


class PDFProcessor(DocumentProcessor):
    """PDF processor with validation and export."""

    def load(self, path):
        self.content = f"PDF from {path}"

    def validate(self):
        """Validate PDF structure."""
        return self.content is not None

    def export_to_json(self):
        """Export PDF metadata to JSON."""
        return {"type": "pdf", "content": self.content}

    def extract_text(self):
        """PDF-specific operation."""
        return "extracted text"


class WordProcessor(DocumentProcessor):
    """Word processor with validation and export."""

    def load(self, path):
        self.content = f"Word doc from {path}"

    def validate(self):
        """Validate Word document."""
        return self.content is not None

    def export_to_json(self):
        """Export Word metadata to JSON."""
        return {"type": "word", "content": self.content}

    def track_changes(self):
        """Word-specific operation."""
        return "tracking changes"


class ExcelProcessor(DocumentProcessor):
    """Excel processor with validation and export."""

    def load(self, path):
        self.content = f"Excel from {path}"

    def validate(self):
        """Validate Excel workbook."""
        return self.content is not None

    def export_to_json(self):
        """Export Excel data to JSON."""
        return {"type": "excel", "content": self.content}

    def calculate_formulas(self):
        """Excel-specific operation."""
        return "calculating formulas"


# Example 4: HTTP Handler missing common response methods
class HTTPHandler:
    """Base handler missing common HTTP operations."""

    def __init__(self):
        self.request = None

    def process_request(self, request):
        """Process incoming request."""
        self.request = request

    # Missing: send_response() and log_request()


class GETHandler(HTTPHandler):
    """GET request handler."""

    def send_response(self, data):
        """Send GET response."""
        return {"status": 200, "data": data}

    def log_request(self):
        """Log GET request."""
        return f"GET: {self.request}"

    def validate_cache(self):
        """GET-specific cache validation."""
        return True


class POSTHandler(HTTPHandler):
    """POST request handler."""

    def send_response(self, data):
        """Send POST response."""
        return {"status": 201, "data": data}

    def log_request(self):
        """Log POST request."""
        return f"POST: {self.request}"

    def validate_body(self):
        """POST-specific body validation."""
        return True


class PUTHandler(HTTPHandler):
    """PUT request handler."""

    def send_response(self, data):
        """Send PUT response."""
        return {"status": 200, "data": data}

    def log_request(self):
        """Log PUT request."""
        return f"PUT: {self.request}"

    def check_idempotency(self):
        """PUT-specific idempotency check."""
        return True


class DELETEHandler(HTTPHandler):
    """DELETE request handler."""

    def send_response(self, data):
        """Send DELETE response."""
        return {"status": 204, "data": data}

    def log_request(self):
        """Log DELETE request."""
        return f"DELETE: {self.request}"

    def verify_permissions(self):
        """DELETE-specific permission check."""
        return True


# Example 5: Database connector missing common operations
class DatabaseConnector:
    """Base connector missing common database operations."""

    def __init__(self, connection_string):
        self.connection_string = connection_string

    def connect(self):
        """Establish connection."""
        pass

    # Missing: execute_query() and begin_transaction()


class MySQLConnector(DatabaseConnector):
    """MySQL connector with common operations."""

    def execute_query(self, query):
        """Execute MySQL query."""
        return f"MySQL: {query}"

    def begin_transaction(self):
        """Start MySQL transaction."""
        return "BEGIN"

    def optimize_table(self, table):
        """MySQL-specific optimization."""
        return f"OPTIMIZE TABLE {table}"


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL connector with common operations."""

    def execute_query(self, query):
        """Execute PostgreSQL query."""
        return f"PostgreSQL: {query}"

    def begin_transaction(self):
        """Start PostgreSQL transaction."""
        return "START TRANSACTION"

    def vacuum(self, table):
        """PostgreSQL-specific vacuum."""
        return f"VACUUM {table}"


class MongoDBConnector(DatabaseConnector):
    """MongoDB connector with common operations."""

    def execute_query(self, query):
        """Execute MongoDB query."""
        return f"MongoDB: {query}"

    def begin_transaction(self):
        """Start MongoDB transaction."""
        return "session.startTransaction()"

    def create_index(self, collection):
        """MongoDB-specific indexing."""
        return f"db.{collection}.createIndex()"


# Example 6: UI Component missing render and handle_event
class UIComponent:
    """Base UI component missing common interface methods."""

    def __init__(self, id):
        self.id = id
        self.visible = True

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    # Missing: render() and handle_event()


class Button(UIComponent):
    """Button with render and event handling."""

    def __init__(self, id, label):
        super().__init__(id)
        self.label = label

    def render(self):
        """Render button."""
        return f"<button id='{self.id}'>{self.label}</button>"

    def handle_event(self, event):
        """Handle button events."""
        if event == "click":
            return "button_clicked"
        return None


class TextInput(UIComponent):
    """Text input with render and event handling."""

    def __init__(self, id, placeholder):
        super().__init__(id)
        self.placeholder = placeholder

    def render(self):
        """Render text input."""
        return f"<input id='{self.id}' placeholder='{self.placeholder}'/>"

    def handle_event(self, event):
        """Handle input events."""
        if event == "change":
            return "text_changed"
        return None


class Dropdown(UIComponent):
    """Dropdown with render and event handling."""

    def __init__(self, id, options):
        super().__init__(id)
        self.options = options

    def render(self):
        """Render dropdown."""
        options_html = "".join([f"<option>{o}</option>" for o in self.options])
        return f"<select id='{self.id}'>{options_html}</select>"

    def handle_event(self, event):
        """Handle dropdown events."""
        if event == "select":
            return "option_selected"
        return None


class CheckBox(UIComponent):
    """Checkbox with render and event handling."""

    def __init__(self, id, label):
        super().__init__(id)
        self.label = label

    def render(self):
        """Render checkbox."""
        return f"<input type='checkbox' id='{self.id}'/><label>{self.label}</label>"

    def handle_event(self, event):
        """Handle checkbox events."""
        if event == "toggle":
            return "checkbox_toggled"
        return None


if __name__ == "__main__":
    print("Unify Interfaces test cases loaded")
    print("This file contains 6 examples of class hierarchies where:")
    print("- Subclasses have common methods that the superclass lacks")
    print("- These methods could be added to the superclass to unify interfaces")
    print("\nExamples:")
    print("1. Animal hierarchy - missing make_sound()")
    print("2. Shape hierarchy - missing calculate_area() and calculate_perimeter()")
    print("3. DocumentProcessor hierarchy - missing validate() and export_to_json()")
    print("4. HTTPHandler hierarchy - missing send_response() and log_request()")
    print("5. DatabaseConnector hierarchy - missing execute_query() and begin_transaction()")
    print("6. UIComponent hierarchy - missing render() and handle_event()")