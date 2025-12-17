"""
Test cases for Form Template Method pattern detection.

Demonstrates sibling classes with methods performing similar steps in the same order,
but with different implementations - indicating opportunities for template method.
"""

# Example 1: Data processors with similar processing steps
class DataProcessor:
    """Base class for data processors."""
    def __init__(self):
        self.data = None
        self.results = []

class CSVProcessor(DataProcessor):
    """Processes CSV files with specific steps."""

    def process(self, filepath):
        """Process CSV file - similar steps to JSONProcessor but different implementation."""
        self.validate_file(filepath)
        self.load_data(filepath)
        self.parse_content()
        self.transform_data()
        self.save_results()
        return self.results

    def validate_file(self, filepath):
        """Validate CSV file format."""
        if not filepath.endswith('.csv'):
            raise ValueError("Not a CSV file")
        # CSV-specific validation

    def load_data(self, filepath):
        """Load CSV data."""
        import csv
        with open(filepath) as f:
            reader = csv.reader(f)
            self.data = list(reader)

    def parse_content(self):
        """Parse CSV content."""
        # CSV-specific parsing
        headers = self.data[0]
        rows = self.data[1:]
        self.data = [dict(zip(headers, row)) for row in rows]

    def transform_data(self):
        """Transform CSV data."""
        # CSV-specific transformation
        for item in self.data:
            item['processed'] = True

    def save_results(self):
        """Save CSV processing results."""
        self.results = self.data.copy()


class JSONProcessor(DataProcessor):
    """Processes JSON files with specific steps."""

    def process(self, filepath):
        """Process JSON file - similar steps to CSVProcessor but different implementation."""
        self.validate_file(filepath)
        self.load_data(filepath)
        self.parse_content()
        self.transform_data()
        self.save_results()
        return self.results

    def validate_file(self, filepath):
        """Validate JSON file format."""
        if not filepath.endswith('.json'):
            raise ValueError("Not a JSON file")
        # JSON-specific validation

    def load_data(self, filepath):
        """Load JSON data."""
        import json
        with open(filepath) as f:
            self.data = json.load(f)

    def parse_content(self):
        """Parse JSON content."""
        # JSON-specific parsing
        if isinstance(self.data, list):
            self.data = {'items': self.data}

    def transform_data(self):
        """Transform JSON data."""
        # JSON-specific transformation
        if 'items' in self.data:
            for item in self.data['items']:
                item['processed'] = True

    def save_results(self):
        """Save JSON processing results."""
        self.results = self.data.copy()


class XMLProcessor(DataProcessor):
    """Processes XML files with specific steps."""

    def process(self, filepath):
        """Process XML file - similar steps but different implementation."""
        self.validate_file(filepath)
        self.load_data(filepath)
        self.parse_content()
        self.transform_data()
        self.save_results()
        return self.results

    def validate_file(self, filepath):
        """Validate XML file format."""
        if not filepath.endswith('.xml'):
            raise ValueError("Not an XML file")
        # XML-specific validation

    def load_data(self, filepath):
        """Load XML data."""
        import xml.etree.ElementTree as ET
        tree = ET.parse(filepath)
        self.data = tree.getroot()

    def parse_content(self):
        """Parse XML content."""
        # XML-specific parsing
        items = []
        for child in self.data:
            items.append({tag.tag: tag.text for tag in child})
        self.data = items

    def transform_data(self):
        """Transform XML data."""
        # XML-specific transformation
        for item in self.data:
            item['processed'] = 'true'

    def save_results(self):
        """Save XML processing results."""
        self.results = self.data.copy()


# Example 2: Report generators with similar generation steps
class ReportGenerator:
    """Base class for report generators."""
    def __init__(self):
        self.report = ""
        self.data = {}

