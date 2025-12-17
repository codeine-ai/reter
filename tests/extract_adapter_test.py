"""Test file for Extract Adapter pattern detection."""

import json
from typing import Any, Dict


# ===== Pattern Example 1: API Client with Multiple Versions (Should be flagged - HIGH) =====

class APIClient:
    """API client handling multiple API versions - needs adapter extraction."""

    def __init__(self, version="v3"):
        self.version = version
        self.api_version = version
        self.base_url = f"https://api.example.com/{version}"

    def get_user_v1(self, user_id):
        """Get user using v1 API."""
        # v1 specific implementation
        return {"id": user_id, "version": "v1"}

    def get_user_v2(self, user_id):
        """Get user using v2 API with enhanced fields."""
        # v2 specific implementation
        return {"id": user_id, "version": "v2", "enhanced": True}

    def get_user_v3(self, user_id):
        """Get user using v3 API with full details."""
        # v3 specific implementation
        return {"id": user_id, "version": "v3", "full": True}

    def process_response_v1(self, response):
        """Process v1 API response format."""
        # v1 response processing
        return json.loads(response)

    def process_response_v2(self, response):
        """Process v2 API response format."""
        # v2 response processing with different structure
        data = json.loads(response)
        return self._transform_v2_data(data)

    def process_response_v3(self, response):
        """Process v3 API response format."""
        # v3 response processing
        data = json.loads(response)
        return self._transform_v3_data(data)

    def _transform_v2_data(self, data):
        """Transform v2 data structure."""
        return data

    def _transform_v3_data(self, data):
        """Transform v3 data structure."""
        return data


# ===== Pattern Example 2: Database Adapter (Should be flagged - HIGH) =====

class DatabaseAdapter:
    """Database adapter supporting multiple database versions."""

    def __init__(self, db_version):
        self.db_version = db_version
        self.connection = None

    def connect_legacy(self, **kwargs):
        """Connect to legacy database."""
        # Legacy connection logic
        pass

    def connect_v1(self, **kwargs):
        """Connect to v1 database."""
        # v1 connection logic
        pass

    def connect_v2(self, **kwargs):
        """Connect to v2 database."""
        # v2 connection logic
        pass

    def query_legacy(self, sql):
        """Execute query on legacy database."""
        # Legacy query execution
        return []

    def query_v1(self, sql):
        """Execute query on v1 database."""
        # v1 query execution
        return []

    def query_v2(self, sql):
        """Execute query on v2 database."""
        # v2 query execution with new features
        return []

    def handle_error_legacy(self, error):
        """Handle legacy database errors."""
        pass

    def handle_error_v1(self, error):
        """Handle v1 database errors."""
        pass

    def handle_error_v2(self, error):
        """Handle v2 database errors."""
        pass


# ===== Pattern Example 3: SDK Wrapper (Should be flagged - MEDIUM) =====

class SDKWrapper:
    """Wrapper for third-party SDK with version handling."""

    def __init__(self, sdk_version="2.0"):
        self.sdk_version = sdk_version

    def initialize_sdk_v1(self):
        """Initialize SDK version 1."""
        # v1 initialization
        pass

    def initialize_sdk_v2(self):
        """Initialize SDK version 2."""
        # v2 initialization
        pass

    def call_api_version_1(self, method, params):
        """Call API using SDK v1 conventions."""
        # v1 API call
        return {}

    def call_api_version_2(self, method, params):
        """Call API using SDK v2 conventions."""
        # v2 API call
        return {}


# ===== Pattern Example 4: Protocol Handler (Should be flagged - MEDIUM) =====

class ProtocolHandler:
    """Handles different protocol versions."""

    def handle_protocol_v1(self, data):
        """Handle protocol version 1."""
        return self.process_v1_format(data)

    def handle_protocol_v2(self, data):
        """Handle protocol version 2."""
        return self.process_v2_format(data)

    def handle_protocol_v3(self, data):
        """Handle protocol version 3."""
        return self.process_v3_format(data)

    def process_v1_format(self, data):
        """Process v1 data format."""
        return data

    def process_v2_format(self, data):
        """Process v2 data format."""
        return data

    def process_v3_format(self, data):
        """Process v3 data format."""
        return data


# ===== Pattern Example 5: Legacy System Bridge (Should be flagged - HIGH) =====

