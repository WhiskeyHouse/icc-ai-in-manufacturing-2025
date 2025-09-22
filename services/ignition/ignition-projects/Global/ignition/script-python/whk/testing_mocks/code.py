"""WHK Testing Mocks
Mock implementations of Ignition system functions for isolated testing.
Allows testing without actual tag operations or system dependencies.
"""

from java.util import Date
from com.inductiveautomation.ignition.common.util import LoggerEx

logger = LoggerEx.newBuilder().name("WHK.Testing.Mocks").build()


class MockQualifiedValue(object):
    """Mock implementation of QualifiedValue for tag operations."""
    
    def __init__(self, value, quality='Good', timestamp=None):
        self.value = value
        self.quality = quality
        self.timestamp = timestamp or Date()
        
    def getValue(self):
        return self.value
        
    def getQuality(self):
        return self.quality
        
    def getTimestamp(self):
        return self.timestamp


class MockTagSystem(object):
    """Mock implementation of system.tag functions."""
    
    def __init__(self):
        self.tag_values = {}
        self.write_log = []
        self.read_log = []
        
    def read(self, tag_paths):
        """Mock tag read operation."""
        if isinstance(tag_paths, str):
            tag_paths = [tag_paths]
            
        self.read_log.append(tag_paths)
        
        results = []
        for path in tag_paths:
            value = self.tag_values.get(path, 0)
            results.append(MockQualifiedValue(value))
            
        return results[0] if len(results) == 1 else results
        
    def readBlocking(self, tag_paths, timeout=5000):
        """Mock blocking tag read."""
        return self.read(tag_paths)
        
    def write(self, tag_paths, values):
        """Mock tag write operation."""
        if isinstance(tag_paths, str):
            tag_paths = [tag_paths]
            values = [values]
            
        self.write_log.append({'paths': tag_paths, 'values': values})
        
        for path, value in zip(tag_paths, values):
            self.tag_values[path] = value
            
        return True
        
    def writeBlocking(self, tag_paths, values, timeout=5000):
        """Mock blocking tag write."""
        return self.write(tag_paths, values)
        
    def configure(self, base_path, tag_definitions, collision_policy='a'):
        """Mock tag configuration."""
        results = []
        for tag_def in tag_definitions:
            path = "{}/{}".format(base_path, tag_def.get('name', 'unknown'))
            results.append({
                'path': path,
                'status': 'Success',
                'message': 'Mock tag created'
            })
            # Initialize with default value
            self.tag_values[path] = tag_def.get('value', 0)
            
        return results
        
    def set_tag_value(self, path, value):
        """Test helper to set tag values."""
        self.tag_values[path] = value
        
    def get_tag_value(self, path):
        """Test helper to get tag values."""
        return self.tag_values.get(path)
        
    def clear_logs(self):
        """Test helper to clear operation logs."""
        self.read_log.clear()
        self.write_log.clear()
        
    def get_read_log(self):
        """Test helper to get read operations."""
        return self.read_log
        
    def get_write_log(self):
        """Test helper to get write operations."""
        return self.write_log


class MockNetSystem(object):
    """Mock implementation of system.net functions."""
    
    def __init__(self):
        self.request_log = []
        self.responses = {}
        
    def httpGet(self, url, headers=None):
        """Mock HTTP GET request."""
        self.request_log.append({'method': 'GET', 'url': url, 'headers': headers})
        return self.responses.get(url, '{"status": "mock_response"}')
        
    def httpPost(self, url, headers=None, data=None):
        """Mock HTTP POST request."""
        self.request_log.append({'method': 'POST', 'url': url, 'headers': headers, 'data': data})
        return self.responses.get(url, '{"status": "mock_response"}')
        
    def set_response(self, url, response):
        """Test helper to set mock responses."""
        self.responses[url] = response
        
    def get_request_log(self):
        """Test helper to get request log."""
        return self.request_log
        
    def clear_log(self):
        """Test helper to clear request log."""
        self.request_log.clear()


class MockUtilSystem(object):
    """Mock implementation of system.util functions."""
    
    def jsonEncode(self, obj):
        """Mock JSON encoding."""
        import json
        return json.dumps(obj)
        
    def jsonDecode(self, json_str):
        """Mock JSON decoding."""
        import json
        return json.loads(json_str)


