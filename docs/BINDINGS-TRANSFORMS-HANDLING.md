# Bindings and Transform Handling Specifications

## Overview

This document provides comprehensive specifications for handling Ignition bindings and script transforms, with particular focus on proper processing of inline Jython scripts, escape character handling, resource.json structure, and transform script validation. These specifications ensure AI-generated bindings and transforms are syntactically correct and production-ready.

## 🎯 Binding Processing Objectives

### Primary Goals
- **Accurate String Handling**: Proper escape sequence processing for inline scripts
- **Resource Structure Compliance**: Correct resource.json format adherence
- **Transform Script Validation**: Comprehensive validation of transform script logic
- **Binding Type Optimization**: Intelligent selection of optimal binding types
- **Performance Awareness**: Detection and prevention of performance anti-patterns

### Critical Requirements
- **Escape Character Preservation**: Maintain \\n, \\t, \\r, \\", \\\\ correctly in JSON
- **Script Syntax Validation**: Ensure embedded Jython compiles correctly
- **Binding Context Awareness**: Validate bindings work in their specific contexts
- **Resource.json Compliance**: Follow Ignition's exact resource file format

## 🔗 Binding Types and Handling

### 1. Tag Bindings

#### Standard Tag Binding Structure

```json
{
  "binding": {
    "type": "tag",
    "config": {
      "path": "[default]Equipment/Tank01/Level",
      "polling": "subscribe",
      "deadband": 0.1,
      "indirect": false
    }
  }
}
```

#### Indirect Tag Binding with Path Construction

```json
{
  "binding": {
    "type": "tag",
    "config": {
      "indirect": true,
      "path": "{root.custom.basePath}/Status",
      "polling": "subscribe"
    }
  }
}
```

#### Validation Rules for Tag Bindings

```python
# validation/binding_validator.py
import re
from typing import Dict, List, Any, Optional

class TagBindingValidator:
    def __init__(self):
        self.tag_path_pattern = re.compile(r'^\[[\w\-]+\][\w\-\/\.]+$')
        self.indirect_pattern = re.compile(r'\{[\w\.]+\}')
        
    def validate_tag_binding(self, binding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tag binding configuration"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'optimizations': []
        }
        
        config = binding.get('config', {})
        path = config.get('path', '')
        
        # Validate path format
        if config.get('indirect', False):
            # Indirect binding - check for parameter references
            if not self.indirect_pattern.search(path):
                result['errors'].append({
                    'message': 'Indirect binding path must contain parameter references like {root.custom.property}',
                    'path': 'config.path',
                    'current_value': path
                })
                result['valid'] = False
        else:
            # Direct binding - validate tag path format
            if not self.tag_path_pattern.match(path):
                result['errors'].append({
                    'message': 'Invalid tag path format. Expected: [provider]folder/tagname',
                    'path': 'config.path',
                    'current_value': path,
                    'example': '[default]Equipment/Tank01/Level'
                })
                result['valid'] = False
        
        # Validate polling mode
        polling = config.get('polling', 'subscribe')
        valid_polling = ['subscribe', 'direct', 'driven']
        if polling not in valid_polling:
            result['errors'].append({
                'message': f'Invalid polling mode. Must be one of: {", ".join(valid_polling)}',
                'path': 'config.polling',
                'current_value': polling
            })
            result['valid'] = False
        
        # Performance warnings
        if polling != 'subscribe':
            result['warnings'].append({
                'message': 'Non-subscribe polling may impact performance',
                'path': 'config.polling',
                'suggestion': 'Use "subscribe" for optimal performance unless specific polling is required'
            })
        
        # Deadband validation for numeric tags
        deadband = config.get('deadband')
        if deadband is not None:
            if not isinstance(deadband, (int, float)) or deadband < 0:
                result['errors'].append({
                    'message': 'Deadband must be a non-negative number',
                    'path': 'config.deadband',
                    'current_value': deadband
                })
                result['valid'] = False
        
        return result
```

