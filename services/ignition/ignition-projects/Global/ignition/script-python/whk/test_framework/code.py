"""Tests for the WHK Testing Framework itself.
Meta-tests to ensure the testing framework works correctly.
"""

from whk.testing_core import TestCase, TestResult, TestSuite, TestRunner
from whk.testing_mocks import MockTagSystem, mock_system, with_mocks
from whk.testing_discovery import TestLoader, TestDiscovery
from whk.testing_reporting import format_test_results


class TestFrameworkCore(TestCase):
    """Test the core testing framework functionality."""
    
    def test_test_case_assertions(self):
        """Test basic assertion methods."""
        # Test assertEqual
        self.assertEqual(1, 1)
        self.assertEqual("hello", "hello")
        
        # Test assertTrue/assertFalse
        self.assertTrue(True)
        self.assertFalse(False)
        
        # Test assertIsNone/assertIsNotNone
        self.assertIsNone(None)
        self.assertIsNotNone("not none")
        
        # Test assertIn/assertNotIn
        self.assertIn(1, [1, 2, 3])
        self.assertNotIn(4, [1, 2, 3])
        
    def test_assertion_failures(self):
        """Test that assertions properly fail."""
        from whk.testing_core import AssertionError
        
        # Test assertEqual failure
        with self.assertRaises(AssertionError):
            self.assertEqual(1, 2)
            
        # Test assertTrue failure
        with self.assertRaises(AssertionError):
            self.assertTrue(False)
            
        # Test assertIn failure
        with self.assertRaises(AssertionError):
            self.assertIn(5, [1, 2, 3])
            
    def test_test_result_tracking(self):
        """Test that TestResult properly tracks test outcomes."""
        result = TestResult()
        
        # Simulate test run
        result.startTestRun()
        result.startTest("test1")
        result.addSuccess("test1")
        
        result.startTest("test2") 
        result.addFailure("test2", {"message": "Test failed"})
        
        result.startTest("test3")
        result.addError("test3", {"message": "Test error"})
        
        result.startTest("test4")
        result.addSkip("test4", "Test skipped")
        
        result.stopTestRun()
        
        # Check tracking
        self.assertEqual(result.tests_run, 4)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.skipped), 1)
        self.assertFalse(result.wasSuccessful())
        
        summary = result.summary()
        self.assertEqual(summary['tests_run'], 4)
        self.assertEqual(summary['failures'], 1)
        self.assertEqual(summary['errors'], 1)
        self.assertEqual(summary['skipped'], 1)
        self.assertFalse(summary['success'])


class TestMockSystem(TestCase):
    """Test the mock system functionality."""
    
    def test_mock_tag_operations(self):
        """Test mock tag read/write operations."""
        mock_tags = MockTagSystem()
        
        # Test write then read
        mock_tags.write("[default]Test/Tag", 123)
        value = mock_tags.read("[default]Test/Tag")
        
        self.assertEqual(value.value, 123)
        
        # Test multiple tags
        mock_tags.writeBlocking(
            ["[default]Tag1", "[default]Tag2"], 
            [100, 200]
        )
        
        values = mock_tags.readBlocking(["[default]Tag1", "[default]Tag2"])
        self.assertEqual(values[0].value, 100)
        self.assertEqual(values[1].value, 200)
        
    def test_mock_tag_logging(self):
        """Test that mock system logs operations."""
        mock_tags = MockTagSystem()
        
        # Clear logs
        mock_tags.clear_logs()
        
        # Perform operations
        mock_tags.read(["[default]Test1", "[default]Test2"])
        mock_tags.write("[default]Output", 456)
        
        # Check logs
        read_log = mock_tags.get_read_log()
        write_log = mock_tags.get_write_log()
        
        self.assertEqual(len(read_log), 1)
        self.assertEqual(len(write_log), 1)
        
        self.assertIn("[default]Test1", read_log[0])
        self.assertIn("[default]Test2", read_log[0])
        self.assertEqual(write_log[0]['paths'], ["[default]Output"])
        self.assertEqual(write_log[0]['values'], [456])
        
    @with_mocks
    def test_mock_activation(self):
        """Test that mock system can be activated."""
        # Mock should be active within this decorator
        
        # Test that we can import and use system
        import system
        
        # Perform some operations
        system.tag.write("[default]MockTest", 789)
        value = system.tag.read("[default]MockTest")
        
        self.assertEqual(value.value, 789)
        
        # Check that operations were logged
        write_log = system.tag.get_write_log()
        self.assertGreater(len(write_log), 0)


class TestDiscoverySystem(TestCase):
    """Test the test discovery functionality."""
    
    def test_test_loader_basic(self):
        """Test basic test loading functionality."""
        loader = TestLoader()
        
        # Test that we can create a loader
        self.assertIsNotNone(loader)
        self.assertEqual(loader.test_method_prefix, 'test_')
        
    def test_test_discovery_basic(self):
        """Test basic test discovery."""
        discovery = TestDiscovery()
        
        # Test listing available tests
        tests = discovery.list_available_tests()
        self.assertIsInstance(tests, list)
        
        # Each test should have required fields
        for test in tests:
            self.assertIn('name', test)
            self.assertIn('module', test)
            self.assertIn('method', test)


class TestReporting(TestCase):
    """Test the result reporting functionality."""
    
    def test_json_reporting(self):
        """Test JSON result formatting."""
        # Create a test result with some data
        result = TestResult()
        result.startTestRun()
        result.tests_run = 3
        result.addFailure("test1", {"message": "Failed", "type": "AssertionError"})
        result.addError("test2", {"message": "Error", "type": "Exception"}) 
        result.addSkip("test3", "Skipped for testing")
        result.stopTestRun()
        
        # Format as JSON
        formatted = format_test_results(result, 'json')
        
        self.assertEqual(formatted['format'], 'json')
        self.assertIn('summary', formatted)
        self.assertIn('failures', formatted)
        self.assertIn('errors', formatted)
        self.assertIn('skipped', formatted)
        
        # Check content
        self.assertEqual(len(formatted['failures']), 1)
        self.assertEqual(len(formatted['errors']), 1)
        self.assertEqual(len(formatted['skipped']), 1)
        
    def test_text_reporting(self):
        """Test text result formatting."""
        result = TestResult()
        result.startTestRun()
        result.tests_run = 1
        result.addSuccess("test1")
        result.stopTestRun()
        
        formatted = format_test_results(result, 'text')
        
        self.assertEqual(formatted['format'], 'text')
        self.assertIn('text', formatted)
        self.assertIn('WHK Test Results', formatted['text'])
        self.assertIn('Tests run: 1', formatted['text'])


# Test functions for discovery
def test_simple_assertion():
    """Simple test function to test discovery."""
    assert 1 == 1, "One should equal one"


def test_math_operations():
    """Test basic math operations.""" 
    assert 2 + 2 == 4, "Addition should work"
    assert 10 - 5 == 5, "Subtraction should work"
    assert 3 * 4 == 12, "Multiplication should work"


def test_string_operations():
    """Test string operations."""
    test_str = "hello world"
    assert "hello" in test_str, "Substring should be found"
    assert test_str.upper() == "HELLO WORLD", "String conversion should work"
    assert len(test_str) == 11, "String length should be correct"