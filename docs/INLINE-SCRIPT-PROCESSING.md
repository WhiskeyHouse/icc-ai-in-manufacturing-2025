# Inline Script Processing Guidelines for Ignition AI Development

## Overview

This document provides comprehensive guidelines for processing inline Jython scripts within Ignition components, focusing on proper escape sequence handling, syntax validation, context-aware processing, and integration with AI code generation workflows. These guidelines ensure AI-generated inline scripts are production-ready and integrate seamlessly with Ignition's execution environments.

## 🎯 Inline Script Processing Objectives

### Primary Goals
- **Accurate Escape Processing**: Handle JSON escape sequences correctly for embedded Jython code
- **Context-Aware Validation**: Validate scripts based on their execution context (Gateway, Client, Perspective)
- **Syntax Verification**: Ensure generated scripts compile and execute correctly in Jython 2.7
- **Performance Optimization**: Generate efficient scripts that don't impact UI responsiveness
- **Security Compliance**: Enforce security best practices for inline script execution

### Critical Requirements
- **Escape Sequence Integrity**: Maintain proper \\n, \\t, \\", \\\\ handling in JSON-embedded scripts
- **Execution Context Awareness**: Different validation for button events vs transform scripts vs timer scripts
- **Import Validation**: Ensure all imports are available in the target execution context
- **Error Handling**: Proper exception handling patterns for production robustness

## 📝 Script Context Categories

### 1. Component Event Scripts

#### Button Action Scripts

Component event scripts execute in response to user interactions and require specific patterns for reliability and security.

```python
# Example: Production-grade button action script with proper escaping
def generate_button_action_script(action_config: Dict[str, Any]) -> str:
    """Generate button action script with proper error handling and logging"""
    
    python_script = f'''def runAction(self, event):
    """
    {action_config.get('description', 'Button action handler')}
    
    Args:
        self: Component reference
        event: Action event object
    """
    import system.util
    import system.tag
    
    logger = system.util.getLogger("ButtonAction.{action_config.get('component_name', 'Unknown')}")
    
    try:
        # Get user context for security
        username = system.security.getUsername()
        user_roles = system.security.getUserRoles(username)
        
        # Check permissions
        required_roles = {action_config.get('required_roles', ['Operators'])}
        if not any(role in user_roles for role in required_roles):
            logger.warning("User {{}} lacks required roles for action".format(username))
            system.gui.messageBox("Insufficient permissions for this action", "Access Denied")
            return
        
        # Perform action based on configuration
        action_type = "{action_config.get('action_type', 'tag_write')}"
        
        if action_type == "tag_write":
            tag_path = "{action_config.get('tag_path', '[default]Equipment/Unknown/Command')}"
            tag_value = {action_config.get('tag_value', 'True')}
            
            # Validate tag exists before writing
            tag_exists = system.tag.exists(tag_path)
            if not tag_exists:
                logger.error("Target tag does not exist: {{}}".format(tag_path))
                system.gui.messageBox("Configuration error: Invalid tag path", "Error")
                return
            
            # Write tag with confirmation if required
            confirm_required = {str(action_config.get('require_confirmation', 'True')).lower()}
            if confirm_required == "true":
                confirm_msg = "{action_config.get('confirmation_message', 'Execute this action?')}"
                result = system.gui.confirm(confirm_msg, "Confirm Action")
                if not result:
                    logger.info("User cancelled action")
                    return
            
            # Execute tag write
            success = system.tag.writeBlocking([tag_path], [tag_value])
            if success:
                logger.info("Tag write successful: {{}} = {{}}".format(tag_path, tag_value))
                
                # Update UI feedback if specified
                feedback_component = "{action_config.get('feedback_component', '')}"
                if feedback_component:
                    feedback_msg = "{action_config.get('success_message', 'Action completed successfully')}"
                    self.getSibling(feedback_component).props.text = feedback_msg
            else:
                logger.error("Tag write failed: {{}}".format(tag_path))
                system.gui.messageBox("Failed to execute action", "Error")
        
        elif action_type == "navigate":
            view_path = "{action_config.get('target_view', '/main/overview')}"
            params = {action_config.get('view_params', '{}')}
            
            logger.info("Navigating to view: {{}}".format(view_path))
            system.perspective.navigate(view=view_path, params=params)
        
        elif action_type == "popup":
            popup_id = "{action_config.get('popup_id', 'actionPopup')}"
            view_path = "{action_config.get('popup_view', '/popups/confirmation')}"
            params = {action_config.get('popup_params', '{}')}
            
            logger.info("Opening popup: {{}}".format(view_path))
            system.perspective.openPopup(id=popup_id, view=view_path, params=params)
        
        else:
            logger.error("Unknown action type: {{}}".format(action_type))
            system.gui.messageBox("Configuration error: Unknown action type", "Error")
    
    except Exception as e:
        logger.error("Button action error: {{}}".format(str(e)))
        system.gui.messageBox("An error occurred while executing the action", "Error")
        
        # Optional: Send error to monitoring system
        try:
            system.util.sendMessage(
                project="ErrorMonitoring",
                messageHandler="logError",
                payload={{
                    "component": "{action_config.get('component_name', 'Unknown')}",
                    "error": str(e),
                    "user": system.security.getUsername(),
                    "timestamp": system.date.now()
                }}
            )
        except:
            pass  # Don't let monitoring errors break the main error handling'''
    
    return python_script
```