### 2. Expression Bindings

#### Simple Expression Binding

```json
{
  "binding": {
    "type": "expression",
    "config": {
      "expression": "{[default]Equipment/Tank01/Level} > {view.params.highAlarm}",
      "runScript": "gateway"
    }
  }
}
```

#### Complex Expression with String Manipulation

```json
{
  "binding": {
    "type": "expression",
    "config": {
      "expression": "format('Tank Level: %.1f%% (%s)', {[default]Equipment/Tank01/Level}, if({[default]Equipment/Tank01/Alarm}, 'ALARM', 'OK'))",
      "runScript": "gateway"
    }
  }
}
```

#### Expression Binding Validator

```python
class ExpressionBindingValidator:
    def __init__(self):
        self.tag_reference_pattern = re.compile(r'\{(\[[\w\-]+\][\w\-\/\.]+)\}')
        self.param_reference_pattern = re.compile(r'\{(view\.params\.[\w]+|session\.[\w\.]+|page\.[\w\.]+)\}')
        self.function_pattern = re.compile(r'(\w+)\s*\(')
        
    def validate_expression_binding(self, binding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate expression binding syntax and references"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'analysis': {}
        }
        
        config = binding.get('config', {})
        expression = config.get('expression', '')
        
        if not expression:
            result['errors'].append({
                'message': 'Expression cannot be empty',
                'path': 'config.expression'
            })
            result['valid'] = False
            return result
        
        # Analyze expression complexity
        result['analysis'] = self._analyze_expression_complexity(expression)
        
        # Validate tag references
        tag_refs = self.tag_reference_pattern.findall(expression)
        for tag_path in tag_refs:
            if not self._is_valid_tag_path(tag_path):
                result['errors'].append({
                    'message': f'Invalid tag path in expression: {tag_path}',
                    'path': 'config.expression',
                    'suggestion': 'Use format [provider]folder/tagname'
                })
                result['valid'] = False
        
        # Validate parameter references
        param_refs = self.param_reference_pattern.findall(expression)
        result['analysis']['parameter_references'] = param_refs
        
        # Check for performance issues
        if len(tag_refs) > 10:
            result['warnings'].append({
                'message': 'Expression references many tags, consider using transform script',
                'path': 'config.expression',
                'tag_count': len(tag_refs)
            })
        
        # Validate function usage
        functions = self.function_pattern.findall(expression)
        for func in functions:
            if not self._is_valid_expression_function(func):
                result['warnings'].append({
                    'message': f'Unknown or deprecated function: {func}',
                    'path': 'config.expression'
                })
        
        # Check expression balance (parentheses, braces)
        if not self._check_expression_balance(expression):
            result['errors'].append({
                'message': 'Unbalanced parentheses or braces in expression',
                'path': 'config.expression'
            })
            result['valid'] = False
        
        return result
    
    def _analyze_expression_complexity(self, expression: str) -> Dict[str, Any]:
        """Analyze expression complexity metrics"""
        return {
            'length': len(expression),
            'tag_count': len(self.tag_reference_pattern.findall(expression)),
            'function_count': len(self.function_pattern.findall(expression)),
            'nesting_depth': self._calculate_nesting_depth(expression),
            'complexity_score': self._calculate_complexity_score(expression)
        }
    
    def _calculate_complexity_score(self, expression: str) -> int:
        """Calculate complexity score for expression"""
        score = 0
        score += len(expression) // 10  # Length factor
        score += len(self.tag_reference_pattern.findall(expression)) * 2  # Tag references
        score += len(self.function_pattern.findall(expression)) * 3  # Function calls
        score += self._calculate_nesting_depth(expression) * 5  # Nesting penalty
        return score
```

### 3. Transform Script Bindings

#### Transform Script Structure and Escape Handling