class HTMLReportGenerator(ReportGenerator):
    """Generates HTML reports."""

    def generate_report(self, data):
        """Generate HTML report - template method candidate."""
        self.prepare_data(data)
        self.create_header()
        self.create_body()
        self.create_footer()
        self.finalize_report()
        return self.report

    def prepare_data(self, data):
        """Prepare data for HTML report."""
        self.data = data
        # HTML-specific data preparation

    def create_header(self):
        """Create HTML header."""
        self.report = "<html><head><title>Report</title></head><body>"
        self.report += f"<h1>{self.data.get('title', 'Report')}</h1>"

    def create_body(self):
        """Create HTML body."""
        self.report += "<div class='content'>"
        for section in self.data.get('sections', []):
            self.report += f"<section><h2>{section['title']}</h2>"
            self.report += f"<p>{section['content']}</p></section>"
        self.report += "</div>"

    def create_footer(self):
        """Create HTML footer."""
        self.report += "<footer>Generated on " + self.data.get('date', '') + "</footer>"

    def finalize_report(self):
        """Finalize HTML report."""
        self.report += "</body></html>"


class PDFReportGenerator(ReportGenerator):
    """Generates PDF reports."""

    def generate_report(self, data):
        """Generate PDF report - template method candidate."""
        self.prepare_data(data)
        self.create_header()
        self.create_body()
        self.create_footer()
        self.finalize_report()
        return self.report

    def prepare_data(self, data):
        """Prepare data for PDF report."""
        self.data = data
        # PDF-specific data preparation
        self.report = "PDF_START\n"

    def create_header(self):
        """Create PDF header."""
        self.report += "PDF_HEADER\n"
        self.report += f"Title: {self.data.get('title', 'Report')}\n"
        self.report += "PDF_HEADER_END\n"

    def create_body(self):
        """Create PDF body."""
        self.report += "PDF_BODY\n"
        for section in self.data.get('sections', []):
            self.report += f"Section: {section['title']}\n"
            self.report += f"Content: {section['content']}\n"
        self.report += "PDF_BODY_END\n"

    def create_footer(self):
        """Create PDF footer."""
        self.report += "PDF_FOOTER\n"
        self.report += "Generated: " + self.data.get('date', '') + "\n"

    def finalize_report(self):
        """Finalize PDF report."""
        self.report += "PDF_END"


class MarkdownReportGenerator(ReportGenerator):
    """Generates Markdown reports."""

    def generate_report(self, data):
        """Generate Markdown report - template method candidate."""
        self.prepare_data(data)
        self.create_header()
        self.create_body()
        self.create_footer()
        self.finalize_report()
        return self.report

    def prepare_data(self, data):
        """Prepare data for Markdown report."""
        self.data = data
        # Markdown-specific data preparation
        self.report = ""

    def create_header(self):
        """Create Markdown header."""
        self.report += f"# {self.data.get('title', 'Report')}\n\n"
        self.report += "---\n\n"

    def create_body(self):
        """Create Markdown body."""
        for section in self.data.get('sections', []):
            self.report += f"## {section['title']}\n\n"
            self.report += f"{section['content']}\n\n"

    def create_footer(self):
        """Create Markdown footer."""
        self.report += "---\n\n"
        self.report += f"*Generated on {self.data.get('date', '')}*\n"

    def finalize_report(self):
        """Finalize Markdown report."""
        self.report += "\n<!-- End of Report -->"


# Example 3: Test runners with similar execution steps
class TestRunner:
    """Base class for test runners."""
    def __init__(self):
        self.tests = []
        self.results = []