#### Transform Script Processing

Transform scripts require special handling due to their frequent execution and performance impact.

```python
# Transform script processor with optimization patterns
class TransformScriptProcessor:
    def __init__(self):
        self.performance_patterns = self._load_performance_patterns()
        self.validation_rules = self._load_transform_validation_rules()
    
    def generate_transform_script(self, transform_config: Dict[str, Any]) -> str:
        """Generate optimized transform script with proper escape handling"""
        
        transform_type = transform_config.get('transform_type', 'value_conversion')
        
        if transform_type == 'status_indicator':
            return self._generate_status_transform(transform_config)
        elif transform_type == 'unit_conversion':
            return self._generate_unit_conversion_transform(transform_config)
        elif transform_type == 'calculation':
            return self._generate_calculation_transform(transform_config)
        else:
            return self._generate_generic_transform(transform_config)
    
    def _generate_status_transform(self, config: Dict[str, Any]) -> str:
        """Generate status indicator transform script"""
        
        status_mappings = config.get('status_mappings', {
            0: {'text': 'Stopped', 'color': '#dc3545'},
            1: {'text': 'Running', 'color': '#28a745'},
            2: {'text': 'Fault', 'color': '#ffc107'}
        })
        
        # Create mapping code
        mapping_code = []
        for value, status in status_mappings.items():
            mapping_code.append(f'''        if value == {value}:
            return {{
                "text": "{status['text']}", 
                "color": "{status['color']}"
            }}''')
        
        mapping_code_str = '\n'.join(mapping_code)
        
        python_script = f'''def transform(value, quality, timestamp):
    """
    Transform numeric status to status object with text and color.
    
    Args:
        value: Numeric status value
        quality: Tag quality object  
        timestamp: Tag timestamp
        
    Returns:
        dict: Status object with text and color properties
    """
    try:
        # Check tag quality first
        if not quality.isGood():
            return {{
                "text": "COMM ERROR",
                "color": "#6c757d"
            }}
        
        # Convert to integer for status mapping
        status_value = int(float(value))
        
{mapping_code_str}
        
        # Default case for unknown status
        return {{
            "text": "UNKNOWN ({{0}})".format(status_value),
            "color": "#6c757d"
        }}
        
    except Exception as e:
        # Return error status
        return {{
            "text": "ERROR",
            "color": "#dc3545"
        }}'''
        
        return python_script
    
    def _generate_unit_conversion_transform(self, config: Dict[str, Any]) -> str:
        """Generate unit conversion transform script"""
        
        from_unit = config.get('from_unit', 'celsius')
        to_unit = config.get('to_unit', 'fahrenheit')
        precision = config.get('precision', 1)
        
        # Define conversion formulas
        conversion_formulas = {
            ('celsius', 'fahrenheit'): 'value * 9.0/5.0 + 32',
            ('fahrenheit', 'celsius'): '(value - 32) * 5.0/9.0',
            ('psi', 'bar'): 'value * 0.0689476',
            ('bar', 'psi'): 'value * 14.5038',
            ('gpm', 'lpm'): 'value * 3.78541',
            ('lpm', 'gpm'): 'value * 0.264172'
        }
        
        conversion_key = (from_unit.lower(), to_unit.lower())
        formula = conversion_formulas.get(conversion_key, 'value')  # Default: no conversion
        
        python_script = f'''def transform(value, quality, timestamp):
    """
    Convert {from_unit} to {to_unit} with {precision} decimal precision.
    
    Args:
        value: Input value in {from_unit}
        quality: Tag quality object
        timestamp: Tag timestamp
        
    Returns:
        float: Converted value in {to_unit}
    """
    try:
        # Check tag quality
        if not quality.isGood():
            return None
        
        # Perform conversion
        input_value = float(value)
        converted_value = {formula}
        
        # Apply precision rounding
        return round(converted_value, {precision})
        
    except (ValueError, TypeError):
        # Return None for invalid input
        return None
    except Exception as e:
        # Log error and return None
        import system.util
        logger = system.util.getLogger("UnitConversion")
        logger.error("Unit conversion error: {{}}".format(str(e)))
        return None'''
        
        return python_script
    
    def _generate_calculation_transform(self, config: Dict[str, Any]) -> str:
        """Generate calculation transform script"""
        
        calculation_type = config.get('calculation_type', 'formula')
        
        if calculation_type == 'formula':
            return self._generate_formula_transform(config)
        elif calculation_type == 'aggregate':
            return self._generate_aggregate_transform(config)
        else:
            return self._generate_custom_calculation_transform(config)
    
    def _generate_formula_transform(self, config: Dict[str, Any]) -> str:
        """Generate formula-based calculation transform"""
        
        formula = config.get('formula', 'value * 1.0')
        description = config.get('description', 'Custom calculation')
        variables = config.get('variables', {})
        
        # Build variable assignments
        var_assignments = []
        for var_name, var_config in variables.items():
            if var_config.get('type') == 'constant':
                var_assignments.append(f'        {var_name} = {var_config["value"]}')
            elif var_config.get('type') == 'tag_reference':
                var_assignments.append(f'        {var_name} = {var_config["tag_path"]}  # Additional tag binding required')
        
        var_code = '\n'.join(var_assignments) if var_assignments else '        # No additional variables defined'
        
        python_script = f'''def transform(value, quality, timestamp):
    """
    {description}
    
    Formula: {formula}
    
    Args:
        value: Primary input value
        quality: Tag quality object
        timestamp: Tag timestamp
        
    Returns:
        float: Calculated result
    """
    import math
    
    try:
        # Check tag quality
        if not quality.isGood():
            return None
        
        # Convert input to float
        input_value = float(value)
        
        # Define variables
{var_code}
        
        # Perform calculation
        result = {formula.replace('value', 'input_value')}
        
        # Validate result
        if math.isnan(result) or math.isinf(result):
            return None
        
        return result
        
    except (ValueError, TypeError, ZeroDivisionError) as e:
        # Return None for calculation errors
        return None
    except Exception as e:
        # Log unexpected errors
        import system.util
        logger = system.util.getLogger("CalculationTransform")
        logger.error("Calculation error: {{}}".format(str(e)))
        return None'''
        
        return python_script
```