```json
{
  "binding": {
    "type": "transform",
    "config": {
      "script": "# Tank status transform\\ndef transform(value, quality, timestamp):\\n\\t\"\"\"\\n\\tTransform tank level to status message.\\n\\t\\n\\tArgs:\\n\\t\\tvalue: Tank level percentage (0-100)\\n\\t\\tquality: Tag quality\\n\\t\\ttimestamp: Tag timestamp\\n\\t\\n\\tReturns:\\n\\t\\tstr: Status message\\n\\t\"\"\"\\n\\ttry:\\n\\t\\tif quality.isGood():\\n\\t\\t\\tlevel = float(value)\\n\\t\\t\\t\\n\\t\\t\\tif level >= 90:\\n\\t\\t\\t\\treturn \\\"CRITICAL: Tank almost full ({:.1f}%)\\\".format(level)\\n\\t\\t\\telif level >= 75:\\n\\t\\t\\t\\treturn \\\"WARNING: Tank filling ({:.1f}%)\\\".format(level)\\n\\t\\t\\telif level >= 25:\\n\\t\\t\\t\\treturn \\\"NORMAL: Tank level {:.1f}%\\\".format(level)\\n\\t\\t\\telse:\\n\\t\\t\\t\\treturn \\\"LOW: Tank needs refilling ({:.1f}%)\\\".format(level)\\n\\t\\telse:\\n\\t\\t\\treturn \\\"ERROR: Invalid reading\\\"\\n\\texcept Exception as e:\\n\\t\\treturn \\\"ERROR: {}\\\".format(str(e))",
      "runScript": "gateway"
    }
  }
}
```

#### Transform Script Validator with Escape Processing

