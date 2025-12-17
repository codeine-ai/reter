"""
Test cases for Introduce Null Object pattern detection.

Demonstrates duplicated null/None checking logic that could be replaced with Null Objects.
"""

# Example 1: Logger with repeated None checks
class Application:
    """Application with optional logger that's checked frequently."""

    def __init__(self, logger=None):
        self.logger = logger
        self.data = []

    def process_data(self, data):
        """Process data with optional logging."""
        if self.logger is not None:
            self.logger.info("Starting data processing")

        try:
            self.data = self._transform_data(data)
            if self.logger is not None:
                self.logger.info(f"Processed {len(self.data)} items")
        except Exception as e:
            if self.logger is not None:
                self.logger.error(f"Error processing data: {e}")
            raise

    def save_results(self):
        """Save results with optional logging."""
        if self.logger is not None:
            self.logger.info("Saving results")

        # Save logic here
        saved = True

        if self.logger is not None:
            self.logger.info("Results saved successfully")

        return saved

    def validate_data(self):
        """Validate data with optional logging."""
        if self.logger is not None:
            self.logger.debug("Validating data")

        errors = []
        for item in self.data:
            if not self._is_valid(item):
                errors.append(item)
                if self.logger is not None:
                    self.logger.warning(f"Invalid item: {item}")

        if self.logger is not None:
            self.logger.info(f"Validation complete: {len(errors)} errors")

        return errors

    def cleanup(self):
        """Cleanup with optional logging."""
        if self.logger is not None:
            self.logger.info("Starting cleanup")

        self.data.clear()

        if self.logger is not None:
            self.logger.info("Cleanup complete")

    def _transform_data(self, data):
        """Transform data."""
        return [d.upper() for d in data]

    def _is_valid(self, item):
        """Check if item is valid."""
        return len(item) > 0


# Example 2: Notification system with optional notifier
class OrderProcessor:
    """Process orders with optional notification service."""

    def __init__(self, notifier=None):
        self.notifier = notifier
        self.orders = []

    def create_order(self, customer, items):
        """Create order with optional notification."""
        order = {"customer": customer, "items": items, "status": "pending"}
        self.orders.append(order)

        if self.notifier is not None:
            self.notifier.send(f"Order created for {customer}")

        return order

    def process_order(self, order_id):
        """Process order with optional notification."""
        order = self.orders[order_id]

        if self.notifier is not None:
            self.notifier.send(f"Processing order {order_id}")

        # Process the order
        order["status"] = "processing"

        if self.notifier is not None:
            self.notifier.send(f"Order {order_id} is being processed")

    def ship_order(self, order_id):
        """Ship order with optional notification."""
        order = self.orders[order_id]

        if self.notifier is not None:
            self.notifier.send(f"Shipping order {order_id}")

        order["status"] = "shipped"

        if self.notifier is not None:
            self.notifier.send(f"Order {order_id} has been shipped")

    def cancel_order(self, order_id):
        """Cancel order with optional notification."""
        order = self.orders[order_id]

        if self.notifier is not None:
            self.notifier.send(f"Cancelling order {order_id}")

        order["status"] = "cancelled"

        if self.notifier is not None:
            self.notifier.send(f"Order {order_id} has been cancelled")

    def complete_order(self, order_id):
        """Complete order with optional notification."""
        order = self.orders[order_id]
        order["status"] = "completed"

        if self.notifier is not None:
            self.notifier.send(f"Order {order_id} completed successfully")


# Example 3: Cache system with optional cache
class DataService:
    """Data service with optional caching."""

    def __init__(self, cache=None, database=None):
        self.cache = cache
        self.database = database

    def get_user(self, user_id):
        """Get user with optional cache check."""
        # Check cache first
        if self.cache is not None:
            cached_user = self.cache.get(f"user_{user_id}")
            if cached_user:
                return cached_user

        # Get from database
        if self.database is not None:
            user = self.database.find_user(user_id)
        else:
            user = {"id": user_id, "name": "Unknown"}

        # Store in cache
        if self.cache is not None and user:
            self.cache.set(f"user_{user_id}", user)

        return user

    def get_product(self, product_id):
        """Get product with optional cache check."""
        # Check cache first
        if self.cache is not None:
            cached_product = self.cache.get(f"product_{product_id}")
            if cached_product:
                return cached_product

        # Get from database
        if self.database is not None:
            product = self.database.find_product(product_id)
        else:
            product = {"id": product_id, "name": "Unknown Product"}

        # Store in cache
        if self.cache is not None and product:
            self.cache.set(f"product_{product_id}", product)

        return product

    def get_order(self, order_id):
        """Get order with optional cache check."""
        # Check cache first
        if self.cache is not None:
            cached_order = self.cache.get(f"order_{order_id}")
            if cached_order:
                return cached_order

        # Get from database
        if self.database is not None:
            order = self.database.find_order(order_id)
        else:
            order = {"id": order_id, "status": "unknown"}

        # Store in cache
        if self.cache is not None and order:
            self.cache.set(f"order_{order_id}", order)

        return order

    def invalidate_user(self, user_id):
        """Invalidate user cache entry."""
        if self.cache is not None:
            self.cache.delete(f"user_{user_id}")

    def invalidate_all(self):
        """Clear all cache entries."""
        if self.cache is not None:
            self.cache.clear()