class UnitTestRunner(TestRunner):
    """Runs unit tests."""

    def run_tests(self, test_suite):
        """Run unit tests - template method candidate."""
        self.setup_environment()
        self.load_tests(test_suite)
        self.execute_tests()
        self.collect_results()
        self.cleanup_environment()
        return self.results

    def setup_environment(self):
        """Setup unit test environment."""
        # Unit test specific setup
        import unittest
        self.loader = unittest.TestLoader()

    def load_tests(self, test_suite):
        """Load unit tests."""
        self.tests = self.loader.loadTestsFromModule(test_suite)

    def execute_tests(self):
        """Execute unit tests."""
        import unittest
        runner = unittest.TextTestRunner()
        self.test_result = runner.run(self.tests)

    def collect_results(self):
        """Collect unit test results."""
        self.results = {
            'passed': self.test_result.wasSuccessful(),
            'failures': len(self.test_result.failures),
            'errors': len(self.test_result.errors)
        }

    def cleanup_environment(self):
        """Cleanup unit test environment."""
        # Unit test specific cleanup
        self.loader = None
        self.test_result = None


class IntegrationTestRunner(TestRunner):
    """Runs integration tests."""

    def run_tests(self, test_suite):
        """Run integration tests - template method candidate."""
        self.setup_environment()
        self.load_tests(test_suite)
        self.execute_tests()
        self.collect_results()
        self.cleanup_environment()
        return self.results

    def setup_environment(self):
        """Setup integration test environment."""
        # Integration test specific setup
        self.db_connection = self._connect_to_database()
        self.api_client = self._create_api_client()

    def load_tests(self, test_suite):
        """Load integration tests."""
        # Integration test specific loading
        self.tests = test_suite.get_integration_tests()

    def execute_tests(self):
        """Execute integration tests."""
        # Integration test specific execution
        self.test_results = []
        for test in self.tests:
            result = test.run(self.db_connection, self.api_client)
            self.test_results.append(result)

    def collect_results(self):
        """Collect integration test results."""
        passed = sum(1 for r in self.test_results if r['passed'])
        self.results = {
            'passed': passed == len(self.test_results),
            'total': len(self.test_results),
            'passed_count': passed
        }

    def cleanup_environment(self):
        """Cleanup integration test environment."""
        # Integration test specific cleanup
        if self.db_connection:
            self.db_connection.close()
        if self.api_client:
            self.api_client.disconnect()

    def _connect_to_database(self):
        """Connect to test database."""
        return None  # Mock connection

    def _create_api_client(self):
        """Create API client for testing."""
        return None  # Mock client


class PerformanceTestRunner(TestRunner):
    """Runs performance tests."""

    def run_tests(self, test_suite):
        """Run performance tests - template method candidate."""
        self.setup_environment()
        self.load_tests(test_suite)
        self.execute_tests()
        self.collect_results()
        self.cleanup_environment()
        return self.results

    def setup_environment(self):
        """Setup performance test environment."""
        # Performance test specific setup
        import time
        self.start_time = time.time()
        self.metrics = []

    def load_tests(self, test_suite):
        """Load performance tests."""
        # Performance test specific loading
        self.tests = test_suite.get_performance_scenarios()

    def execute_tests(self):
        """Execute performance tests."""
        # Performance test specific execution
        import time
        for test in self.tests:
            test_start = time.time()
            test.run()
            test_end = time.time()
            self.metrics.append({
                'test': test.name,
                'duration': test_end - test_start
            })

    def collect_results(self):
        """Collect performance test results."""
        import time
        total_time = time.time() - self.start_time
        avg_time = sum(m['duration'] for m in self.metrics) / len(self.metrics) if self.metrics else 0
        self.results = {
            'total_time': total_time,
            'average_time': avg_time,
            'metrics': self.metrics
        }

    def cleanup_environment(self):
        """Cleanup performance test environment."""
        # Performance test specific cleanup
        self.metrics.clear()
        self.start_time = None


# Example 4: Request handlers with similar handling steps
class RequestHandler:
    """Base class for request handlers."""
    def __init__(self):
        self.request = None
        self.response = None

