"""WHK Testing Framework Core
Core unit testing framework for Ignition Jython scripts.
Provides TestCase class, assertions, and test runners compatible with Ignition environment.
"""

import sys
import traceback
from java.util import Date
from com.inductiveautomation.ignition.common.util import LoggerEx

logger = LoggerEx.newBuilder().name("WHK.Testing").build()


class AssertionError(Exception):
    """Custom assertion error for test failures."""
    pass


class TestResult(object):
    """Stores results from test execution."""
    
    def __init__(self):
        self.tests_run = 0
        self.failures = []
        self.errors = []
        self.skipped = []
        self.start_time = None
        self.end_time = None
        
    def startTest(self, test):
        """Called when test starts."""
        self.tests_run += 1
        
    def addSuccess(self, test):
        """Called when test passes."""
        pass
        
    def addError(self, test, error_info):
        """Called when test has an error."""
        self.errors.append((test, error_info))
        
    def addFailure(self, test, failure_info):
        """Called when test fails assertion."""
        self.failures.append((test, failure_info))
        
    def addSkip(self, test, reason):
        """Called when test is skipped."""
        self.skipped.append((test, reason))
        
    def startTestRun(self):
        """Called when test run starts."""
        self.start_time = Date()
        
    def stopTestRun(self):
        """Called when test run ends."""
        self.end_time = Date()
        
    def wasSuccessful(self):
        """Return True if all tests passed."""
        return len(self.failures) == 0 and len(self.errors) == 0
        
    def summary(self):
        """Return summary dict of results."""
        duration = 0
        if self.start_time and self.end_time:
            duration = self.end_time.getTime() - self.start_time.getTime()
            
        return {
            'tests_run': self.tests_run,
            'failures': len(self.failures),
            'errors': len(self.errors),
            'skipped': len(self.skipped),
            'success': self.wasSuccessful(),
            'duration_ms': duration,
            'start_time': str(self.start_time) if self.start_time else None,
            'end_time': str(self.end_time) if self.end_time else None
        }


class TestCase(object):
    """Base class for writing unit tests in Ignition."""
    
    def __init__(self, method_name='runTest'):
        self.method_name = method_name
        self._test_method = getattr(self, method_name, None)
        
    def setUp(self):
        """Override to set up test fixtures."""
        pass
        
    def tearDown(self):
        """Override to clean up after tests."""
        pass
        
    def run(self, result=None):
        """Run this test case."""
        if result is None:
            result = TestResult()
            
        result.startTest(self)
        
        try:
            self.setUp()
        except Exception as e:
            result.addError(self, self._exc_info())
            return result
            
        try:
            if self._test_method:
                self._test_method()
            result.addSuccess(self)
        except AssertionError as e:
            result.addFailure(self, self._exc_info())
        except Exception as e:
            result.addError(self, self._exc_info())
        finally:
            try:
                self.tearDown()
            except Exception as e:
                result.addError(self, self._exc_info())
                
        return result
        
    def _exc_info(self):
        """Get current exception info."""
        exc_type = sys.exc_info()[0]
        exc_value = sys.exc_info()[1]
        exc_tb = traceback.format_exc()
        return {
            'type': str(exc_type.__name__) if exc_type else 'Unknown',
            'message': str(exc_value) if exc_value else '',
            'traceback': exc_tb
        }
        
    def __str__(self):
        return "{}.{}".format(self.__class__.__name__, self.method_name)
        
    # Assertion methods
    def assertEqual(self, first, second, msg=None):
        """Assert that two values are equal."""
        if first != second:
            error_msg = msg or "{} != {}".format(repr(first), repr(second))
            raise AssertionError(error_msg)
            
    def assertNotEqual(self, first, second, msg=None):
        """Assert that two values are not equal."""
        if first == second:
            error_msg = msg or "{} == {}".format(repr(first), repr(second))
            raise AssertionError(error_msg)
            
    def assertTrue(self, expr, msg=None):
        """Assert that expression is true."""
        if not expr:
            error_msg = msg or "{} is not true".format(repr(expr))
            raise AssertionError(error_msg)
            
    def assertFalse(self, expr, msg=None):
        """Assert that expression is false."""
        if expr:
            error_msg = msg or "{} is not false".format(repr(expr))
            raise AssertionError(error_msg)
            
    def assertIsNone(self, expr, msg=None):
        """Assert that expression is None."""
        if expr is not None:
            error_msg = msg or "{} is not None".format(repr(expr))
            raise AssertionError(error_msg)
            
    def assertIsNotNone(self, expr, msg=None):
        """Assert that expression is not None."""
        if expr is None:
            error_msg = msg or "Expression is None"
            raise AssertionError(error_msg)
            
    def assertIn(self, member, container, msg=None):
        """Assert that member is in container."""
        if member not in container:
            error_msg = msg or "{} not found in {}".format(repr(member), repr(container))
            raise AssertionError(error_msg)
            
    def assertNotIn(self, member, container, msg=None):
        """Assert that member is not in container."""
        if member in container:
            error_msg = msg or "{} found in {}".format(repr(member), repr(container))
            raise AssertionError(error_msg)
            
    def assertRaises(self, expected_exception, callable_obj=None, *args, **kwargs):
        """Assert that calling callable_obj raises expected_exception."""
        if callable_obj is None:
            return _AssertRaisesContext(expected_exception, self)
            
        try:
            callable_obj(*args, **kwargs)
        except expected_exception:
            return
        except Exception as e:
            raise AssertionError("Expected {} but got {}".format(
                expected_exception.__name__, e.__class__.__name__))
        else:
            raise AssertionError("Expected {} but no exception was raised".format(
                expected_exception.__name__))
                
    def assertAlmostEqual(self, first, second, places=7, msg=None):
        """Assert that two floats are equal within a tolerance."""
        if round(abs(second - first), places) != 0:
            error_msg = msg or "{} != {} within {} decimal places".format(
                first, second, places)
            raise AssertionError(error_msg)