```python
import ast
import json
from typing import Dict, List, Any, Optional

class TransformScriptValidator:
    def __init__(self):
        self.required_signature = 'def transform(value, quality, timestamp):'
        
    def validate_transform_binding(self, binding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transform script binding with proper escape handling"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'script_analysis': {}
        }
        
        config = binding.get('config', {})
        escaped_script = config.get('script', '')
        
        if not escaped_script:
            result['errors'].append({
                'message': 'Transform script cannot be empty',
                'path': 'config.script'
            })
            result['valid'] = False
            return result
        
        # Process escape sequences to get actual Python code
        try:
            # Handle JSON escape sequences
            actual_script = self._process_escape_sequences(escaped_script)
            result['script_analysis']['processed_script'] = actual_script
        except Exception as e:
            result['errors'].append({
                'message': f'Failed to process escape sequences: {str(e)}',
                'path': 'config.script'
            })
            result['valid'] = False
            return result
        
        # Validate Python syntax
        syntax_result = self._validate_python_syntax(actual_script)
        if not syntax_result['valid']:
            result['errors'].extend(syntax_result['errors'])
            result['valid'] = False
        
        # Validate transform function signature
        signature_result = self._validate_transform_signature(actual_script)
        if not signature_result['valid']:
            result['errors'].extend(signature_result['errors'])
            result['valid'] = False
        
        # Analyze script quality
        quality_analysis = self._analyze_script_quality(actual_script)
        result['script_analysis'].update(quality_analysis)
        result['warnings'].extend(quality_analysis.get('warnings', []))
        
        # Check for performance issues
        performance_issues = self._check_performance_patterns(actual_script)
        result['warnings'].extend(performance_issues)
        
        return result
    
    def _process_escape_sequences(self, escaped_script: str) -> str:
        """Process JSON escape sequences to get actual Python code"""
        # Handle common JSON escape sequences
        replacements = {
            '\\n': '\n',     # Newlines
            '\\t': '\t',     # Tabs  
            '\\r': '\r',     # Carriage returns
            '\\"': '"',      # Quotes
            '\\\\': '\\',    # Backslashes
        }
        
        processed = escaped_script
        for escaped, actual in replacements.items():
            processed = processed.replace(escaped, actual)
        
        return processed
    
    def _validate_python_syntax(self, script: str) -> Dict[str, Any]:
        """Validate Python syntax of transform script"""
        result = {'valid': True, 'errors': []}
        
        try:
            # Parse the script to check syntax
            ast.parse(script)
        except SyntaxError as e:
            result['valid'] = False
            result['errors'].append({
                'message': f'Python syntax error: {e.msg}',
                'line': e.lineno,
                'column': e.offset,
                'path': 'config.script'
            })
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'message': f'Script parsing error: {str(e)}',
                'path': 'config.script'
            })
        
        return result
    
    def _validate_transform_signature(self, script: str) -> Dict[str, Any]:
        """Validate transform function has correct signature"""
        result = {'valid': True, 'errors': []}
        
        try:
            tree = ast.parse(script)
            
            # Look for transform function
            transform_func = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'transform':
                    transform_func = node
                    break
            
            if not transform_func:
                result['valid'] = False
                result['errors'].append({
                    'message': 'Transform script must contain a function named "transform"',
                    'path': 'config.script',
                    'required_signature': self.required_signature
                })
                return result
            
            # Check function arguments
            args = transform_func.args.args
            expected_args = ['value', 'quality', 'timestamp']
            
            if len(args) != 3:
                result['valid'] = False
                result['errors'].append({
                    'message': f'Transform function must have exactly 3 arguments: {", ".join(expected_args)}',
                    'path': 'config.script',
                    'current_args': [arg.arg for arg in args] if args else []
                })
            else:
                actual_args = [arg.arg for arg in args]
                if actual_args != expected_args:
                    result['errors'].append({
                        'message': f'Transform function arguments should be: {", ".join(expected_args)}',
                        'path': 'config.script',
                        'current_args': actual_args,
                        'severity': 'warning'
                    })
        
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'message': f'Error validating function signature: {str(e)}',
                'path': 'config.script'
            })
        
        return result
    
    def _analyze_script_quality(self, script: str) -> Dict[str, Any]:
        """Analyze transform script quality and best practices"""
        analysis = {
            'warnings': [],
            'lines_of_code': len([line for line in script.split('\n') if line.strip()]),
            'has_error_handling': 'try:' in script and 'except' in script,
            'has_quality_check': 'quality.isGood()' in script or 'quality.isBad()' in script,
            'has_return_statement': 'return' in script,
            'uses_logging': 'logger' in script or 'system.util.getLogger' in script
        }
        
        # Check for quality handling
        if not analysis['has_quality_check']:
            analysis['warnings'].append({
                'message': 'Transform should check tag quality before processing',
                'suggestion': 'Add quality.isGood() check before processing value',
                'path': 'config.script'
            })
        
        # Check for error handling
        if not analysis['has_error_handling']:
            analysis['warnings'].append({
                'message': 'Transform should include error handling',
                'suggestion': 'Wrap transform logic in try-except block',
                'path': 'config.script'
            })
        
        # Check script length
        if analysis['lines_of_code'] > 50:
            analysis['warnings'].append({
                'message': 'Transform script is quite long, consider simplifying',
                'suggestion': 'Break complex logic into smaller functions',
                'path': 'config.script'
            })
        
        return analysis
    
    def _check_performance_patterns(self, script: str) -> List[Dict[str, Any]]:
        """Check for performance anti-patterns in transform script"""
        warnings = []
        
        # Check for database calls
        if 'system.db.' in script:
            warnings.append({
                'message': 'Database calls in transform scripts can impact performance',
                'suggestion': 'Consider using cached data or move logic to gateway script',
                'path': 'config.script',
                'severity': 'warning'
            })
        
        # Check for tag reads
        if 'system.tag.read' in script:
            warnings.append({
                'message': 'Tag reads in transform scripts should be avoided',
                'suggestion': 'Use additional bindings instead of reading tags in transform',
                'path': 'config.script',
                'severity': 'warning'
            })
        
        # Check for complex calculations
        if script.count('for ') > 2 or script.count('while ') > 1:
            warnings.append({
                'message': 'Complex loops in transform scripts may impact UI performance',
                'suggestion': 'Consider pre-calculating values or using gateway scripts',
                'path': 'config.script',
                'severity': 'warning'
            })
        
        return warnings
```