### 2. Script Validation and Processing Pipeline

#### Escape Sequence Processor

```python
# processing/escape_processor.py
import re
import json
from typing import Dict, List, Any, Optional, Tuple

class ScriptEscapeProcessor:
    def __init__(self):
        self.escape_patterns = self._define_escape_patterns()
        self.validation_rules = self._load_validation_rules()
    
    def _define_escape_patterns(self) -> Dict[str, str]:
        """Define escape sequence patterns for JSON-embedded scripts"""
        return {
            # Standard JSON escape sequences
            '\\\\n': '\n',    # Newlines
            '\\\\t': '\t',    # Tabs
            '\\\\r': '\r',    # Carriage returns
            '\\\\"': '"',     # Double quotes
            "\\\\'": "'",     # Single quotes
            '\\\\\\\\': '\\', # Backslashes (must be last)
            
            # Python-specific sequences in JSON
            '\\\\\\n': '\\\n',  # Literal backslash-newline
            '\\\\\\t': '\\\t',  # Literal backslash-tab
        }
    
    def process_inline_script(self, script_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process inline script with proper escape handling and validation"""
        
        result = {
            'processed_script': '',
            'valid': True,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        try:
            # Step 1: Process escape sequences
            processed_script = self._process_escape_sequences(script_content)
            result['processed_script'] = processed_script
            result['metadata']['original_length'] = len(script_content)
            result['metadata']['processed_length'] = len(processed_script)
            
            # Step 2: Validate Python syntax
            syntax_result = self._validate_python_syntax(processed_script)
            if not syntax_result['valid']:
                result['valid'] = False
                result['errors'].extend(syntax_result['errors'])
                return result
            
            # Step 3: Context-specific validation
            context_result = self._validate_script_context(processed_script, context)
            result['errors'].extend(context_result['errors'])
            result['warnings'].extend(context_result['warnings'])
            
            if context_result['errors']:
                result['valid'] = False
            
            # Step 4: Performance analysis
            perf_analysis = self._analyze_performance_implications(processed_script, context)
            result['warnings'].extend(perf_analysis['warnings'])
            result['metadata']['performance_score'] = perf_analysis['score']
            
            # Step 5: Security analysis
            security_analysis = self._analyze_security_implications(processed_script, context)
            result['warnings'].extend(security_analysis['warnings'])
            result['errors'].extend(security_analysis['errors'])
            
            if security_analysis['errors']:
                result['valid'] = False
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'processing_error',
                'message': f'Failed to process inline script: {str(e)}',
                'line': 0
            })
        
        return result
    
    def _process_escape_sequences(self, script: str) -> str:
        """Process JSON escape sequences to get actual Python code"""
        
        processed = script
        
        # Process escape sequences in order (backslashes last)
        for escaped_seq, actual_seq in self.escape_patterns.items():
            processed = processed.replace(escaped_seq, actual_seq)
        
        return processed
    
    def _validate_python_syntax(self, script: str) -> Dict[str, Any]:
        """Validate Python syntax of processed script"""
        
        result = {'valid': True, 'errors': []}
        
        try:
            import ast
            # Attempt to parse the script
            tree = ast.parse(script)
            
            # Additional Jython-specific checks
            jython_result = self._validate_jython_compatibility(tree, script)
            result['errors'].extend(jython_result['errors'])
            
            if jython_result['errors']:
                result['valid'] = False
                
        except SyntaxError as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'syntax_error',
                'message': f'Python syntax error: {e.msg}',
                'line': e.lineno,
                'column': e.offset,
                'text': getattr(e, 'text', '').strip() if hasattr(e, 'text') else ''
            })
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'parse_error',
                'message': f'Failed to parse script: {str(e)}',
                'line': 0
            })
        
        return result
    
    def _validate_jython_compatibility(self, ast_tree, script: str) -> Dict[str, Any]:
        """Validate Jython 2.7 compatibility"""
        
        result = {'errors': []}
        
        # Check for Python 3 specific features
        python3_features = self._detect_python3_features(ast_tree, script)
        for feature in python3_features:
            result['errors'].append({
                'type': 'jython_incompatibility',
                'message': f'Python 3 feature not supported in Jython 2.7: {feature["feature"]}',
                'line': feature.get('line', 0),
                'suggestion': feature.get('suggestion', 'Use Python 2.7 compatible syntax')
            })
        
        return result
    
    def _detect_python3_features(self, ast_tree, script: str) -> List[Dict[str, Any]]:
        """Detect Python 3 features that aren't compatible with Jython 2.7"""
        
        features = []
        lines = script.split('\n')
        
        # Check for f-strings
        for i, line in enumerate(lines):
            if re.search(r'f["\']', line):
                features.append({
                    'feature': 'f-strings',
                    'line': i + 1,
                    'suggestion': 'Use .format() or % formatting instead'
                })
        
        # Check for async/await
        if 'async def' in script or 'await ' in script:
            features.append({
                'feature': 'async/await',
                'line': 0,
                'suggestion': 'Use traditional callback patterns'
            })
        
        # Check for type hints
        if re.search(r':\s*\w+\s*=', script) or re.search(r'->\s*\w+:', script):
            features.append({
                'feature': 'type hints',
                'line': 0,
                'suggestion': 'Remove type hints or use comments'
            })
        
        return features
    
    def _validate_script_context(self, script: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate script against its execution context"""
        
        result = {'errors': [], 'warnings': []}
        
        script_context = context.get('execution_context', 'gateway')
        component_type = context.get('component_type', 'unknown')
        
        # Validate function signature based on context
        if script_context == 'transform':
            if 'def transform(value, quality, timestamp):' not in script:
                result['errors'].append({
                    'type': 'missing_signature',
                    'message': 'Transform scripts must have signature: def transform(value, quality, timestamp):',
                    'line': 1
                })
        
        elif script_context == 'component_event':
            if 'def runAction(self, event):' not in script and component_type == 'button':
                result['errors'].append({
                    'type': 'missing_signature', 
                    'message': 'Button event scripts must have signature: def runAction(self, event):',
                    'line': 1
                })
        
        # Validate system function usage
        system_functions = re.findall(r'system\.(\w+)', script)
        for func_module in system_functions:
            if not self._is_module_available(func_module, script_context):
                result['warnings'].append({
                    'type': 'module_availability',
                    'message': f'Module system.{func_module} may not be available in {script_context} context',
                    'suggestion': f'Verify system.{func_module} is available in {script_context}'
                })
        
        return result
    
    def _analyze_performance_implications(self, script: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance implications of the script"""
        
        result = {'warnings': [], 'score': 100}
        
        script_context = context.get('execution_context', 'gateway')
        
        # Check for performance anti-patterns
        if script_context in ['transform', 'component_event']:
            
            # Database calls in UI context
            if 'system.db.' in script:
                result['warnings'].append({
                    'type': 'performance_warning',
                    'message': 'Database calls in UI scripts can cause responsiveness issues',
                    'suggestion': 'Consider moving database operations to gateway scripts'
                })
                result['score'] -= 30
            
            # Complex loops
            loop_count = script.count('for ') + script.count('while ')
            if loop_count > 2:
                result['warnings'].append({
                    'type': 'performance_warning',
                    'message': f'Script contains {loop_count} loops which may impact UI performance',
                    'suggestion': 'Consider optimizing or moving complex logic to gateway'
                })
                result['score'] -= loop_count * 10
            
            # Tag reads in transforms
            if script_context == 'transform' and 'system.tag.read' in script:
                result['warnings'].append({
                    'type': 'performance_warning',
                    'message': 'Tag reads in transform scripts should be avoided',
                    'suggestion': 'Use additional bindings instead of reading tags in transform'
                })
                result['score'] -= 40
        
        return result
    
    def _analyze_security_implications(self, script: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security implications of the script"""
        
        result = {'warnings': [], 'errors': []}
        
        # Check for potentially dangerous operations
        dangerous_patterns = [
            ('exec(', 'Dynamic code execution'),
            ('eval(', 'Dynamic expression evaluation'),
            ('__import__', 'Dynamic imports'),
            ('open(', 'File system access'),
            ('subprocess', 'System command execution')
        ]
        
        for pattern, description in dangerous_patterns:
            if pattern in script:
                result['warnings'].append({
                    'type': 'security_warning',
                    'message': f'Potentially dangerous operation detected: {description}',
                    'pattern': pattern,
                    'suggestion': 'Review security implications carefully'
                })
        
        # Check for hardcoded credentials
        credential_patterns = [
            r'password\s*=\s*["\'].+["\']',
            r'passwd\s*=\s*["\'].+["\']',
            r'secret\s*=\s*["\'].+["\']',
            r'token\s*=\s*["\'].+["\']'
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, script, re.IGNORECASE):
                result['errors'].append({
                    'type': 'security_error',
                    'message': 'Hardcoded credentials detected in script',
                    'suggestion': 'Use secure credential storage instead of hardcoding'
                })
        
        return result
    
    def format_script_for_json(self, script: str) -> str:
        """Format Python script for JSON embedding with proper escaping"""
        
        # Escape characters for JSON representation
        replacements = [
            ('\\', '\\\\'),    # Backslashes first
            ('"', '\\"'),      # Double quotes
            ('\n', '\\n'),     # Newlines
            ('\t', '\\t'),     # Tabs
            ('\r', '\\r'),     # Carriage returns
        ]
        
        formatted = script
        for actual, escaped in replacements:
            formatted = formatted.replace(actual, escaped)
        
        return formatted
```

