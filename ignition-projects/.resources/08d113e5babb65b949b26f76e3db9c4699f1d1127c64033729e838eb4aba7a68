"""WebDev POST Handler for WHK Validation API."""

import json
import system
from java.util import Date

import whk.validation


def _parse_json(payload):
    if not payload:
        return {}
    return json.loads(payload)


def _resolve_validation_mode(mode):
    normalized = (mode or 'local').lower()
    if normalized in ('local', 'rules', 'rules_engine', 'auto'):
        return normalized
    return 'local'


def _run_script_validation(script_content, context, metadata, mode):
    if mode == 'rules' or mode == 'rules_engine':
        return whk.validation.validate_script_with_rules_engine(
            script_content,
            context,
            metadata,
            fallback_to_local=(mode != 'rules_engine')
        )
    if mode == 'auto':
        return whk.validation.validate_script_with_rules_engine(
            script_content,
            context,
            metadata,
            fallback_to_local=True
        )
    return whk.validation.validate_script_local(script_content, context)


def _run_component_validation(component_config, context, metadata, mode):
    if mode == 'rules' or mode == 'rules_engine':
        return whk.validation.validate_component_with_rules_engine(
            component_config,
            context,
            metadata,
            fallback_to_local=(mode != 'rules_engine')
        )
    if mode == 'auto':
        return whk.validation.validate_component_with_rules_engine(
            component_config,
            context,
            metadata,
            fallback_to_local=True
        )
    return whk.validation.validate_component_local(component_config, context)


def doPost(request, session):
    """Handle POST requests for validation API."""
    path_info = request.get('pathInfo', '') or ''

    try:
        data = _parse_json(request.get('postData', ''))
    except Exception:
        return {
            'json': {'error': 'Invalid JSON in request body'},
            'response_code': 400
        }

    if path_info == '/scripts':
        script_content = data.get('script')
        if not script_content:
            return {
                'json': {'error': 'script field is required'},
                'response_code': 400
            }

        context = data.get('context', {}) if isinstance(data.get('context', {}), dict) else {}
        metadata = data.get('metadata', {}) if isinstance(data.get('metadata', {}), dict) else {}
        session_id = data.get('session_id')
        create_session_flag = data.get('create_session', True)
        mode = _resolve_validation_mode(data.get('mode'))

        validation_result = _run_script_validation(script_content, context, metadata, mode)

        session_record = None
        if create_session_flag:
            session_record = whk.validation.create_validation_session(
                'script',
                script_content,
                validation_result,
                context,
                session_id,
                metadata
            )

        response_payload = dict(validation_result)
        if session_record:
            response_payload['session_id'] = session_record['session_id']
            response_payload['session'] = session_record

        return {'json': response_payload}

    if path_info == '/components':
        component_config = data.get('component')
        if not component_config:
            return {
                'json': {'error': 'component field is required'},
                'response_code': 400
            }

        context = data.get('context', {}) if isinstance(data.get('context', {}), dict) else {}
        metadata = data.get('metadata', {}) if isinstance(data.get('metadata', {}), dict) else {}
        session_id = data.get('session_id')
        create_session_flag = data.get('create_session', False)
        mode = _resolve_validation_mode(data.get('mode'))

        validation_result = _run_component_validation(component_config, context, metadata, mode)

        session_record = None
        if create_session_flag:
            session_record = whk.validation.create_validation_session(
                'component',
                component_config,
                validation_result,
                context,
                session_id,
                metadata
            )

        payload = {
            'component_type': component_config.get('type', 'unknown') if isinstance(component_config, dict) else 'unknown',
            'validation_result': validation_result,
            'timestamp': str(Date())
        }

        if session_record:
            payload['session_id'] = session_record['session_id']
            payload['session'] = session_record

        return {'json': payload}

    if path_info == '/tags':
        tag_definitions = data.get('tags')
        if not tag_definitions or not isinstance(tag_definitions, list):
            return {
                'json': {'error': 'tags must be a list of tag definitions'},
                'response_code': 400
            }

        base_path = data.get('basePath', '')
        collision_policy = data.get('collisionPolicy', 'a')
        metadata = data.get('metadata', {}) if isinstance(data.get('metadata', {}), dict) else {}

        try:
            configure_result = system.tag.configure(base_path, tag_definitions, collision_policy)
            normalized = whk.validation.normalize_tag_config_results(configure_result)
        except Exception as exc:
            return {
                'json': {
                    'error': 'Failed to create tags',
                    'message': str(exc)
                },
                'response_code': 500
            }

        return {
            'json': {
                'operation': 'create',
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
            'available_endpoints': ['/scripts', '/components', '/tags']
        },
        'response_code': 404
    }