### 4. Property Bindings

#### Property Binding Structure

```json
{
  "binding": {
    "type": "property",
    "config": {
      "property": "view.params.selectedTank",
      "fallback": "Tank01"
    }
  }
}
```

#### Property Binding Validator

```python
class PropertyBindingValidator:
    def __init__(self):
        self.valid_property_roots = [
            'view.params',
            'view.custom', 
            'session.props',
            'page.props',
            'this.props',
            'parent.props'
        ]
    
    def validate_property_binding(self, binding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate property binding configuration"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        config = binding.get('config', {})
        property_path = config.get('property', '')
        
        if not property_path:
            result['errors'].append({
                'message': 'Property path cannot be empty',
                'path': 'config.property'
            })
            result['valid'] = False
            return result
        
        # Validate property path format
        valid_root = False
        for root in self.valid_property_roots:
            if property_path.startswith(root):
                valid_root = True
                break
        
        if not valid_root:
            result['errors'].append({
                'message': f'Invalid property root. Must start with one of: {", ".join(self.valid_property_roots)}',
                'path': 'config.property',
                'current_value': property_path
            })
            result['valid'] = False
        
        # Check for fallback value
        if 'fallback' not in config:
            result['warnings'].append({
                'message': 'Consider providing a fallback value for property binding',
                'path': 'config.fallback',
                'suggestion': 'Add fallback value to handle cases where property is undefined'
            })
        
        return result
```

## 📄 Resource.json Handling

### Resource.json Structure Specification

