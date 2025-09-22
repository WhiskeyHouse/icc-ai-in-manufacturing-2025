# WHK Testing Framework for Ignition

A comprehensive unit testing framework for Jython code in Ignition that provides test discovery, execution, and reporting via WebDev endpoints.

## Overview

The WHK Testing Framework enables:
- **Unit testing** of Jython scripts in Ignition environment
- **Automatic test discovery** using `test_` prefix convention
- **WebDev REST API** for test execution and CI/CD integration
- **Mock system functions** for isolated testing
- **Multiple output formats** (JSON, JUnit XML, HTML, Text)
- **Integration** with existing WHK validation framework

## Quick Start

### 1. Test a Simple Function

Create a test file at `ignition/script-python/whk/tests/test_example/code.py`:

```python
from whk.testing import TestCase

class TestExample(TestCase):
    def test_basic_math(self):
        """Test basic arithmetic operations."""
        self.assertEqual(2 + 2, 4)
        self.assertTrue(10 > 5)
        self.assertIn('hello', 'hello world')

# Simple test function (also discoverable)
def test_string_operations():
    """Test string manipulations."""
    test_str = "Ignition"
    assert len(test_str) == 8, "String length should be 8"
    assert test_str.lower() == "ignition", "Lowercase should work"
```

### 2. Run Tests via WebDev API

**Discover all tests:**
```bash
GET http://localhost:8088/data/testing/discover
```

**Run a specific test:**
```bash
POST http://localhost:8088/data/testing/run
Content-Type: application/json

{
    "test_name": "whk.tests.test_example.test_string_operations"
}
```

**Run all tests in a module:**
```bash
POST http://localhost:8088/data/testing/run
Content-Type: application/json

{
    "module_path": "whk.tests.test_example"
}
```

**Run all tests:**
```bash
POST http://localhost:8088/data/testing/run
Content-Type: application/json

{
    "run_all": true
}
```

## Framework Components

### Core Testing (`whk.testing`)

The main testing classes and functions:

```python
from whk.testing import TestCase, TestSuite, TestRunner

class MyTest(TestCase):
    def setUp(self):
        """Called before each test method."""
        self.test_data = {"value": 100}
    
    def tearDown(self):
        """Called after each test method."""
        pass
    
    def test_example(self):
        """Example test method."""
        self.assertEqual(self.test_data["value"], 100)
        self.assertGreater(self.test_data["value"], 50)
```

Available assertion methods:
- `assertEqual(a, b)` - Assert a equals b
- `assertNotEqual(a, b)` - Assert a does not equal b  
- `assertTrue(x)` - Assert x is true
- `assertFalse(x)` - Assert x is false
- `assertIsNone(x)` - Assert x is None
- `assertIsNotNone(x)` - Assert x is not None
- `assertIn(a, b)` - Assert a is in b
- `assertNotIn(a, b)` - Assert a is not in b
- `assertRaises(exception, callable)` - Assert callable raises exception
- `assertAlmostEqual(a, b, places=7)` - Assert floats are equal within tolerance

### Mock System Functions (`whk.testing.mocks`)

Test Ignition scripts without actual system dependencies:

```python
from whk.testing import TestCase
from whk.testing.mocks import with_mocks, setup_test_tags, assert_tag_written

class TestBatchControl(TestCase):
    
    @with_mocks
    def test_temperature_monitoring(self):
        """Test batch temperature monitoring with mocks."""
        # Setup initial tag values
        setup_test_tags({
            "[default]Batch/Temperature": 90.0,  # Over limit
            "[default]Batch/Status": "Running"
        })
        
        # Import and run your script
        import my_batch_script
        result = my_batch_script.monitor_temperature()
        
        # Verify expected tag writes occurred
        assert_tag_written(self, "[default]Batch/EmergencyStop", True)
        assert_tag_written(self, "[default]Audit/Action", "Emergency Stop")
```

Mock utilities:
- `@with_mocks` - Decorator to activate mocks for test
- `setup_test_tags(dict)` - Set initial tag values
- `setup_test_responses(dict)` - Set HTTP response mocks
- `assert_tag_written(test, path, value)` - Assert tag was written
- `assert_tag_read(test, path)` - Assert tag was read
- `assert_http_called(test, url, method)` - Assert HTTP request was made

### Test Discovery (`whk.testing.discovery`)

Automatically find and load tests:

```python
from whk.testing.discovery import discover_tests, list_tests

# Discover all tests
all_tests = discover_tests()

# Discover tests in specific module
module_tests = discover_tests(module_path="whk.tests.test_validation")

# Discover specific test
single_test = discover_tests(test_name="whk.tests.test_validation.test_script_validation")

# List available tests
test_list = list_tests()
```

Test discovery rules:
- Functions starting with `test_` are discovered as tests
- Classes ending with `Test` and inheriting from `TestCase` are discovered
- Methods in test classes starting with `test_` are discovered as individual tests

### Result Reporting (`whk.testing.reporting`)

Multiple output formats for test results:

