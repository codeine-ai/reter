"""Test file for Encapsulate Composite With Builder pattern detection."""


# ===== Pattern Example 1: XML/HTML Tag Builder (Should be flagged - HIGH) =====

class Tag:
    """XML/HTML tag that can contain child tags and attributes."""

    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.children = []
        self.text_content = None

    def add_attribute(self, key, value):
        """Add an attribute to the tag."""
        self.attributes[key] = value

    def add_child(self, child):
        """Add a child tag."""
        self.children.append(child)

    def add_text(self, text):
        """Add text content."""
        self.text_content = text

    def append_child(self, tag):
        """Append a child tag."""
        self.children.append(tag)

    def insert_child(self, index, tag):
        """Insert a child at specific position."""
        self.children.insert(index, tag)

    def register_namespace(self, prefix, uri):
        """Register XML namespace."""
        self.attributes[f"xmlns:{prefix}"] = uri

    def to_xml(self):
        """Convert to XML string."""
        # Complex rendering logic here
        pass


# ===== Pattern Example 2: Document Builder (Should be flagged - MEDIUM) =====

class Document:
    """Document that contains sections and metadata."""

    def __init__(self, title):
        self.title = title
        self.sections = []
        self.metadata = {}

    def add_section(self, section):
        """Add a section to the document."""
        self.sections.append(section)

    def append_paragraph(self, text):
        """Append a paragraph."""
        if not self.sections:
            self.sections.append([])
        self.sections[-1].append(text)

    def add_metadata(self, key, value):
        """Add metadata."""
        self.metadata[key] = value


# ===== Pattern Example 3: Menu System (Should be flagged - MEDIUM) =====

class Menu:
    """Menu that can contain items and submenus."""

    def __init__(self, title):
        self.title = title
        self.items = []
        self.submenus = []

    def add_item(self, item):
        """Add a menu item."""
        self.items.append(item)

    def add_submenu(self, submenu):
        """Add a submenu."""
        self.submenus.append(submenu)

    def insert_separator(self, index):
        """Insert a separator."""
        self.items.insert(index, "---")

    def register_shortcut(self, item, keys):
        """Register keyboard shortcut."""
        # Implementation
        pass


# ===== Client Code (Complex Construction - Anti-pattern) =====

def build_complex_document():
    """Client code with repetitive construction - should use builder."""
    doc = Document("Annual Report")
    doc.add_metadata("author", "John Doe")
    doc.add_metadata("date", "2024-01-01")
    doc.add_metadata("version", "1.0")

    doc.add_section("Introduction")
    doc.append_paragraph("First paragraph...")
    doc.append_paragraph("Second paragraph...")

    doc.add_section("Financial Overview")
    doc.append_paragraph("Revenue increased...")
    doc.append_paragraph("Expenses decreased...")

    doc.add_section("Conclusion")
    doc.append_paragraph("In summary...")

    return doc


def build_complex_menu():
    """Another example of complex construction."""
    menu = Menu("File")
    menu.add_item("New")
    menu.add_item("Open")
    menu.add_item("Save")
    menu.insert_separator(3)
    menu.add_item("Exit")

    edit_menu = Menu("Edit")
    edit_menu.add_item("Cut")
    edit_menu.add_item("Copy")
    edit_menu.add_item("Paste")

    menu.add_submenu(edit_menu)
    menu.register_shortcut("New", "Ctrl+N")
    menu.register_shortcut("Open", "Ctrl+O")
    menu.register_shortcut("Save", "Ctrl+S")

    return menu


def build_complex_xml():
    """XML construction without builder - repetitive and error-prone."""
    root = Tag("html")
    root.add_attribute("lang", "en")
    root.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

    head = Tag("head")
    title = Tag("title")
    title.add_text("My Page")
    head.add_child(title)

    meta1 = Tag("meta")
    meta1.add_attribute("charset", "UTF-8")
    head.add_child(meta1)

    meta2 = Tag("meta")
    meta2.add_attribute("name", "viewport")
    meta2.add_attribute("content", "width=device-width")
    head.add_child(meta2)

    root.add_child(head)

    body = Tag("body")
    body.add_attribute("class", "main")

    header = Tag("header")
    h1 = Tag("h1")
    h1.add_text("Welcome")
    header.add_child(h1)
    body.add_child(header)

    root.add_child(body)

    return root


# ===== Example of Good Design (Already has builder) =====

class QueryBuilder:
    """SQL Query builder with fluent interface - good example."""

    def __init__(self):
        self.query_parts = {
            "select": [],
            "from": None,
            "where": [],
            "order_by": []
        }

    def select(self, *fields):
        """Add SELECT fields."""
        self.query_parts["select"].extend(fields)
        return self

    def from_table(self, table):
        """Set FROM table."""
        self.query_parts["from"] = table
        return self

    def where(self, condition):
        """Add WHERE condition."""
        self.query_parts["where"].append(condition)
        return self

    def order_by(self, field, direction="ASC"):
        """Add ORDER BY."""
        self.query_parts["order_by"].append(f"{field} {direction}")
        return self

    def build(self):
        """Build the final query."""
        # Build query string
        return "SELECT ..."


def use_query_builder():
    """Good example - using builder pattern."""
    query = (QueryBuilder()
             .select("id", "name", "email")
             .from_table("users")
             .where("active = 1")
             .where("age > 18")
             .order_by("name")
             .build())

    return query


# ===== Simple Class (Should NOT be flagged) =====

class SimpleList:
    """Simple class with just append - too simple for builder."""

    def __init__(self):
        self.items = []

    def append(self, item):
        """Add an item."""
        self.items.append(item)


# ===== Component Tree (Should be flagged - HIGH) =====

class Component:
    """UI Component that forms a tree structure."""

    def __init__(self, type_name, id_val=None):
        self.type = type_name
        self.id = id_val
        self.children = []
        self.properties = {}
        self.event_handlers = {}
        self.styles = {}

    def add_child(self, component):
        """Add child component."""
        self.children.append(component)
        return self  # Fluent interface

    def add_property(self, name, value):
        """Add a property."""
        self.properties[name] = value
        return self

    def add_style(self, name, value):
        """Add CSS style."""
        self.styles[name] = value
        return self

    def add_event_handler(self, event, handler):
        """Add event handler."""
        self.event_handlers[event] = handler
        return self

    def append_children(self, *components):
        """Append multiple children."""
        self.children.extend(components)
        return self

    def insert_child_at(self, index, component):
        """Insert child at index."""
        self.children.insert(index, component)
        return self


def build_ui_tree():
    """Complex UI construction - needs builder."""
    root = Component("div", "app")
    root.add_style("margin", "10px")
    root.add_style("padding", "20px")

    header = Component("header")
    header.add_style("background", "blue")
    header.add_child(
        Component("h1").add_property("text", "Title")
    )

    nav = Component("nav")
    nav.add_child(Component("a").add_property("href", "/home"))
    nav.add_child(Component("a").add_property("href", "/about"))
    nav.add_child(Component("a").add_property("href", "/contact"))

    header.add_child(nav)
    root.add_child(header)

    main_content = Component("main")
    main_content.add_style("flex", "1")

    root.add_child(main_content)

    return root