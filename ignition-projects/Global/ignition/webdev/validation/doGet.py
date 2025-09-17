"""WebDev GET Handler for WHK Validation API."""

import whk.validation


def doGet(request, session):
    """Handle GET requests for validation endpoints."""
    path_info = request.get('pathInfo', '') or ''

    if not path_info or path_info == '/':
        return {
            'json': {
                'service': 'WHK Validation API',
                'version': '1.0.0',
                'description': 'REST API for Jython script and Perspective component validation',
                'endpoints': {
                    'GET /health': 'Check service health',
                    'GET /sessions': 'List all validation sessions',
                    'GET /sessions/{id}': 'Get specific validation session',
                    'POST /scripts': 'Validate Jython script',
                    'POST /components': 'Validate Perspective component',
                    'POST /tags': 'Create Ignition tags',
                    'PATCH /sessions/{id}': 'Update validation session',
                    'PATCH /tags': 'Update Ignition tags'
                },
                'integration': {
                    'rules_engine': 'http://host.docker.internal:8087',
                    'project': 'Global (inheritable)',
                    'module': 'whk.validation'
                }
            }
        }

    if path_info == '/health':
        return {'json': whk.validation.get_service_health()}

    if path_info == '/sessions':
        sessions = whk.validation.list_validation_sessions()
        return {
            'json': {
                'sessions': sessions,
                'total': len(sessions)
            }
        }

    if path_info.startswith('/sessions/'):
        session_id = path_info.replace('/sessions/', '').strip()
        if not session_id:
            return {
                'json': {'error': 'Session ID is required'},
                'response_code': 400
            }

        session_data = whk.validation.get_validation_session(session_id)
        if session_data:
            return {'json': session_data}

        return {
            'json': {'error': 'Session not found', 'session_id': session_id},
            'response_code': 404
        }

    return {
        'json': {
            'error': 'Endpoint not found',
            'path': path_info,
            'available_endpoints': ['/health', '/sessions', '/sessions/{id}']
        },
        'response_code': 404
    }