class _AssertRaisesContext(object):
    """Context manager for assertRaises."""
    
    def __init__(self, expected, test_case):
        self.expected = expected
        self.test_case = test_case
        self.exception = None
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise AssertionError("{} not raised".format(exc_name))
            
        if not issubclass(exc_type, self.expected):
            return False
            
        self.exception = exc_value
        return True


class TestSuite(object):
    """Collection of test cases."""
    
    def __init__(self, tests=None):
        self._tests = tests or []
        
    def addTest(self, test):
        """Add a test case to the suite."""
        self._tests.append(test)
        
    def run(self, result=None):
        """Run all tests in the suite."""
        if result is None:
            result = TestResult()
            
        result.startTestRun()
        
        for test in self._tests:
            if hasattr(test, 'run'):
                test.run(result)
            else:
                logger.warn("Test {} does not have run method".format(test))
                
        result.stopTestRun()
        return result
        
    def countTestCases(self):
        """Return number of test cases."""
        return len(self._tests)
        
    def __iter__(self):
        return iter(self._tests)


class TestRunner(object):
    """Runs tests and provides formatted output."""
    
    def __init__(self, verbosity=1):
        self.verbosity = verbosity
        
    def run(self, test):
        """Run test or test suite."""
        result = TestResult()
        
        if hasattr(test, 'run'):
            test.run(result)
        else:
            logger.error("Test object does not have run method")
            
        self._print_results(result)
        return result
        
    def _print_results(self, result):
        """Print formatted test results."""
        summary = result.summary()
        
        if self.verbosity >= 1:
            logger.info("Ran {} tests in {}ms".format(
                summary['tests_run'], summary['duration_ms']))
                
            if summary['failures']:
                logger.warn("FAILURES: {}".format(summary['failures']))
                for test, failure in result.failures:
                    logger.warn("FAIL: {}".format(test))
                    logger.warn("  {}".format(failure['message']))
                    
            if summary['errors']:
                logger.error("ERRORS: {}".format(summary['errors']))
                for test, error in result.errors:
                    logger.error("ERROR: {}".format(test))
                    logger.error("  {}".format(error['message']))
                    
            if summary['success']:
                logger.info("ALL TESTS PASSED")
            else:
                logger.error("SOME TESTS FAILED")


def run_tests(test_module_or_function):
    """Convenience function to run tests."""
    runner = TestRunner(verbosity=2)
    
    if hasattr(test_module_or_function, '__call__'):
        suite = TestSuite()
        suite.addTest(test_module_or_function)
        return runner.run(suite)
    else:
        return runner.run(test_module_or_function)


def skip(reason):
    """Decorator to skip a test."""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            if hasattr(args[0], '_test_result'):
                args[0]._test_result.addSkip(args[0], reason)
                return
            raise Exception("Test skipped: {}".format(reason))
        return wrapper
    return decorator