```python
# processing/resource_handler.py
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

class ResourceJsonHandler:
    """Handler for Ignition resource.json files with proper structure validation"""
    
    def __init__(self):
        self.resource_schema = self._get_resource_schema()
    
    def _get_resource_schema(self) -> Dict[str, Any]:
        """Define the expected resource.json schema"""
        return {
            "type": "object",
            "required": ["resource"],
            "properties": {
                "resource": {
                    "type": "object",
                    "required": ["type", "version", "data"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "com.inductiveautomation.perspective.common.resource.View",
                                "com.inductiveautomation.perspective.common.resource.Session",
                                "com.inductiveautomation.ignition.common.tags.model.TagProvider"
                            ]
                        },
                        "version": {
                            "type": "integer",
                            "minimum": 1
                        },
                        "data": {
                            "type": "object"
                        }
                    }
                }
            }
        }
    
    def create_perspective_view_resource(self, view_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create properly structured resource.json for Perspective view"""
        
        # Ensure view data has required structure
        if 'root' not in view_data:
            raise ValueError("View data must contain 'root' component")
        
        resource = {
            "resource": {
                "type": "com.inductiveautomation.perspective.common.resource.View",
                "version": 1,
                "data": {
                    "view": {
                        "params": view_data.get('params', {}),
                        "props": view_data.get('props', {}),
                        "root": view_data['root'],
                        "custom": view_data.get('custom', {})
                    }
                }
            }
        }
        
        # Add metadata if provided
        if metadata:
            resource['resource']['data']['view'].update(metadata)
        
        return resource
    
    def validate_resource_structure(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resource.json structure"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check top-level structure
            if 'resource' not in resource_data:
                result['errors'].append({
                    'message': 'Resource file must contain "resource" key at root level',
                    'path': 'resource'
                })
                result['valid'] = False
                return result
            
            resource = resource_data['resource']
            
            # Validate required fields
            required_fields = ['type', 'version', 'data']
            for field in required_fields:
                if field not in resource:
                    result['errors'].append({
                        'message': f'Resource must contain "{field}" field',
                        'path': f'resource.{field}'
                    })
                    result['valid'] = False
            
            # Validate resource type
            if 'type' in resource:
                valid_types = [
                    'com.inductiveautomation.perspective.common.resource.View',
                    'com.inductiveautomation.perspective.common.resource.Session',
                    'com.inductiveautomation.ignition.common.tags.model.TagProvider'
                ]
                
                if resource['type'] not in valid_types:
                    result['warnings'].append({
                        'message': f'Unknown resource type: {resource["type"]}',
                        'path': 'resource.type',
                        'valid_types': valid_types
                    })
            
            # Validate version
            if 'version' in resource:
                if not isinstance(resource['version'], int) or resource['version'] < 1:
                    result['errors'].append({
                        'message': 'Resource version must be a positive integer',
                        'path': 'resource.version',
                        'current_value': resource['version']
                    })
                    result['valid'] = False
            
            # Type-specific validation
            if resource.get('type') == 'com.inductiveautomation.perspective.common.resource.View':
                view_result = self._validate_view_resource(resource.get('data', {}))
                result['errors'].extend(view_result['errors'])
                result['warnings'].extend(view_result['warnings'])
                if not view_result['valid']:
                    result['valid'] = False
        
        except Exception as e:
            result['errors'].append({
                'message': f'Error validating resource structure: {str(e)}',
                'path': 'resource'
            })
            result['valid'] = False
        
        return result
    
    def _validate_view_resource(self, view_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Perspective view resource data"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if 'view' not in view_data:
            result['errors'].append({
                'message': 'View resource data must contain "view" object',
                'path': 'resource.data.view'
            })
            result['valid'] = False
            return result
        
        view = view_data['view']
        
        # Check for root component
        if 'root' not in view:
            result['errors'].append({
                'message': 'View must contain root component',
                'path': 'resource.data.view.root'
            })
            result['valid'] = False
        
        # Validate root component structure
        if 'root' in view:
            root_validation = self._validate_component_structure(view['root'], 'resource.data.view.root')
            result['errors'].extend(root_validation['errors'])
            result['warnings'].extend(root_validation['warnings'])
            if not root_validation['valid']:
                result['valid'] = False
        
        # Validate view parameters
        if 'params' in view:
            params_validation = self._validate_view_parameters(view['params'])
            result['warnings'].extend(params_validation.get('warnings', []))
        
        return result
    
    def _validate_component_structure(self, component: Dict[str, Any], path: str) -> Dict[str, Any]:
        """Validate component structure within resource"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Component must have type and props
        required_fields = ['type', 'props']
        for field in required_fields:
            if field not in component:
                result['errors'].append({
                    'message': f'Component must contain "{field}" field',
                    'path': f'{path}.{field}'
                })
                result['valid'] = False
        
        # Validate component type format
        if 'type' in component:
            component_type = component['type']
            if not isinstance(component_type, str) or not component_type.startswith('ia.'):
                result['errors'].append({
                    'message': 'Component type must be a string starting with "ia."',
                    'path': f'{path}.type',
                    'current_value': component_type
                })
                result['valid'] = False
        
        # Recursively validate child components
        if 'props' in component and isinstance(component['props'], dict):
            for prop_name, prop_value in component['props'].items():
                if isinstance(prop_value, dict) and 'type' in prop_value:
                    # This is a child component
                    child_validation = self._validate_component_structure(
                        prop_value, 
                        f'{path}.props.{prop_name}'
                    )
                    result['errors'].extend(child_validation['errors'])
                    result['warnings'].extend(child_validation['warnings'])
                    if not child_validation['valid']:
                        result['valid'] = False
        
        return result
    
    def process_binding_escapes(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Process escape sequences in component bindings and scripts"""
        processed_component = json.loads(json.dumps(component))  # Deep copy
        
        def process_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if key == 'script' and isinstance(value, str):
                        # Process script escape sequences
                        obj[key] = self._process_script_escapes(value)
                    elif key == 'expression' and isinstance(value, str):
                        # Process expression escape sequences (minimal)
                        obj[key] = self._process_expression_escapes(value)
                    elif isinstance(value, (dict, list)):
                        process_recursive(value, current_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        process_recursive(item, f"{path}[{i}]")
        
        process_recursive(processed_component)
        return processed_component
    
    def _process_script_escapes(self, script: str) -> str:
        """Process escape sequences in script strings"""
        # Handle JSON escape sequences for Python code
        replacements = [
            ('\\n', '\n'),    # Newlines
            ('\\t', '\t'),    # Tabs
            ('\\r', '\r'),    # Carriage returns
            ('\\"', '"'),     # Double quotes
            ("\\'", "'"),     # Single quotes  
            ('\\\\', '\\'),   # Backslashes (must be last)
        ]
        
        processed = script
        for escaped, actual in replacements:
            processed = processed.replace(escaped, actual)
        
        return processed
    
    def _process_expression_escapes(self, expression: str) -> str:
        """Process escape sequences in expression strings"""
        # Minimal processing for expressions - mainly quotes
        replacements = [
            ('\\"', '"'),
            ("\\'", "'")
        ]
        
        processed = expression
        for escaped, actual in replacements:
            processed = processed.replace(escaped, actual)
        
        return processed
    
    def format_for_json_output(self, script: str) -> str:
        """Format Python script for JSON output with proper escaping"""
        # Escape characters for JSON representation
        replacements = [
            ('\\', '\\\\'),   # Backslashes first
            ('"', '\\"'),     # Double quotes
            ('\n', '\\n'),    # Newlines
            ('\t', '\\t'),    # Tabs
            ('\r', '\\r'),    # Carriage returns
        ]
        
        formatted = script
        for actual, escaped in replacements:
            formatted = formatted.replace(actual, escaped)
        
        return formatted
```

