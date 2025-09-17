"""WebDev PATCH Handler for WHK Validation API."""

import json
import system
from java.util import Date

import whk.validation


def _parse_json(payload):
    if not payload:
        return {}
    return json.loads(payload)


def doPatch(request, session):
    """Handle PATCH requests for validation API."""
    path_info = request.get('pathInfo', '') or ''

    try:
        data = _parse_json(request.get('postData', ''))
    except Exception:
        return {
            'json': {'error': 'Invalid JSON in request body'},
            'response_code': 400
        }

    if path_info.startswith('/sessions/'):
        session_id = path_info.replace('/sessions/', '').strip()
        if not session_id:
            return {
                'json': {'error': 'Session ID is required'},
                'response_code': 400
            }

        existing = whk.validation.get_validation_session(session_id)
        if not existing:
            return {
                'json': {'error': 'Session not found', 'session_id': session_id},
                'response_code': 404
            }

        script_updates = data.get('script_updates')
        component_updates = data.get('component_updates') or data.get('component')
        content = data.get('content')
        context = data.get('context') if isinstance(data.get('context'), dict) else None
        metadata = data.get('metadata') if isinstance(data.get('metadata'), dict) else None
        status = data.get('status')
        notes = data.get('notes')
        reviewer = data.get('reviewer')
        revalidate = bool(data.get('revalidate'))
        mode = data.get('mode', data.get('validation_mode', 'local'))

        updated_session = whk.validation.update_validation_session(
            session_id,
            script_updates=script_updates,
            component_updates=component_updates,
            content=content,
            context=context,
            metadata=metadata,
            status=status,
            notes=notes,
            reviewer=reviewer,
            revalidate=revalidate,
            validation_mode=mode
        )

        if not updated_session:
            return {
                'json': {'error': 'Failed to update session', 'session_id': session_id},
                'response_code': 500
            }

        return {
            'json': {
                'session_id': session_id,
                'updated_at': updated_session.get('updated_at'),
                'validation_result': updated_session.get('validation_result'),
                'status': updated_session.get('status'),
                'message': 'Session updated successfully'
            }
        }

    if path_info == '/tags':
        tag_definitions = data.get('tags')
        if not tag_definitions or not isinstance(tag_definitions, list):
            return {
                'json': {'error': 'tags must be a list of tag definitions'},
                'response_code': 400
            }

        base_path = data.get('basePath', '')
        collision_policy = data.get('collisionPolicy', 'm')
        metadata = data.get('metadata', {}) if isinstance(data.get('metadata', {}), dict) else {}

        try:
            configure_result = system.tag.configure(base_path, tag_definitions, collision_policy)
            normalized = whk.validation.normalize_tag_config_results(configure_result)
        except Exception as exc:
            return {
                'json': {
                    'error': 'Failed to update tags',
                    'message': str(exc)
                },
                'response_code': 500
            }

        return {
            'json': {
                'operation': 'update',
                'base_path': base_path,
                'collision_policy': collision_policy,
                'metadata': metadata,
                'results': normalized,
                'timestamp': str(Date())
            }
        }

    return {
        'json': {
            'error': 'Endpoint not found',
            'path': path_info,
            'available_endpoints': ['/sessions/{id}', '/tags']
        },
        'response_code': 404
    }
