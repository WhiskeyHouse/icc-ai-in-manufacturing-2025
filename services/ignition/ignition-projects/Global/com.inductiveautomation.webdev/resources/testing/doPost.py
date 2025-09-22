"""WebDev POST Handler for WHK Testing API.
Executes unit tests and returns results.
"""

import json
import system
from java.util import Date
from com.inductiveautomation.ignition.common.util import LoggerEx

import whk.testing_core
import whk.testing_discovery

logger = LoggerEx.newBuilder().name("WHK.Testing.WebDev").build()

# Store test results for retrieval
test_results_store = {}


def _parse_json(payload):
    """Parse JSON payload with error handling."""
    if not payload:
        return {}
    try:
        return json.loads(payload)
    except Exception as e:
        logger.error("JSON parse error: {}".format(e))
        return {}


def _generate_session_id():
    """Generate unique session ID for test run."""
    return "test_run_{}".format(Date().getTime())


def _store_test_results(session_id, results):
    """Store test results for later retrieval."""
    test_results_store[session_id] = {
        'results': results,
        'timestamp': str(Date()),
        'session_id': session_id
    }
    
    # Clean up old results (keep last 50)
    if len(test_results_store) > 50:
        oldest_key = min(test_results_store.keys())
        del test_results_store[oldest_key]


def _run_single_test(test_name):
    """Run a single test by name."""
    try:
        suite = whk.testing_discovery.discover_tests(test_name=test_name)
        
        if suite.countTestCases() == 0:
            return {
                'success': False,
                'error': 'Test not found: {}'.format(test_name),
                'test_name': test_name
            }
            
        runner = whk.testing_core.TestRunner(verbosity=1)
        result = runner.run(suite)
        
        return {
            'success': result.wasSuccessful(),
            'test_name': test_name,
            'summary': result.summary(),
            'failures': [{'test': str(test), 'details': failure} for test, failure in result.failures],
            'errors': [{'test': str(test), 'details': error} for test, error in result.errors],
            'skipped': [{'test': str(test), 'reason': reason} for test, reason in result.skipped]
        }
        
    except Exception as e:
        logger.error("Error running test {}: {}".format(test_name, e))
        return {
            'success': False,
            'error': str(e),
            'test_name': test_name
        }


def _run_module_tests(module_path):
    """Run all tests in a module."""
    try:
        suite = whk.testing_discovery.discover_tests(module_path=module_path)
        
        if suite.countTestCases() == 0:
            return {
                'success': False,
                'error': 'No tests found in module: {}'.format(module_path),
                'module_path': module_path
            }
            
        runner = whk.testing_core.TestRunner(verbosity=1)
        result = runner.run(suite)
        
        return {
            'success': result.wasSuccessful(),
            'module_path': module_path,
            'summary': result.summary(),
            'failures': [{'test': str(test), 'details': failure} for test, failure in result.failures],
            'errors': [{'test': str(test), 'details': error} for test, error in result.errors],
            'skipped': [{'test': str(test), 'reason': reason} for test, reason in result.skipped]
        }
        
    except Exception as e:
        logger.error("Error running module tests {}: {}".format(module_path, e))
        return {
            'success': False,
            'error': str(e),
            'module_path': module_path
        }


def _run_all_tests():
    """Run all discovered tests."""
    try:
        suite = whk.testing_discovery.discover_tests()
        
        if suite.countTestCases() == 0:
            return {
                'success': False,
                'error': 'No tests found',
                'scope': 'all'
            }
            
        runner = whk.testing_core.TestRunner(verbosity=1)
        result = runner.run(suite)
        
        return {
            'success': result.wasSuccessful(),
            'scope': 'all',
            'summary': result.summary(),
            'failures': [{'test': str(test), 'details': failure} for test, failure in result.failures],
            'errors': [{'test': str(test), 'details': error} for test, error in result.errors],
            'skipped': [{'test': str(test), 'reason': reason} for test, reason in result.skipped]
        }
        
    except Exception as e:
        logger.error("Error running all tests: {}".format(e))
        return {
            'success': False,
            'error': str(e),
            'scope': 'all'
        }


def doPost(request, session):
    """Handle POST requests for test execution."""
    path_info = request.get('pathInfo', '') or ''
    
    try:
        data = _parse_json(request.get('postData', ''))
    except Exception:
        return {
            'json': {'error': 'Invalid JSON in request body'},
            'response_code': 400
        }
    
    # POST /testing/run - Execute tests
    if path_info == '/run':
        test_name = data.get('test_name')
        module_path = data.get('module_path')
        run_all = data.get('run_all', False)
        store_results = data.get('store_results', True)
        
        session_id = _generate_session_id()
        start_time = Date()
        
        # Determine what to run
        if test_name:
            results = _run_single_test(test_name)
        elif module_path:
            results = _run_module_tests(module_path)
        elif run_all:
            results = _run_all_tests()
        else:
            return {
                'json': {
                    'error': 'Must specify test_name, module_path, or run_all=true'
                },
                'response_code': 400
            }
        
        # Add execution metadata
        end_time = Date()
        results['session_id'] = session_id
        results['execution_time'] = {
            'start': str(start_time),
            'end': str(end_time),
            'duration_ms': end_time.getTime() - start_time.getTime()
        }
        
        # Store results if requested
        if store_results:
            _store_test_results(session_id, results)
        
        return {'json': results}
    
    # POST /testing/discover - Refresh test discovery
    elif path_info == '/discover':
        try:
            tests = whk.testing_discovery.list_tests()
            return {
                'json': {
                    'tests': tests,
                    'count': len(tests),
                    'timestamp': str(Date())
                }
            }
        except Exception as e:
            logger.error("Test discovery failed: {}".format(e))
            return {
                'json': {
                    'error': 'Test discovery failed: {}'.format(str(e))
                },
                'response_code': 500
            }
    
    # POST /testing/validate - Validate test syntax without running
    elif path_info == '/validate':
        test_name = data.get('test_name')
        if not test_name:
            return {
                'json': {'error': 'test_name is required'},
                'response_code': 400
            }
        
        try:
            test_info = whk.testing_discovery.get_test_info(test_name)
            return {'json': test_info}
        except Exception as e:
            logger.error("Test validation failed: {}".format(e))
            return {
                'json': {
                    'error': 'Test validation failed: {}'.format(str(e))
                },
                'response_code': 500
            }
    
    # Unknown endpoint
    return {
        'json': {
            'error': 'Endpoint not found',
            'path': path_info,
            'available_endpoints': ['/run', '/discover', '/validate']
        },
        'response_code': 404
    }