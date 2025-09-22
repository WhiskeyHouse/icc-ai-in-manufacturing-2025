"""WebDev GET Handler for WHK Testing API.
Provides test discovery and result retrieval endpoints.
"""

import system
from java.util import Date
from com.inductiveautomation.ignition.common.util import LoggerEx

import whk.testing_discovery

logger = LoggerEx.newBuilder().name("WHK.Testing.WebDev").build()

# Import test results store from doPost
try:
    from doPost import test_results_store
except ImportError:
    test_results_store = {}


def doGet(request, session):
    """Handle GET requests for test discovery and results."""
    path_info = request.get('pathInfo', '') or ''
    
    # GET /testing/discover - List available tests
    if path_info == '/discover':
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
    
    # GET /testing/results - List available test result sessions
    elif path_info == '/results':
        try:
            sessions = []
            for session_id, data in test_results_store.items():
                summary = data['results'].get('summary', {})
                sessions.append({
                    'session_id': session_id,
                    'timestamp': data['timestamp'],
                    'success': data['results'].get('success', False),
                    'tests_run': summary.get('tests_run', 0),
                    'failures': summary.get('failures', 0),
                    'errors': summary.get('errors', 0)
                })
            
            # Sort by timestamp (newest first)
            sessions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return {
                'json': {
                    'sessions': sessions,
                    'count': len(sessions)
                }
            }
        except Exception as e:
            logger.error("Failed to list test results: {}".format(e))
            return {
                'json': {
                    'error': 'Failed to list test results: {}'.format(str(e))
                },
                'response_code': 500
            }
    
    # GET /testing/results/{session_id} - Get specific test results
    elif path_info.startswith('/results/'):
        session_id = path_info[9:]  # Remove '/results/' prefix
        
        if session_id in test_results_store:
            return {'json': test_results_store[session_id]}
        else:
            return {
                'json': {
                    'error': 'Test results not found for session: {}'.format(session_id)
                },
                'response_code': 404
            }
    
    # GET /testing/health - Service health check
    elif path_info == '/health':
        try:
            # Test basic functionality
            tests = whk.testing_discovery.list_tests()
            test_count = len(tests)
            
            return {
                'json': {
                    'status': 'healthy',
                    'test_framework': 'whk.testing',
                    'discovered_tests': test_count,
                    'stored_results': len(test_results_store),
                    'timestamp': str(Date())
                }
            }
        except Exception as e:
            logger.error("Health check failed: {}".format(e))
            return {
                'json': {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': str(Date())
                },
                'response_code': 500
            }
    
    # GET /testing/info/{test_name} - Get test metadata
    elif path_info.startswith('/info/'):
        test_name = path_info[6:]  # Remove '/info/' prefix
        
        try:
            test_info = whk.testing_discovery.get_test_info(test_name)
            return {'json': test_info}
        except Exception as e:
            logger.error("Failed to get test info for {}: {}".format(test_name, e))
            return {
                'json': {
                    'error': 'Failed to get test info: {}'.format(str(e))
                },
                'response_code': 500
            }
    
    # GET /testing - API documentation
    elif path_info == '' or path_info == '/':
        return {
            'json': {
                'service': 'WHK Testing Framework API',
                'version': '1.0.0',
                'endpoints': {
                    'GET /testing/discover': 'List all available tests',
                    'GET /testing/results': 'List test result sessions',
                    'GET /testing/results/{session_id}': 'Get specific test results',
                    'GET /testing/health': 'Service health check',
                    'GET /testing/info/{test_name}': 'Get test metadata',
                    'POST /testing/run': 'Execute tests',
                    'POST /testing/discover': 'Refresh test discovery',
                    'POST /testing/validate': 'Validate test syntax'
                },
                'examples': {
                    'run_single_test': {
                        'method': 'POST',
                        'url': '/testing/run',
                        'body': {'test_name': 'whk.tests.test_validation.test_script_validation'}
                    },
                    'run_module_tests': {
                        'method': 'POST',
                        'url': '/testing/run',
                        'body': {'module_path': 'whk.tests.test_validation'}
                    },
                    'run_all_tests': {
                        'method': 'POST',
                        'url': '/testing/run',
                        'body': {'run_all': True}
                    }
                },
                'timestamp': str(Date())
            }
        }
    
    # Unknown endpoint
    return {
        'json': {
            'error': 'Endpoint not found',
            'path': path_info,
            'available_endpoints': [
                '/discover',
                '/results',
                '/results/{session_id}',
                '/health',
                '/info/{test_name}',
                '/'
            ]
        },
        'response_code': 404
    }