class APIRequestHandler(RequestHandler):
    """Handles API requests."""

    def handle_request(self, request):
        """Handle API request - template method candidate."""
        self.authenticate(request)
        self.validate_request(request)
        self.process_request(request)
        self.format_response()
        self.log_request()
        return self.response

    def authenticate(self, request):
        """Authenticate API request."""
        # Check API key
        if 'api_key' not in request.headers:
            raise ValueError("Missing API key")
        # API-specific authentication

    def validate_request(self, request):
        """Validate API request."""
        self.request = request
        # Validate JSON schema
        if request.content_type != 'application/json':
            raise ValueError("Invalid content type")

    def process_request(self, request):
        """Process API request."""
        # API-specific processing
        data = request.get_json()
        self.response = {'status': 'success', 'data': data}

    def format_response(self):
        """Format API response."""
        # Format as JSON
        import json
        self.response = json.dumps(self.response)

    def log_request(self):
        """Log API request."""
        # Log to API log
        print(f"API Request: {self.request.path}")


class WebRequestHandler(RequestHandler):
    """Handles web requests."""

    def handle_request(self, request):
        """Handle web request - template method candidate."""
        self.authenticate(request)
        self.validate_request(request)
        self.process_request(request)
        self.format_response()
        self.log_request()
        return self.response

    def authenticate(self, request):
        """Authenticate web request."""
        # Check session
        if 'session_id' not in request.cookies:
            raise ValueError("Not logged in")
        # Web-specific authentication

    def validate_request(self, request):
        """Validate web request."""
        self.request = request
        # Validate CSRF token
        if request.method == 'POST' and 'csrf_token' not in request.form:
            raise ValueError("Missing CSRF token")

    def process_request(self, request):
        """Process web request."""
        # Web-specific processing
        template_data = {'user': request.user, 'page': request.path}
        self.response = template_data

    def format_response(self):
        """Format web response."""
        # Format as HTML
        self.response = f"<html><body>{self.response}</body></html>"

    def log_request(self):
        """Log web request."""
        # Log to web log
        print(f"Web Request: {self.request.path}")


class GraphQLRequestHandler(RequestHandler):
    """Handles GraphQL requests."""

    def handle_request(self, request):
        """Handle GraphQL request - template method candidate."""
        self.authenticate(request)
        self.validate_request(request)
        self.process_request(request)
        self.format_response()
        self.log_request()
        return self.response

    def authenticate(self, request):
        """Authenticate GraphQL request."""
        # Check bearer token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise ValueError("Invalid authorization")
        # GraphQL-specific authentication

    def validate_request(self, request):
        """Validate GraphQL request."""
        self.request = request
        # Validate GraphQL query
        query = request.get_json().get('query', '')
        if not query:
            raise ValueError("Missing GraphQL query")

    def process_request(self, request):
        """Process GraphQL request."""
        # GraphQL-specific processing
        query_data = request.get_json()
        # Execute GraphQL query
        self.response = {'data': {'result': 'GraphQL result'}}

    def format_response(self):
        """Format GraphQL response."""
        # Format as GraphQL response
        import json
        self.response = json.dumps({'data': self.response})

    def log_request(self):
        """Log GraphQL request."""
        # Log to GraphQL log
        print(f"GraphQL Request: {self.request.get_json().get('query', '')[:50]}")


# Test function
def test_form_template_method_opportunities():
    """Test that demonstrates template method opportunities."""
    # The classes above show multiple examples of the Form Template Method pattern:

    # 1. DataProcessor subclasses (CSVProcessor, JSONProcessor, XMLProcessor)
    #    all have process() methods with the same sequence of steps

    # 2. ReportGenerator subclasses (HTMLReportGenerator, PDFReportGenerator, MarkdownReportGenerator)
    #    all have generate_report() methods with identical step sequences

    # 3. TestRunner subclasses (UnitTestRunner, IntegrationTestRunner, PerformanceTestRunner)
    #    all have run_tests() methods following the same algorithm

    # 4. RequestHandler subclasses (APIRequestHandler, WebRequestHandler, GraphQLRequestHandler)
    #    all have handle_request() methods with the same processing steps

    print("Form Template Method test cases loaded successfully")
    return True


if __name__ == "__main__":
    test_form_template_method_opportunities()