### Example: Complete Transform Script Binding

```python
def create_tank_status_transform() -> Dict[str, Any]:
    """Create a complete tank status transform binding with proper escaping"""
    
    # Original Python script (readable format)
    python_script = '''def transform(value, quality, timestamp):
    """
    Transform tank level to status message with color coding.
    
    Args:
        value: Tank level percentage (0-100)
        quality: Tag quality object
        timestamp: Tag timestamp
    
    Returns:
        dict: Status object with message and color
    """
    import system.util
    
    logger = system.util.getLogger("TankTransform")
    
    try:
        if not quality.isGood():
            logger.warning("Poor quality reading for tank level")
            return {
                "message": "ERROR: Invalid reading",
                "color": "#ff0000",
                "level": 0
            }
        
        level = float(value)
        
        if level >= 90:
            return {
                "message": "CRITICAL: Tank almost full ({:.1f}%)".format(level),
                "color": "#ff4444",
                "level": level
            }
        elif level >= 75:
            return {
                "message": "WARNING: Tank filling ({:.1f}%)".format(level),
                "color": "#ffaa00", 
                "level": level
            }
        elif level >= 25:
            return {
                "message": "NORMAL: Tank level {:.1f}%".format(level),
                "color": "#00aa00",
                "level": level
            }
        else:
            return {
                "message": "LOW: Tank needs refilling ({:.1f}%)".format(level),
                "color": "#ff8800",
                "level": level
            }
            
    except Exception as e:
        logger.error("Tank transform error: {}".format(str(e)))
        return {
            "message": "ERROR: {}".format(str(e)),
            "color": "#ff0000",
            "level": 0
        }'''
    
    # Process for JSON inclusion
    handler = ResourceJsonHandler()
    escaped_script = handler.format_for_json_output(python_script)
    
    # Create the binding
    transform_binding = {
        "binding": {
            "type": "transform",
            "config": {
                "script": escaped_script,
                "runScript": "gateway"
            }
        }
    }
    
    return transform_binding

# Usage example:
tank_transform = create_tank_status_transform()
print(json.dumps(tank_transform, indent=2))
```

This comprehensive binding and transform handling specification ensures that AI-generated bindings are properly formatted, escaped, and validated for production use in Ignition systems.