# Example 4: File handler with optional error handler
class FileProcessor:
    """Process files with optional error handler."""

    def __init__(self, error_handler=None):
        self.error_handler = error_handler
        self.files_processed = []

    def process_file(self, filepath):
        """Process a file with error handling."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            self.files_processed.append(filepath)
            return content
        except FileNotFoundError:
            if self.error_handler is not None:
                self.error_handler.handle_error(f"File not found: {filepath}")
            return None
        except PermissionError:
            if self.error_handler is not None:
                self.error_handler.handle_error(f"Permission denied: {filepath}")
            return None
        except Exception as e:
            if self.error_handler is not None:
                self.error_handler.handle_error(f"Error reading {filepath}: {e}")
            return None

    def write_file(self, filepath, content):
        """Write to a file with error handling."""
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        except PermissionError:
            if self.error_handler is not None:
                self.error_handler.handle_error(f"Cannot write to {filepath}")
            return False
        except Exception as e:
            if self.error_handler is not None:
                self.error_handler.handle_error(f"Error writing {filepath}: {e}")
            return False

    def delete_file(self, filepath):
        """Delete a file with error handling."""
        try:
            import os
            os.remove(filepath)
            return True
        except FileNotFoundError:
            if self.error_handler is not None:
                self.error_handler.handle_error(f"Cannot delete, file not found: {filepath}")
            return False
        except Exception as e:
            if self.error_handler is not None:
                self.error_handler.handle_error(f"Error deleting {filepath}: {e}")
            return False

    def backup_file(self, filepath):
        """Backup a file with error handling."""
        try:
            import shutil
            backup_path = f"{filepath}.backup"
            shutil.copy(filepath, backup_path)
            return backup_path
        except Exception as e:
            if self.error_handler is not None:
                self.error_handler.handle_error(f"Error backing up {filepath}: {e}")
            return None


# Example 5: Configuration manager with optional validator
class ConfigManager:
    """Manage configuration with optional validator."""

    def __init__(self, validator=None):
        self.validator = validator
        self.config = {}

    def load_config(self, config_dict):
        """Load configuration with optional validation."""
        if self.validator is not None:
            if not self.validator.validate(config_dict):
                raise ValueError("Invalid configuration")

        self.config = config_dict

        if self.validator is not None:
            self.validator.log_validation("Configuration loaded successfully")

    def get_value(self, key, default=None):
        """Get configuration value with optional validation."""
        if self.validator is not None:
            if not self.validator.is_valid_key(key):
                return default

        return self.config.get(key, default)

    def set_value(self, key, value):
        """Set configuration value with optional validation."""
        if self.validator is not None:
            if not self.validator.validate_value(key, value):
                raise ValueError(f"Invalid value for {key}")

        self.config[key] = value

        if self.validator is not None:
            self.validator.log_change(key, value)

    def remove_value(self, key):
        """Remove configuration value with optional validation."""
        if self.validator is not None:
            if not self.validator.can_remove(key):
                return False

        if key in self.config:
            del self.config[key]

            if self.validator is not None:
                self.validator.log_removal(key)

            return True
        return False

    def validate_all(self):
        """Validate all configuration values."""
        if self.validator is not None:
            return self.validator.validate_all(self.config)
        return True


# Example 6: Event system with optional listeners
class EventManager:
    """Manage events with optional listener checking."""

    def __init__(self):
        self.listeners = {}

    def emit(self, event_name, data=None):
        """Emit event to listeners if they exist."""
        listener = self.listeners.get(event_name)

        if listener is not None:
            listener.handle(event_name, data)

        # Also check for wildcard listener
        wildcard = self.listeners.get("*")
        if wildcard is not None:
            wildcard.handle(event_name, data)

    def on(self, event_name, listener):
        """Register event listener."""
        self.listeners[event_name] = listener

    def off(self, event_name):
        """Remove event listener."""
        listener = self.listeners.get(event_name)

        if listener is not None:
            listener.cleanup()
            del self.listeners[event_name]

    def emit_error(self, error):
        """Emit error event."""
        error_listener = self.listeners.get("error")

        if error_listener is not None:
            error_listener.handle_error(error)

    def emit_warning(self, warning):
        """Emit warning event."""
        warning_listener = self.listeners.get("warning")

        if warning_listener is not None:
            warning_listener.handle_warning(warning)


# Test function
def test_null_object_opportunities():
    """Test that demonstrates null object opportunities."""
    # The classes above show multiple examples of the Introduce Null Object pattern:

    # 1. Application class has 5 methods checking if self.logger is not None
    #    Could use a NullLogger that implements the logger interface with no-op methods

    # 2. OrderProcessor has 5 methods checking if self.notifier is not None
    #    Could use a NullNotifier that silently ignores notifications

    # 3. DataService repeatedly checks self.cache and self.database for None
    #    Could use NullCache and NullDatabase objects

    # 4. FileProcessor checks self.error_handler in multiple error cases
    #    Could use a NullErrorHandler

    # 5. ConfigManager checks self.validator throughout the code
    #    Could use a NullValidator that always returns valid

    # 6. EventManager checks for None listeners before calling them
    #    Could use NullListener objects

    print("Introduce Null Object test cases loaded successfully")
    return True


if __name__ == "__main__":
    test_null_object_opportunities()