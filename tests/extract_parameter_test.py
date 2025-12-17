"""
Test cases for Extract Parameter pattern detection.

This file contains examples where methods/constructors create objects locally
and assign them to fields - opportunities for dependency injection.
"""

# Example 1: Service class with hardcoded dependencies in __init__
class PaymentService:
    """Service with hardcoded dependencies that should be parameterized."""

    def __init__(self):
        # These should be parameters instead of hardcoded instantiations
        self.logger = Logger()
        self.validator = PaymentValidator()
        self.client = PaymentGatewayClient()
        self.cache = CacheManager()

    def process_payment(self, amount, card_number):
        self.logger.log("Processing payment")
        if self.validator.validate(card_number):
            return self.client.charge(amount, card_number)
        return False


# Example 2: Controller with multiple hardcoded services
class OrderController:
    """Controller creating multiple services internally."""

    def __init__(self, config):
        self.config = config
        # Multiple hardcoded instantiations
        self.order_service = OrderService()
        self.inventory_service = InventoryService()
        self.notification_service = NotificationService()
        self.shipping_handler = ShippingHandler()

    def create_order(self, items, user_id):
        # Process order
        pass

    def setup_monitoring(self):
        # Another method creating dependencies
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()


# Example 3: Repository with hardcoded connection
class UserRepository:
    """Repository with hardcoded database connection."""

    def __init__(self):
        # Database connection should be injected
        self.connection = DatabaseConnection("production")
        self.query_builder = QueryBuilder()

    def find_user(self, user_id):
        return self.connection.execute(
            self.query_builder.select("users", user_id)
        )


# Example 4: Manager class with factory creation
class TaskManager:
    """Manager creating internal components."""

    def __init__(self, name):
        self.name = name
        # These could be parameterized for flexibility
        self.queue = TaskQueue()
        self.executor = TaskExecutor()
        self.scheduler = TaskScheduler()

    def initialize_workers(self):
        # Method creating more dependencies
        self.worker_pool = WorkerPool(size=10)
        self.monitor = TaskMonitor()


# Example 5: Mixed - some parameters, some hardcoded (partial application)
class EmailService:
    """Service with mixed parameterization."""

    def __init__(self, smtp_config):
        self.smtp_config = smtp_config
        # These should also be parameters
        self.template_engine = TemplateEngine()
        self.validator = EmailValidator()
        self.rate_limiter = RateLimiter()

    def send_email(self, to, subject, body):
        # Send email logic
        pass


# Example 6: Builder with internal factories
class ReportBuilder:
    """Builder creating internal components."""

    def __init__(self):
        # Multiple hardcoded components
        self.data_fetcher = DataFetcher()
        self.formatter = ReportFormatter()
        self.exporter = ReportExporter()

    def set_format(self, format_type):
        # Method also creating dependencies
        if format_type == "pdf":
            self.pdf_renderer = PDFRenderer()
        elif format_type == "excel":
            self.excel_renderer = ExcelRenderer()


# Example 7: Adapter with hardcoded adaptee
class PaymentAdapter:
    """Adapter creating its adaptee internally."""

    def __init__(self):
        # Adaptee should be injected
        self.legacy_payment_system = LegacyPaymentSystem()
        self.error_handler = PaymentErrorHandler()

    def charge(self, amount, account):
        try:
            return self.legacy_payment_system.process(amount, account)
        except Exception as e:
            self.error_handler.handle(e)


# Example 8: Complex initialization with many dependencies
class ApplicationContext:
    """Application context with many hardcoded dependencies."""

    def __init__(self):
        # Many hardcoded dependencies - high severity
        self.config_loader = ConfigLoader()
        self.database_manager = DatabaseManager()
        self.cache_manager = CacheManager()
        self.security_manager = SecurityManager()
        self.event_bus = EventBus()
        self.logger_factory = LoggerFactory()

    def initialize_plugins(self):
        # More dependencies created in method
        self.plugin_loader = PluginLoader()
        self.plugin_registry = PluginRegistry()


# Counter-example: Properly parameterized class
class ProperlyInjectedService:
    """Good example with dependency injection."""

    def __init__(self, logger, validator, client):
        # Dependencies are injected, not created
        self.logger = logger
        self.validator = validator
        self.client = client

    def process(self, data):
        self.logger.log("Processing")
        if self.validator.validate(data):
            return self.client.send(data)


# Example 9: Test class with hardcoded mocks (common anti-pattern)
class PaymentServiceTest:
    """Test class with hardcoded test doubles."""

    def __init__(self):
        # Test doubles should be parameterized for flexibility
        self.mock_gateway = MockPaymentGateway()
        self.stub_validator = StubValidator()
        self.fake_logger = FakeLogger()

    def test_payment_success(self):
        service = PaymentService()
        # Test logic
        pass


# Helper classes referenced above (minimal implementations)
class Logger:
    pass

class PaymentValidator:
    pass

class PaymentGatewayClient:
    pass

class CacheManager:
    pass

class OrderService:
    pass

class InventoryService:
    pass

class NotificationService:
    pass

class ShippingHandler:
    pass

class MetricsCollector:
    pass

class AlertManager:
    pass

class DatabaseConnection:
    def __init__(self, env):
        self.env = env

class QueryBuilder:
    pass

class TaskQueue:
    pass

class TaskExecutor:
    pass

class TaskScheduler:
    pass

class WorkerPool:
    def __init__(self, size):
        self.size = size

class TaskMonitor:
    pass

class TemplateEngine:
    pass

class EmailValidator:
    pass

class RateLimiter:
    pass

class DataFetcher:
    pass

class ReportFormatter:
    pass

class ReportExporter:
    pass

class PDFRenderer:
    pass

class ExcelRenderer:
    pass

class LegacyPaymentSystem:
    pass

class PaymentErrorHandler:
    pass

class ConfigLoader:
    pass

class DatabaseManager:
    pass

class SecurityManager:
    pass

class EventBus:
    pass

class LoggerFactory:
    pass

class PluginLoader:
    pass

class PluginRegistry:
    pass

class MockPaymentGateway:
    pass

class StubValidator:
    pass

class FakeLogger:
    pass