```python
from whk.testing.reporting import format_test_results

# Run tests and get results
runner = TestRunner()
result = runner.run(test_suite)

# Format in different ways
json_report = format_test_results(result, 'json')
xml_report = format_test_results(result, 'junit_xml')  # For CI/CD
html_report = format_test_results(result, 'html')     # For web display
text_report = format_test_results(result, 'text')     # For console
```

## WebDev API Reference

### GET Endpoints

**GET /testing** - API documentation
```json
{
    "service": "WHK Testing Framework API",
    "version": "1.0.0",
    "endpoints": { ... }
}
```

**GET /testing/discover** - List all available tests
```json
{
    "tests": [
        {
            "name": "whk.tests.test_validation.test_script_validation",
            "module": "whk.tests.test_validation", 
            "method": "test_script_validation"
        }
    ],
    "count": 1
}
```

**GET /testing/results** - List test result sessions
```json
{
    "sessions": [
        {
            "session_id": "test_run_1642434567890",
            "timestamp": "2025-01-17T12:00:00Z",
            "success": true,
            "tests_run": 5,
            "failures": 0,
            "errors": 0
        }
    ]
}
```

**GET /testing/results/{session_id}** - Get specific test results
```json
{
    "session_id": "test_run_1642434567890",
    "results": {
        "success": true,
        "summary": { ... },
        "failures": [],
        "errors": [],
        "skipped": []
    }
}
```

**GET /testing/health** - Service health check
```json
{
    "status": "healthy",
    "test_framework": "whk.testing",
    "discovered_tests": 15,
    "stored_results": 3
}
```

### POST Endpoints

**POST /testing/run** - Execute tests

Run specific test:
```json
{
    "test_name": "whk.tests.test_validation.test_script_validation",
    "store_results": true
}
```

Run module tests:
```json
{
    "module_path": "whk.tests.test_validation",
    "store_results": true
}
```

Run all tests:
```json
{
    "run_all": true,
    "store_results": true
}
```

Response:
```json
{
    "success": true,
    "session_id": "test_run_1642434567890",
    "summary": {
        "tests_run": 3,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "success": true,
        "duration_ms": 150
    },
    "failures": [],
    "errors": [],
    "skipped": []
}
```

**POST /testing/discover** - Refresh test discovery
```json
{
    "tests": [...],
    "count": 15
}
```

**POST /testing/validate** - Validate test syntax
```json
{
    "test_name": "whk.tests.test_validation.test_script_validation"
}
```

Response:
```json
{
    "name": "whk.tests.test_validation.test_script_validation",
    "exists": true,
    "module": "whk.tests.test_validation",
    "method": "test_script_validation",
    "docstring": "Test script validation functionality."
}
```

## Testing Patterns

### Testing Ignition Scripts

```python
from whk.testing import TestCase
from whk.testing.mocks import with_mocks, setup_test_tags, assert_tag_written

class TestProductionScript(TestCase):
    
    @with_mocks
    def test_recipe_execution(self):
        """Test recipe execution with proper audit logging."""
        # Setup test environment
        setup_test_tags({
            "[default]Recipe/Current/ID": "BATCH_001",
            "[default]Recipe/Current/Step": 1,
            "[default]Equipment/Tank1/Ready": True
        })
        
        # Import and execute your script
        import production.recipe_manager
        result = production.recipe_manager.execute_step()
        
        # Verify expected behavior
        self.assertTrue(result)
        assert_tag_written(self, "[default]Recipe/Current/Step", 2)
        assert_tag_written(self, "[default]Audit/LastAction", "Step 1 completed")
```

### Testing Component Scripts

```python
from whk.testing import TestCase
from whk.testing.mocks import with_mocks, mock_system

class TestButtonScript(TestCase):
    
    @with_mocks
    def test_start_button_script(self):
        """Test start button event script."""
        # Your button script logic here
        def start_button_script():
            import system
            current_status = system.tag.read("[default]Line/Status").value
            if current_status == "Ready":
                system.tag.writeBlocking("[default]Line/Command", "Start")
                return True
            return False
        
        # Setup test
        mock_system.tag.set_tag_value("[default]Line/Status", "Ready")
        
        # Execute
        result = start_button_script()
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(
            mock_system.tag.get_tag_value("[default]Line/Command"), 
            "Start"
        )
```

### Testing with External Services

```python
from whk.testing import TestCase
from whk.testing.mocks import with_mocks, setup_test_responses

class TestServiceIntegration(TestCase):
    
    @with_mocks
    def test_api_call(self):
        """Test external API integration."""
        # Setup mock HTTP response
        setup_test_responses({
            "http://api.example.com/data": '{"status": "success", "value": 123}'
        })
        
        # Your script that calls the API
        import system
        response = system.net.httpGet("http://api.example.com/data")
        data = system.util.jsonDecode(response)
        
        # Verify
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["value"], 123)
```

