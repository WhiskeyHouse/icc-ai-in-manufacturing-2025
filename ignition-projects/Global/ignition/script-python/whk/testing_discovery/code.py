"""WHK Test Discovery System
Automatically discovers and loads test functions from script modules.
Supports test_ prefix convention and flexible filtering.
"""

import system
from com.inductiveautomation.ignition.common.util import LoggerEx
from whk.testing_core import TestCase, TestSuite

logger = LoggerEx.newBuilder().name("WHK.Testing.Discovery").build()


class TestLoader(object):
    """Loads tests from script modules and functions."""
    
    def __init__(self):
        self.test_method_prefix = 'test_'
        self.test_case_suffix = 'Test'
        
    def loadTestsFromName(self, name):
        """Load tests from a dotted module.function name."""
        parts = name.split('.')
        
        if len(parts) < 2:
            logger.error("Invalid test name format: {}".format(name))
            return TestSuite()
            
        module_path = '.'.join(parts[:-1])
        function_name = parts[-1]
        
        try:
            module = self._import_module(module_path)
            if hasattr(module, function_name):
                test_func = getattr(module, function_name)
                if callable(test_func):
                    return self._function_to_test_case(test_func, function_name)
        except Exception as e:
            logger.error("Failed to load test {}: {}".format(name, e))
            
        return TestSuite()
        
    def loadTestsFromModule(self, module_path):
        """Load all test functions from a module."""
        try:
            module = self._import_module(module_path)
            return self._discover_tests_in_module(module, module_path)
        except Exception as e:
            logger.error("Failed to load module {}: {}".format(module_path, e))
            return TestSuite()
            
    def discoverTests(self, start_path='whk', pattern='test_*'):
        """Discover all tests under the start path."""
        suite = TestSuite()
        
        # Get all script modules
        try:
            modules = self._get_script_modules(start_path)
            
            for module_path in modules:
                if self._should_include_module(module_path, pattern):
                    module_suite = self.loadTestsFromModule(module_path)
                    if module_suite.countTestCases() > 0:
                        for test in module_suite:
                            suite.addTest(test)
                            
        except Exception as e:
            logger.error("Test discovery failed: {}".format(e))
            
        return suite
        
    def _import_module(self, module_path):
        """Import a script module by path."""
        try:
            # Try to import using Python's import mechanism
            parts = module_path.split('.')
            module = __import__(parts[0])
            
            for part in parts[1:]:
                module = getattr(module, part)
                
            return module
        except (ImportError, AttributeError):
            # Fall back to eval-based import for Ignition
            try:
                return eval(module_path)
            except:
                raise ImportError("Cannot import module: {}".format(module_path))
                
    def _discover_tests_in_module(self, module, module_path):
        """Find test functions and classes in a module."""
        suite = TestSuite()
        
        # Look for functions starting with test_
        for attr_name in dir(module):
            if attr_name.startswith(self.test_method_prefix):
                attr = getattr(module, attr_name)
                if callable(attr):
                    test_case = self._function_to_test_case(attr, attr_name, module_path)
                    suite.addTest(test_case)
                    
        # Look for TestCase subclasses
        for attr_name in dir(module):
            if attr_name.endswith(self.test_case_suffix):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, TestCase) and 
                    attr != TestCase):
                    
                    # Find test methods in the class
                    for method_name in dir(attr):
                        if method_name.startswith(self.test_method_prefix):
                            test_instance = attr(method_name)
                            suite.addTest(test_instance)
                            
        return suite
        
    def _function_to_test_case(self, test_func, func_name, module_path=None):
        """Convert a test function to a TestCase instance."""
        class FunctionTestCase(TestCase):
            def __init__(self, test_function, test_name):
                super(FunctionTestCase, self).__init__()
                self._test_function = test_function
                self._test_name = test_name
                self.method_name = test_name
                
            def runTest(self):
                return self._test_function()
                
            def __str__(self):
                if module_path:
                    return "{}.{}".format(module_path, self._test_name)
                return self._test_name
                
        return FunctionTestCase(test_func, func_name)
        
    def _get_script_modules(self, start_path):
        """Get list of available script modules under start_path."""
        modules = []
        
        # This is a simplified version - in a real implementation,
        # you'd need to traverse the Ignition script library structure
        # For now, we'll return known test modules
        known_modules = [
            'whk.test_validation',
            'whk.test_batch_control', 
            'whk.test_framework',
            'whk.test_scripts.good',
            'whk.test_scripts.bad'
        ]
        
        for module in known_modules:
            if module.startswith(start_path):
                modules.append(module)
                
        return modules
        
    def _should_include_module(self, module_path, pattern):
        """Check if module should be included based on pattern."""
        if pattern == 'test_*':
            # Include modules with 'test' in the name
            return 'test' in module_path.lower()
        else:
            # Simple pattern matching
            return pattern.replace('*', '') in module_path


class TestDiscovery(object):
    """Main interface for test discovery."""
    
    def __init__(self):
        self.loader = TestLoader()
        
    def discover_all_tests(self):
        """Discover all available tests."""
        return self.loader.discoverTests()
        
    def discover_tests_in_module(self, module_path):
        """Discover tests in a specific module."""
        return self.loader.loadTestsFromModule(module_path)
        
    def discover_specific_test(self, test_name):
        """Discover a specific test by name."""
        return self.loader.loadTestsFromName(test_name)
        
    def list_available_tests(self):
        """Return list of available test names."""
        suite = self.discover_all_tests()
        tests = []
        
        for test in suite:
            tests.append({
                'name': str(test),
                'module': getattr(test, '__module__', 'unknown'),
                'method': getattr(test, 'method_name', 'unknown')
            })
            
        return tests
        
    def get_test_metadata(self, test_name):
        """Get metadata about a specific test."""
        try:
            suite = self.discover_specific_test(test_name)
            if suite.countTestCases() > 0:
                test = list(suite)[0]
                return {
                    'name': str(test),
                    'module': getattr(test, '__module__', 'unknown'),
                    'method': getattr(test, 'method_name', 'unknown'),
                    'docstring': getattr(test._test_function if hasattr(test, '_test_function') else test._test_method, '__doc__', None),
                    'exists': True
                }
        except Exception as e:
            logger.warn("Failed to get metadata for {}: {}".format(test_name, e))
            
        return {
            'name': test_name,
            'exists': False,
            'error': 'Test not found or failed to load'
        }


# Global discovery instance
discovery = TestDiscovery()


def discover_tests(module_path=None, test_name=None):
    """Convenience function for test discovery."""
    if test_name:
        return discovery.discover_specific_test(test_name)
    elif module_path:
        return discovery.discover_tests_in_module(module_path)
    else:
        return discovery.discover_all_tests()


def list_tests():
    """List all available tests."""
    return discovery.list_available_tests()


def get_test_info(test_name):
    """Get information about a specific test."""
    return discovery.get_test_metadata(test_name)