class LegacySystemBridge:
    """Bridge to handle both legacy and new systems."""

    def __init__(self):
        self.version = None
        self.client_version = None

    def process_legacy_request(self, request):
        """Process legacy format requests."""
        return self.convert_legacy_to_standard(request)

    def process_new_request(self, request):
        """Process new format requests."""
        return self.convert_new_to_standard(request)

    def handle_old_authentication(self, credentials):
        """Handle old authentication method."""
        # Old auth logic
        pass

    def handle_new_authentication(self, credentials):
        """Handle new authentication method."""
        # New auth logic
        pass

    def translate_old_response(self, response):
        """Translate old response format."""
        return response

    def translate_new_response(self, response):
        """Translate new response format."""
        return response

    def convert_legacy_to_standard(self, data):
        """Convert legacy format to standard."""
        return data

    def convert_new_to_standard(self, data):
        """Convert new format to standard."""
        return data


# ===== Example of Good Design (Already extracted adapters) =====

class BaseAdapter:
    """Base adapter interface."""

    def connect(self):
        raise NotImplementedError

    def query(self, sql):
        raise NotImplementedError


class DatabaseV1Adapter(BaseAdapter):
    """Adapter for database v1 - good pattern."""

    def connect(self):
        # v1 specific connection
        pass

    def query(self, sql):
        # v1 specific query
        return []


class DatabaseV2Adapter(BaseAdapter):
    """Adapter for database v2 - good pattern."""

    def connect(self):
        # v2 specific connection
        pass

    def query(self, sql):
        # v2 specific query
        return []


# ===== Simple Class (Should NOT be flagged) =====

class SimpleClient:
    """Simple client with no version handling."""

    def __init__(self):
        self.connected = False

    def connect(self):
        """Connect to service."""
        self.connected = True

    def disconnect(self):
        """Disconnect from service."""
        self.connected = False

    def send_request(self, data):
        """Send a request."""
        return {"response": "ok"}


# ===== Client with Version Switching (Should be flagged - HIGH) =====

class MultiVersionClient:
    """Client handling multiple API versions with conditionals."""

    def __init__(self, api_version="3.0"):
        self.api_version = api_version

    def make_request(self, endpoint, data):
        """Make request based on version."""
        if self.api_version == "1.0":
            return self.make_request_v1(endpoint, data)
        elif self.api_version == "2.0":
            return self.make_request_v2(endpoint, data)
        else:
            return self.make_request_v3(endpoint, data)

    def make_request_v1(self, endpoint, data):
        """Make v1 API request."""
        # v1 request logic
        return {}

    def make_request_v2(self, endpoint, data):
        """Make v2 API request."""
        # v2 request logic
        return {}

    def make_request_v3(self, endpoint, data):
        """Make v3 API request."""
        # v3 request logic
        return {}

    def parse_response_api_1(self, response):
        """Parse API v1 response."""
        return response

    def parse_response_api_2(self, response):
        """Parse API v2 response."""
        return response

    def parse_response_api_3(self, response):
        """Parse API v3 response."""
        return response


# ===== Service Connector (Should be flagged - MEDIUM) =====

class ServiceConnector:
    """Connector supporting old and new service interfaces."""

    def connect_old_service(self):
        """Connect to old service interface."""
        pass

    def connect_new_service(self):
        """Connect to new service interface."""
        pass

    def authenticate_legacy(self, credentials):
        """Legacy authentication method."""
        pass

    def authenticate_new(self, credentials):
        """New authentication method."""
        pass


# ===== Client Code Examples =====

def use_api_client():
    """Example of using multi-version API client - problematic."""
    client = APIClient(version="v2")

    if client.version == "v1":
        user = client.get_user_v1(123)
        processed = client.process_response_v1(json.dumps(user))
    elif client.version == "v2":
        user = client.get_user_v2(123)
        processed = client.process_response_v2(json.dumps(user))
    else:
        user = client.get_user_v3(123)
        processed = client.process_response_v3(json.dumps(user))

    return processed


def use_database_adapter():
    """Example of using multi-version database adapter - problematic."""
    db = DatabaseAdapter(db_version="v2")

    if db.db_version == "legacy":
        db.connect_legacy()
        results = db.query_legacy("SELECT * FROM users")
    elif db.db_version == "v1":
        db.connect_v1()
        results = db.query_v1("SELECT * FROM users")
    else:
        db.connect_v2()
        results = db.query_v2("SELECT * FROM users")

    return results