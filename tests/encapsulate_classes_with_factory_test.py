"""Test file for Encapsulate Classes With Factory pattern detection."""

from abc import ABC, abstractmethod


# ===== Pattern Example 1: Descriptor Family (Should be flagged) =====

class AttributeDescriptor(ABC):
    """Base descriptor class."""

    @abstractmethod
    def to_string(self):
        pass


class BooleanDescriptor(AttributeDescriptor):
    """Descriptor for boolean attributes."""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_string(self):
        return f"{self.name}: {self.value}"


class NumberDescriptor(AttributeDescriptor):
    """Descriptor for numeric attributes."""

    def __init__(self, name, value, min_val=None, max_val=None):
        self.name = name
        self.value = value
        self.min_val = min_val
        self.max_val = max_val

    def to_string(self):
        return f"{self.name}: {self.value} ({self.min_val}-{self.max_val})"


class StringDescriptor(AttributeDescriptor):
    """Descriptor for string attributes."""

    def __init__(self, name, value, max_length=None):
        self.name = name
        self.value = value
        self.max_length = max_length

    def to_string(self):
        return f"{self.name}: {self.value}"


# ===== Pattern Example 2: Handler Family (Should be flagged) =====

class MessageHandler(ABC):
    """Base handler for messages."""

    @abstractmethod
    def handle(self, message):
        pass


class EmailHandler(MessageHandler):
    """Handles email messages."""

    def __init__(self, smtp_server, port):
        self.smtp_server = smtp_server
        self.port = port

    def handle(self, message):
        print(f"Sending email via {self.smtp_server}:{self.port}")


class SMSHandler(MessageHandler):
    """Handles SMS messages."""

    def __init__(self, api_key, gateway):
        self.api_key = api_key
        self.gateway = gateway

    def handle(self, message):
        print(f"Sending SMS via {self.gateway}")


class PushHandler(MessageHandler):
    """Handles push notifications."""

    def __init__(self, service_url, api_token):
        self.service_url = service_url
        self.api_token = api_token

    def handle(self, message):
        print(f"Sending push to {self.service_url}")


# ===== Client Code (Direct Instantiation) =====

def create_descriptors():
    """Client code that directly instantiates descriptor classes."""
    # These should be created via factory instead
    bool_desc = BooleanDescriptor("enabled", True)
    num_desc = NumberDescriptor("age", 25, 0, 120)
    str_desc = StringDescriptor("name", "John", 100)

    return [bool_desc, num_desc, str_desc]


def setup_notification_handlers():
    """Client code that directly instantiates handler classes."""
    # These should be created via factory instead
    email = EmailHandler("smtp.example.com", 587)
    sms = SMSHandler("api-key-123", "twilio")
    push = PushHandler("https://push.example.com", "token-456")

    return [email, sms, push]


def send_notifications(message):
    """More client code with direct instantiation."""
    handlers = [
        EmailHandler("smtp.gmail.com", 465),
        SMSHandler("key-789", "nexmo"),
        PushHandler("https://firebase.com", "firebase-token"),
    ]

    for handler in handlers:
        handler.handle(message)


# ===== Example of Good Design (Already has factory) =====

class Command(ABC):
    """Base command class."""

    @abstractmethod
    def execute(self):
        pass


class SaveCommand(Command):
    """Command for saving."""

    def __init__(self, data):
        self.data = data

    def execute(self):
        print(f"Saving: {self.data}")


class LoadCommand(Command):
    """Command for loading."""

    def __init__(self, source):
        self.source = source

    def execute(self):
        print(f"Loading from: {self.source}")


class CommandFactory:
    """Factory for creating commands (good pattern example)."""

    @staticmethod
    def create_save_command(data):
        return SaveCommand(data)

    @staticmethod
    def create_load_command(source):
        return LoadCommand(source)


def use_commands_properly():
    """Client code using factory (good example)."""
    save_cmd = CommandFactory.create_save_command("my data")
    load_cmd = CommandFactory.create_load_command("file.txt")

    save_cmd.execute()
    load_cmd.execute()