### 3. Context-Aware Script Generation

#### Script Template Engine

```python
# templates/script_templates.py
from typing import Dict, List, Any, Optional
from jinja2 import Template, Environment, BaseLoader
import json

class ScriptTemplateEngine:
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self.templates = self._load_script_templates()
        
    def _load_script_templates(self) -> Dict[str, str]:
        """Load script templates for different contexts"""
        return {
            'button_action': '''def runAction(self, event):
    """
    {{ description }}
    
    Args:
        self: Component reference
        event: Action event object
    """
    import system.util
    import system.tag
    {% if requires_security %}import system.security{% endif %}
    
    logger = system.util.getLogger("{{ component_name }}")
    
    try:
        {% if requires_security %}
        # Security validation
        username = system.security.getUsername()
        user_roles = system.security.getUserRoles(username)
        required_roles = {{ required_roles }}
        
        if not any(role in user_roles for role in required_roles):
            logger.warning("User {} lacks required roles".format(username))
            system.gui.messageBox("Insufficient permissions", "Access Denied")
            return
        {% endif %}
        
        {% if confirmation_required %}
        # Confirmation dialog
        result = system.gui.confirm("{{ confirmation_message }}", "Confirm Action")
        if not result:
            logger.info("User cancelled action")
            return
        {% endif %}
        
        # Execute action
        {% for action in actions %}
        {{ action.code }}
        {% endfor %}
        
        logger.info("Action completed successfully")
        
    except Exception as e:
        logger.error("Action error: {}".format(str(e)))
        system.gui.messageBox("An error occurred", "Error")''',
            
            'transform_script': '''def transform(value, quality, timestamp):
    """
    {{ description }}
    
    Args:
        value: {{ value_description }}
        quality: Tag quality object
        timestamp: Tag timestamp
        
    Returns:
        {{ return_description }}
    """
    try:
        # Quality check
        if not quality.isGood():
            {% if quality_fallback %}
            return {{ quality_fallback }}
            {% else %}
            return None
            {% endif %}
        
        # Value processing
        {% if input_validation %}
        # Input validation
        {% for validation in input_validations %}
        {{ validation.code }}
        {% endfor %}
        {% endif %}
        
        # Main transformation logic
        {{ transformation_code }}
        
        return result
        
    except Exception as e:
        {% if error_logging %}
        import system.util
        logger = system.util.getLogger("Transform")
        logger.error("Transform error: {}".format(str(e)))
        {% endif %}
        return {{ error_fallback }}''',
            
            'timer_script': '''# Timer script - {{ schedule_description }}
import system.util
import system.tag
{% if database_operations %}import system.db{% endif %}

logger = system.util.getLogger("{{ script_name }}")

try:
    {% if data_collection %}
    # Data collection
    {% for collection in data_collections %}
    {{ collection.code }}
    {% endfor %}
    {% endif %}
    
    {% if calculations %}
    # Calculations
    {% for calc in calculations %}
    {{ calc.code }}
    {% endfor %}
    {% endif %}
    
    {% if database_operations %}
    # Database operations
    {% for db_op in database_operations %}
    {{ db_op.code }}
    {% endfor %}
    {% endif %}
    
    logger.debug("Timer script completed successfully")
    
except Exception as e:
    logger.error("Timer script error: {}".format(str(e)))
    {% if error_notifications %}
    # Send error notification
    {% for notification in error_notifications %}
    {{ notification.code }}
    {% endfor %}
    {% endif %}'''
        }
    
    def generate_script(self, template_name: str, context: Dict[str, Any]) -> str:
        """Generate script from template with given context"""
        
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = Template(self.templates[template_name])
        generated_script = template.render(**context)
        
        return generated_script
    
    def generate_button_action(self, config: Dict[str, Any]) -> str:
        """Generate button action script with proper context"""
        
        context = {
            'description': config.get('description', 'Button action handler'),
            'component_name': config.get('component_name', 'ButtonAction'),
            'requires_security': config.get('requires_security', True),
            'required_roles': config.get('required_roles', ['Operators']),
            'confirmation_required': config.get('confirmation_required', False),
            'confirmation_message': config.get('confirmation_message', 'Execute this action?'),
            'actions': self._generate_action_code(config.get('actions', []))
        }
        
        return self.generate_script('button_action', context)
    
    def _generate_action_code(self, actions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate code for individual actions"""
        
        action_codes = []
        
        for action in actions:
            action_type = action.get('type', 'tag_write')
            
            if action_type == 'tag_write':
                code = f'''# Write to tag
        tag_path = "{action.get('tag_path', '[default]Unknown')}"
        tag_value = {action.get('tag_value', 'True')}
        success = system.tag.writeBlocking([tag_path], [tag_value])
        if not success:
            raise Exception("Failed to write tag: {{}}".format(tag_path))'''
            
            elif action_type == 'navigate':
                code = f'''# Navigate to view
        view_path = "{action.get('view_path', '/main/overview')}"
        params = {action.get('view_params', '{}')}
        system.perspective.navigate(view=view_path, params=params)'''
            
            elif action_type == 'popup':
                code = f'''# Open popup
        popup_id = "{action.get('popup_id', 'actionPopup')}"
        view_path = "{action.get('popup_view', '/popups/confirmation')}"
        params = {action.get('popup_params', '{}')}
        system.perspective.openPopup(id=popup_id, view=view_path, params=params)'''
            
            elif action_type == 'custom':
                code = action.get('code', '# Custom action code here')
            
            else:
                code = f'# Unknown action type: {action_type}'
            
            action_codes.append({'code': code})
        
        return action_codes
```

This comprehensive inline script processing system ensures that AI-generated scripts are properly escaped, validated, and optimized for their specific execution contexts within Ignition, while maintaining production-grade error handling and security compliance.