## CI/CD Integration

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Run Tests') {
            steps {
                script {
                    def response = httpRequest(
                        url: 'http://ignition-gateway:8088/data/testing/run',
                        httpMode: 'POST',
                        contentType: 'APPLICATION_JSON',
                        requestBody: '{"run_all": true}'
                    )
                    
                    def results = readJSON text: response.content
                    
                    if (!results.success) {
                        error("Tests failed: ${results.summary.failures} failures, ${results.summary.errors} errors")
                    }
                    
                    echo "All ${results.summary.tests_run} tests passed!"
                }
            }
        }
    }
    
    post {
        always {
            // Get JUnit XML format for reporting
            script {
                def xmlResponse = httpRequest(
                    url: 'http://ignition-gateway:8088/data/testing/results/latest',
                    httpMode: 'GET'
                )
                // Process XML results...
            }
        }
    }
}
```

### GitHub Actions Example

```yaml
name: Ignition Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Wait for Ignition
      run: |
        timeout 60 bash -c 'until curl -f http://localhost:8088/data/testing/health; do sleep 2; done'
    
    - name: Run Tests
      run: |
        response=$(curl -s -X POST \
          -H "Content-Type: application/json" \
          -d '{"run_all": true}' \
          http://localhost:8088/data/testing/run)
        
        echo "$response" | jq .
        
        success=$(echo "$response" | jq -r .success)
        if [ "$success" != "true" ]; then
          echo "Tests failed!"
          exit 1
        fi
```

## Best Practices

### 1. Test Organization

```
ignition/script-python/
├── whk/
│   ├── production/              # Production code
│   │   ├── batch_control/
│   │   └── recipe_manager/
│   └── tests/                   # Test code
│       ├── test_batch_control/
│       ├── test_recipe_manager/
│       └── test_integration/
```

### 2. Test Naming

- Test files: `test_module_name/code.py`
- Test classes: `TestModuleName(TestCase)`
- Test methods: `test_specific_functionality(self)`
- Test functions: `test_specific_functionality()`

### 3. Use Mocks for System Dependencies

```python
# Good - Uses mocks
@with_mocks
def test_tag_operations():
    setup_test_tags({"[default]Input": 100})
    # Test logic here

# Avoid - Depends on real tags
def test_tag_operations():
    system.tag.write("[default]Input", 100)  # May affect real system
```

### 4. Write Descriptive Test Names

```python
# Good
def test_emergency_stop_triggers_when_temperature_exceeds_limit(self):
    """Test that emergency stop is triggered when temperature exceeds 85°F."""

# Avoid  
def test_temp(self):
    """Test temperature."""
```

### 5. Test Both Success and Failure Cases

```python
def test_batch_validation_success(self):
    """Test batch validation with valid data."""
    # Test success case

def test_batch_validation_missing_recipe(self):
    """Test batch validation fails when recipe is missing."""
    # Test failure case
```

## Troubleshooting

### Common Issues

**1. Tests not discovered**
- Ensure test functions start with `test_`
- Check that test files are in the correct location
- Verify module imports work correctly

**2. Mock system not working**
- Ensure `@with_mocks` decorator is used
- Check that mocks are activated before system imports
- Use `mock_system.reset_all_mocks()` between tests if needed

**3. WebDev endpoint errors**
- Verify Ignition gateway is running
- Check that WebDev module is enabled
- Ensure proper JSON formatting in requests

**4. Import errors in tests**
- Check that script library paths are correct
- Verify that all dependencies are available
- Use absolute imports when possible

### Debugging Tests

```python
from whk.testing import TestCase
from com.inductiveautomation.ignition.common.util import LoggerEx

class TestWithLogging(TestCase):
    def setUp(self):
        self.logger = LoggerEx.newBuilder().name("WHK.Test.Debug").build()
    
    def test_with_debugging(self):
        """Test with debug logging."""
        self.logger.info("Starting test")
        
        # Your test logic
        result = some_function()
        
        self.logger.info("Function returned: {}".format(result))
        self.assertEqual(result, expected_value)
```

## Extending the Framework

### Custom Assertions

```python
from whk.testing import TestCase

class CustomTestCase(TestCase):
    def assertTagValue(self, tag_path, expected_value):
        """Custom assertion for tag values."""
        actual_value = system.tag.read(tag_path).value
        self.assertEqual(actual_value, expected_value, 
                        "Tag {} has value {} but expected {}".format(
                            tag_path, actual_value, expected_value))

class MyTest(CustomTestCase):
    def test_tag_operations(self):
        self.assertTagValue("[default]Output", 100)
```

### Custom Reporters

```python
from whk.testing.reporting import TestReporter, reporting_manager

class SlackReporter(TestReporter):
    def format_results(self, test_result):
        summary = test_result.summary()
        if summary['success']:
            message = "✅ All {} tests passed!".format(summary['tests_run'])
        else:
            message = "❌ {} tests failed, {} errors".format(
                summary['failures'], summary['errors'])
        
        return {
            'format': 'slack',
            'message': message,
            'summary': summary
        }

# Register custom reporter
reporting_manager.add_reporter('slack', SlackReporter)
```

The WHK Testing Framework provides a comprehensive solution for unit testing Jython code in Ignition, enabling Test-Driven Development practices and CI/CD integration for industrial automation projects.