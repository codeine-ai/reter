"""
Test cases for Inline Singleton pattern detection.

This file contains examples of singleton classes that don't need
global access and could be inlined into the classes that use them.
"""

# Example 1: Classic singleton used by only one class
class DatabaseConnection:
    """Singleton used by only one repository."""
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if DatabaseConnection._instance is not None:
            raise Exception("Singleton instance already exists")
        self.connection_string = "database://localhost"

    def execute_query(self, query):
        return f"Executing: {query}"


class UserRepository:
    """Only class that uses DatabaseConnection singleton."""

    def __init__(self):
        self.db = DatabaseConnection.getInstance()

    def find_user(self, user_id):
        return self.db.execute_query(f"SELECT * FROM users WHERE id={user_id}")


# Example 2: Unused singleton (can be removed)
class ConfigurationManager:
    """Singleton that is never actually used."""
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.settings = {}

    def get_setting(self, key):
        return self.settings.get(key)


# Example 3: Simple singleton with low complexity
class Logger:
    """Simple singleton with minimal functionality."""
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def log(self, message):
        print(f"[LOG] {message}")


class ServiceA:
    """Uses the logger singleton."""

    def __init__(self):
        self.logger = Logger.instance()

    def process(self):
        self.logger.log("Processing in ServiceA")


class ServiceB:
    """Also uses the logger singleton."""

    def __init__(self):
        self.logger = Logger.instance()

    def handle(self):
        self.logger.log("Handling in ServiceB")


# Example 4: Complex singleton (should probably remain)
class ApplicationContext:
    """Complex singleton with many methods and state."""
    _instance = None
    _shared_instance = None  # Alternative instance attribute

    @classmethod
    def shared(cls):
        if cls._shared_instance is None:
            cls._shared_instance = cls()
        return cls._shared_instance

    def __init__(self):
        self.services = {}
        self.repositories = {}
        self.configurations = {}
        self.cache = {}
        self.event_bus = None
        self.security_context = None

    def register_service(self, name, service):
        self.services[name] = service

    def get_service(self, name):
        return self.services.get(name)

    def register_repository(self, name, repo):
        self.repositories[name] = repo

    def get_repository(self, name):
        return self.repositories.get(name)

    def configure(self, config):
        self.configurations.update(config)

    def get_config(self, key):
        return self.configurations.get(key)

    def cache_value(self, key, value):
        self.cache[key] = value

    def get_cached(self, key):
        return self.cache.get(key)

    def publish_event(self, event):
        if self.event_bus:
            self.event_bus.publish(event)

    def set_security_context(self, context):
        self.security_context = context

    def check_permission(self, permission):
        if self.security_context:
            return self.security_context.has_permission(permission)
        return False


# Many classes use ApplicationContext
class OrderService:
    def __init__(self):
        self.context = ApplicationContext.shared()

class PaymentService:
    def __init__(self):
        self.context = ApplicationContext.shared()

class ShippingService:
    def __init__(self):
        self.context = ApplicationContext.shared()

class InventoryService:
    def __init__(self):
        self.context = ApplicationContext.shared()

class NotificationService:
    def __init__(self):
        self.context = ApplicationContext.shared()


# Example 5: Thread-safe singleton (attribute-based)
class ThreadSafeCache:
    """Singleton with thread safety considerations."""
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.cache_data = {}
        return cls.__instance

    def get(self, key):
        return self.cache_data.get(key)

    def set(self, key, value):
        self.cache_data[key] = value


class CacheUser:
    """Single user of the thread-safe cache."""

    def __init__(self):
        self.cache = ThreadSafeCache()

    def store_data(self, key, value):
        self.cache.set(key, value)


# Example 6: Enum-style singleton (Python's default pattern)
class StatusCodes:
    """Singleton for status codes - but really should be an Enum."""
    INSTANCE = None

    @classmethod
    def default(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = cls()
        return cls.INSTANCE

    def __init__(self):
        self.SUCCESS = 200
        self.NOT_FOUND = 404
        self.ERROR = 500


class APIHandler:
    """Uses status codes singleton."""

    def __init__(self):
        self.status = StatusCodes.default()

    def handle_request(self):
        return self.status.SUCCESS


# Example 7: Factory singleton (medium complexity)
class WidgetFactory:
    """Singleton factory with moderate complexity."""
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.widget_types = {}
        self.default_config = {}

    def register_widget(self, name, widget_class):
        self.widget_types[name] = widget_class

    def create_widget(self, widget_type):
        if widget_type in self.widget_types:
            return self.widget_types[widget_type]()
        return None

    def set_default_config(self, config):
        self.default_config = config


class UIBuilder:
    """Uses the widget factory."""

    def __init__(self):
        self.factory = WidgetFactory.getInstance()

    def build_ui(self):
        button = self.factory.create_widget("button")
        return button


class FormBuilder:
    """Also uses the widget factory."""

    def __init__(self):
        self.factory = WidgetFactory.getInstance()

    def build_form(self):
        input_field = self.factory.create_widget("input")
        return input_field


# Counter-example: Not a singleton (for comparison)
class RegularService:
    """Regular class, not a singleton."""

    def __init__(self):
        self.data = []

    def add_data(self, item):
        self.data.append(item)


# Example 8: Resource manager singleton
class ResourceManager:
    """Singleton managing limited resources."""
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.resources = []
        self.pool_size = 10

    def acquire_resource(self):
        if len(self.resources) < self.pool_size:
            resource = f"Resource_{len(self.resources)}"
            self.resources.append(resource)
            return resource
        return None

    def release_resource(self, resource):
        if resource in self.resources:
            self.resources.remove(resource)


class ResourceConsumerA:
    """Uses resource manager."""

    def __init__(self):
        self.manager = ResourceManager.get_instance()

    def use_resource(self):
        resource = self.manager.acquire_resource()
        # Use resource
        self.manager.release_resource(resource)


class ResourceConsumerB:
    """Also uses resource manager."""

    def __init__(self):
        self.manager = ResourceManager.get_instance()

    def process_with_resource(self):
        resource = self.manager.acquire_resource()
        # Process with resource
        self.manager.release_resource(resource)


class ResourceConsumerC:
    """Third user of resource manager."""

    def __init__(self):
        self.manager = ResourceManager.get_instance()

    def handle_with_resource(self):
        resource = self.manager.acquire_resource()
        # Handle with resource
        self.manager.release_resource(resource)