class MockSecuritySystem(object):
    """Mock implementation of system.security functions."""
    
    def __init__(self):
        self.current_user = 'test_user'
        self.user_roles = ['TestRole']
        
    def getUserName(self):
        """Get current user name."""
        return self.current_user
        
    def getUserRoles(self, username=None):
        """Get user roles."""
        return self.user_roles
        
    def isScreenLocked(self):
        """Check if screen is locked."""
        return False
        
    def set_current_user(self, username):
        """Test helper to set current user."""
        self.current_user = username
        
    def set_user_roles(self, roles):
        """Test helper to set user roles."""
        self.user_roles = roles


class MockSystemContext(object):
    """Complete mock of Ignition system module."""
    
    def __init__(self):
        self.tag = MockTagSystem()
        self.net = MockNetSystem()
        self.util = MockUtilSystem()
        self.security = MockSecuritySystem()
        
    def reset_all_mocks(self):
        """Reset all mock objects to initial state."""
        self.tag = MockTagSystem()
        self.net = MockNetSystem()
        self.util = MockUtilSystem()
        self.security = MockSecuritySystem()


# Global mock system instance
mock_system = MockSystemContext()


class MockManager(object):
    """Manages mock activation and restoration."""
    
    def __init__(self):
        self.original_system = None
        self.mocks_active = False
        
    def activate_mocks(self):
        """Replace system module with mocks."""
        if self.mocks_active:
            return
            
        try:
            import sys
            self.original_system = sys.modules.get('system')
            sys.modules['system'] = mock_system
            
            # Also replace global system if it exists
            import __builtin__
            if hasattr(__builtin__, 'system'):
                setattr(__builtin__, '_original_system', __builtin__.system)
                setattr(__builtin__, 'system', mock_system)
                
            self.mocks_active = True
            logger.info("Mock system activated")
            
        except Exception as e:
            logger.error("Failed to activate mocks: {}".format(e))
            
    def deactivate_mocks(self):
        """Restore original system module."""
        if not self.mocks_active:
            return
            
        try:
            import sys
            if self.original_system:
                sys.modules['system'] = self.original_system
            elif 'system' in sys.modules:
                del sys.modules['system']
                
            # Restore global system
            import __builtin__
            if hasattr(__builtin__, '_original_system'):
                setattr(__builtin__, 'system', __builtin__._original_system)
                delattr(__builtin__, '_original_system')
                
            self.mocks_active = False
            logger.info("Mock system deactivated")
            
        except Exception as e:
            logger.error("Failed to deactivate mocks: {}".format(e))
            
    def reset_mocks(self):
        """Reset all mock objects to initial state."""
        mock_system.reset_all_mocks()
        logger.info("Mock system reset")
        
    def is_active(self):
        """Check if mocks are currently active."""
        return self.mocks_active


# Global mock manager
mock_manager = MockManager()


def with_mocks(test_func):
    """Decorator to run a test with mocks activated."""
    def wrapper(*args, **kwargs):
        mock_manager.activate_mocks()
        try:
            return test_func(*args, **kwargs)
        finally:
            mock_manager.deactivate_mocks()
    return wrapper


def setup_test_tags(tag_configs):
    """Helper to set up test tag values."""
    for path, value in tag_configs.items():
        mock_system.tag.set_tag_value(path, value)


def setup_test_responses(url_responses):
    """Helper to set up test HTTP responses."""
    for url, response in url_responses.items():
        mock_system.net.set_response(url, response)


def assert_tag_written(test_case, tag_path, expected_value):
    """Assert that a tag was written with expected value."""
    write_log = mock_system.tag.get_write_log()
    
    for entry in write_log:
        if tag_path in entry['paths']:
            index = entry['paths'].index(tag_path)
            actual_value = entry['values'][index]
            test_case.assertEqual(actual_value, expected_value, 
                                "Tag {} not written with expected value".format(tag_path))
            return
            
    test_case.fail("Tag {} was not written".format(tag_path))


def assert_tag_read(test_case, tag_path):
    """Assert that a tag was read."""
    read_log = mock_system.tag.get_read_log()
    
    for entry in read_log:
        if tag_path in entry:
            return
            
    test_case.fail("Tag {} was not read".format(tag_path))


def assert_http_called(test_case, url, method='GET'):
    """Assert that an HTTP request was made."""
    request_log = mock_system.net.get_request_log()
    
    for entry in request_log:
        if entry['url'] == url and entry['method'] == method:
            return
            
    test_case.fail("HTTP {} request to {} was not made".format(method, url))