# Resource.json Handling Patterns for Ignition AI Development

## Overview

This document provides comprehensive patterns and best practices for handling Ignition's resource.json files in AI-powered development workflows. It covers the structure, validation, generation, and optimization of resource files that define Perspective views, sessions, and other Ignition artifacts, ensuring AI-generated content integrates seamlessly with Ignition's project structure.

## 🎯 Resource.json Objectives

### Primary Goals
- **Accurate Structure Generation**: Ensure AI creates valid resource.json files that Ignition can import
- **Version Compatibility**: Maintain compatibility across different Ignition versions
- **Optimization Patterns**: Generate efficient resource structures for better performance
- **Validation Integration**: Comprehensive validation before deployment
- **Git Workflow Support**: Proper handling in version control and CI/CD pipelines

### Integration Benefits
- **Seamless Project Import**: Resources load correctly in Ignition Designer
- **Performance Optimization**: Optimized resource structures for faster loading
- **Development Efficiency**: Automated generation reduces manual resource creation
- **Quality Assurance**: Validation prevents deployment of malformed resources

## 📋 Resource.json Structure Patterns

### 1. Perspective View Resource Pattern

#### Complete View Resource Structure

```json
{
  "resource": {
    "type": "com.inductiveautomation.perspective.common.resource.View",
    "version": 1,
    "data": {
      "view": {
        "params": {
          "tankId": {
            "paramType": "string",
            "value": "TANK-001"
          },
          "displayMode": {
            "paramType": "string", 
            "value": "operations"
          },
          "refreshInterval": {
            "paramType": "int",
            "value": 5000
          }
        },
        "props": {
          "defaultSize": {
            "height": 800,
            "width": 1200
          }
        },
        "root": {
          "type": "ia.container.coord",
          "meta": {
            "name": "root"
          },
          "props": {
            "style": {
              "backgroundColor": "var(--neutral-20)"
            }
          },
          "position": {
            "basis": "100px"
          },
          "children": [
            {
              "type": "ia.display.label",
              "meta": {
                "name": "TitleLabel"
              },
              "props": {
                "text": {
                  "binding": {
                    "type": "expression",
                    "config": {
                      "expression": "format('Tank Status - %s', {view.params.tankId})"
                    }
                  }
                },
                "style": {
                  "fontSize": "24px",
                  "fontWeight": "bold",
                  "color": "var(--neutral-90)"
                }
              },
              "position": {
                "x": 20,
                "y": 20,
                "width": 400,
                "height": 40
              }
            }
          ]
        },
        "custom": {
          "applicationSettings": {
            "autoRefresh": true,
            "theme": "light",
            "permissions": {
              "read": ["Operators", "Engineers"],
              "write": ["Engineers"]
            }
          }
        }
      }
    }
  }
}
```

#### View Resource Validation Pattern

```python
# validation/resource_validator.py
import json
import jsonschema
from typing import Dict, List, Any, Optional
from pathlib import Path

class ResourceValidator:
    def __init__(self):
        self.view_schema = self._create_view_schema()
        self.session_schema = self._create_session_schema()
        
    def _create_view_schema(self) -> Dict[str, Any]:
        """Create JSON schema for Perspective view resources"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["resource"],
            "properties": {
                "resource": {
                    "type": "object",
                    "required": ["type", "version", "data"],
                    "properties": {
                        "type": {
                            "const": "com.inductiveautomation.perspective.common.resource.View"
                        },
                        "version": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "data": {
                            "type": "object",
                            "required": ["view"],
                            "properties": {
                                "view": {
                                    "type": "object",
                                    "required": ["root"],
                                    "properties": {
                                        "params": {
                                            "$ref": "#/definitions/viewParams"
                                        },
                                        "props": {
                                            "$ref": "#/definitions/viewProps"
                                        },
                                        "root": {
                                            "$ref": "#/definitions/component"
                                        },
                                        "custom": {
                                            "type": "object"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "definitions": {
                "viewParams": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z][a-zA-Z0-9]*$": {
                            "$ref": "#/definitions/parameter"
                        }
                    },
                    "additionalProperties": False
                },
                "parameter": {
                    "type": "object",
                    "required": ["paramType"],
                    "properties": {
                        "paramType": {
                            "enum": ["string", "int", "float", "boolean", "datetime", "dataset"]
                        },
                        "value": {
                            "description": "Default parameter value"
                        }
                    }
                },
                "viewProps": {
                    "type": "object",
                    "properties": {
                        "defaultSize": {
                            "type": "object",
                            "properties": {
                                "height": {"type": "number", "minimum": 100},
                                "width": {"type": "number", "minimum": 100}
                            }
                        },
                        "breakpoints": {
                            "type": "object"
                        }
                    }
                },
                "component": {
                    "type": "object",
                    "required": ["type"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "pattern": "^ia\\."
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$"
                                }
                            }
                        },
                        "props": {
                            "type": "object"
                        },
                        "position": {
                            "$ref": "#/definitions/position"
                        },
                        "events": {
                            "type": "object"
                        },
                        "children": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/component"
                            }
                        }
                    }
                },
                "position": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "width": {"type": "number", "minimum": 1},
                        "height": {"type": "number", "minimum": 1},
                        "basis": {"type": "string"},
                        "grow": {"type": "number"},
                        "shrink": {"type": "number"}
                    }
                }
            }
        }
    
    def validate_view_resource(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Perspective view resource structure"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'optimizations': []
        }
        
        try:
            # JSON Schema validation
            jsonschema.validate(resource_data, self.view_schema)
            
            # Additional business logic validation
            view_data = resource_data['resource']['data']['view']
            
            # Validate component hierarchy
            root_validation = self._validate_component_hierarchy(view_data['root'])
            result['errors'].extend(root_validation['errors'])
            result['warnings'].extend(root_validation['warnings'])
            
            # Check for performance issues
            performance_issues = self._check_performance_patterns(view_data)
            result['warnings'].extend(performance_issues)
            
            # Suggest optimizations
            optimizations = self._suggest_optimizations(view_data)
            result['optimizations'].extend(optimizations)
            
            if result['errors']:
                result['valid'] = False
                
        except jsonschema.ValidationError as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'schema_violation',
                'message': e.message,
                'path': list(e.absolute_path),
                'schema_path': list(e.schema_path)
            })
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'validation_error',
                'message': str(e)
            })
        
        return result
    
    def _validate_component_hierarchy(self, component: Dict[str, Any], path: str = "root") -> Dict[str, Any]:
        """Validate component hierarchy for issues"""
        result = {
            'errors': [],
            'warnings': []
        }
        
        component_type = component.get('type', '')
        
        # Check for proper component naming
        meta = component.get('meta', {})
        if 'name' not in meta:
            result['warnings'].append({
                'type': 'missing_name',
                'message': f'Component at {path} should have a name for better debugging',
                'path': path,
                'component_type': component_type
            })
        
        # Check for excessive nesting
        children = component.get('children', [])
        if self._calculate_nesting_depth(component) > 8:
            result['warnings'].append({
                'type': 'deep_nesting',
                'message': f'Deep component nesting at {path} may impact performance',
                'path': path,
                'nesting_depth': self._calculate_nesting_depth(component)
            })
        
        # Recursively validate children
        for i, child in enumerate(children):
            child_path = f"{path}.children[{i}]"
            child_result = self._validate_component_hierarchy(child, child_path)
            result['errors'].extend(child_result['errors'])
            result['warnings'].extend(child_result['warnings'])
        
        return result
    
    def _check_performance_patterns(self, view_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance anti-patterns in view"""
        warnings = []
        
        # Count total components
        total_components = self._count_components(view_data['root'])
        if total_components > 100:
            warnings.append({
                'type': 'too_many_components',
                'message': f'View has {total_components} components, consider breaking into multiple views',
                'component_count': total_components
            })
        
        # Check for binding complexity
        binding_count = self._count_bindings(view_data['root'])
        if binding_count > 50:
            warnings.append({
                'type': 'many_bindings',
                'message': f'View has {binding_count} bindings, may impact load time',
                'binding_count': binding_count
            })
        
        return warnings
    
    def _suggest_optimizations(self, view_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest optimizations for view structure"""
        optimizations = []
        
        # Check for parameter usage
        params = view_data.get('params', {})
        param_usage = self._analyze_parameter_usage(view_data['root'], set(params.keys()))
        
        unused_params = param_usage['unused']
        if unused_params:
            optimizations.append({
                'type': 'unused_parameters',
                'message': f'Remove unused parameters: {", ".join(unused_params)}',
                'unused_parameters': unused_params
            })
        
        # Check for redundant styling
        style_analysis = self._analyze_styling_patterns(view_data['root'])
        if style_analysis['redundant_styles'] > 5:
            optimizations.append({
                'type': 'redundant_styling',
                'message': 'Consider using CSS classes or theme variables for repeated styles',
                'redundant_count': style_analysis['redundant_styles']
            })
        
        return optimizations
```

### 2. Resource Generation Patterns

#### AI-Driven Resource Generator

```python
# generation/resource_generator.py
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class ResourceGenerator:
    def __init__(self):
        self.component_templates = self._load_component_templates()
        self.validation_patterns = self._load_validation_patterns()
    
    def generate_view_resource(self, 
                             view_config: Dict[str, Any],
                             components: List[Dict[str, Any]],
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate complete view resource from configuration"""
        
        # Create base resource structure
        resource = {
            "resource": {
                "type": "com.inductiveautomation.perspective.common.resource.View",
                "version": 1,
                "data": {
                    "view": {
                        "params": self._generate_view_parameters(view_config),
                        "props": self._generate_view_properties(view_config),
                        "root": self._generate_root_container(components, view_config),
                        "custom": self._generate_custom_properties(view_config, metadata)
                    }
                }
            }
        }
        
        # Apply WHK-specific patterns
        self._apply_whk_patterns(resource, view_config)
        
        # Optimize structure
        self._optimize_resource_structure(resource)
        
        return resource
    
    def _generate_view_parameters(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate view parameters based on configuration"""
        params = {}
        
        # Standard WHK parameters
        whk_standard_params = {
            'equipmentId': {
                'paramType': 'string',
                'value': config.get('default_equipment_id', 'EQUIP-001')
            },
            'operatorLevel': {
                'paramType': 'int', 
                'value': config.get('default_operator_level', 1)
            },
            'refreshInterval': {
                'paramType': 'int',
                'value': config.get('refresh_interval', 5000)
            }
        }
        
        # Add standard parameters
        params.update(whk_standard_params)
        
        # Add custom parameters from config
        custom_params = config.get('parameters', {})
        for param_name, param_config in custom_params.items():
            params[param_name] = {
                'paramType': param_config.get('type', 'string'),
                'value': param_config.get('default_value', '')
            }
        
        return params
    
    def _generate_view_properties(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate view-level properties"""
        props = {}
        
        # Default size based on view type
        view_type = config.get('view_type', 'standard')
        default_sizes = {
            'overview': {'width': 1920, 'height': 1080},
            'detail': {'width': 1200, 'height': 800},
            'popup': {'width': 600, 'height': 400},
            'standard': {'width': 1200, 'height': 800}
        }
        
        props['defaultSize'] = default_sizes.get(view_type, default_sizes['standard'])
        
        # Responsive breakpoints for WHK standard
        props['breakpoints'] = {
            'small': {'maxWidth': 768},
            'medium': {'maxWidth': 1024},
            'large': {'maxWidth': 1440}
        }
        
        return props
    
    def _generate_root_container(self, components: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate root container with components"""
        
        # Determine optimal container type
        container_type = self._determine_container_type(components, config)
        
        root = {
            "type": container_type,
            "meta": {
                "name": "root"
            },
            "props": self._generate_container_props(container_type, config),
            "position": {
                "basis": "100px"
            }
        }
        
        # Add children components
        if components:
            root['children'] = self._layout_components(components, container_type, config)
        
        return root
    
    def _determine_container_type(self, components: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
        """Determine optimal container type based on components and configuration"""
        
        layout_preference = config.get('layout_preference', 'auto')
        
        if layout_preference != 'auto':
            return f"ia.container.{layout_preference}"
        
        # Auto-determine based on component analysis
        component_count = len(components)
        has_dynamic_sizing = any(
            comp.get('responsive', False) for comp in components
        )
        
        if component_count <= 3 and not has_dynamic_sizing:
            return "ia.container.coord"  # Coordinate for simple layouts
        elif has_dynamic_sizing or component_count > 10:
            return "ia.container.flex"   # Flex for responsive layouts
        else:
            return "ia.container.coord"  # Default to coordinate
    
    def _layout_components(self, components: List[Dict[str, Any]], container_type: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Layout components optimally within container"""
        
        if container_type == "ia.container.flex":
            return self._layout_flex_components(components, config)
        else:
            return self._layout_coordinate_components(components, config)
    
    def _layout_flex_components(self, components: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Layout components using flexbox principles"""
        
        layouted_components = []
        
        # Analyze component priorities and grouping
        component_groups = self._group_components_by_priority(components)
        
        for group in component_groups:
            for i, component in enumerate(group):
                # Add flex-specific positioning
                component['position'] = {
                    'grow': component.get('flex_grow', 0),
                    'shrink': component.get('flex_shrink', 1),
                    'basis': component.get('flex_basis', 'auto')
                }
                
                layouted_components.append(component)
        
        return layouted_components
    
    def _layout_coordinate_components(self, components: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Layout components using coordinate positioning"""
        
        layouted_components = []
        
        # Grid-based layout for coordinate container
        grid_config = config.get('grid', {
            'columns': 12,
            'row_height': 60,
            'margin': 10
        })
        
        current_row = 0
        current_col = 0
        
        for component in components:
            # Calculate position based on component size and current position
            comp_width = component.get('width', 200)
            comp_height = component.get('height', 40)
            
            # Convert grid position to pixels
            x = current_col * (comp_width + grid_config['margin'])
            y = current_row * (grid_config['row_height'] + grid_config['margin'])
            
            component['position'] = {
                'x': x,
                'y': y,
                'width': comp_width,
                'height': comp_height
            }
            
            layouted_components.append(component)
            
            # Update position for next component
            current_col += 1
            if current_col >= grid_config['columns']:
                current_col = 0
                current_row += 1
        
        return layouted_components
    
    def _apply_whk_patterns(self, resource: Dict[str, Any], config: Dict[str, Any]):
        """Apply WHK-specific patterns to resource"""
        
        view_data = resource['resource']['data']['view']
        
        # Add WHK custom properties
        if 'custom' not in view_data:
            view_data['custom'] = {}
        
        view_data['custom']['whkMetadata'] = {
            'version': '2.0',
            'created': datetime.now().isoformat(),
            'area': config.get('area', 'General'),
            'process': config.get('process', 'Unknown'),
            'criticality': config.get('criticality', 'standard'),
            'compliance': {
                'fda': config.get('fda_compliant', False),
                'iso': config.get('iso_compliant', False)
            }
        }
        
        # Apply WHK security patterns
        if config.get('require_security', True):
            self._apply_security_patterns(view_data, config)
        
        # Apply WHK styling patterns
        self._apply_whk_styling(view_data, config)
    
    def _apply_security_patterns(self, view_data: Dict[str, Any], config: Dict[str, Any]):
        """Apply WHK security patterns"""
        
        security_level = config.get('security_level', 'standard')
        
        # Add security metadata
        view_data['custom']['security'] = {
            'level': security_level,
            'required_roles': self._get_required_roles(security_level),
            'audit_enabled': security_level in ['high', 'critical'],
            'session_timeout': self._get_session_timeout(security_level)
        }
    
    def _apply_whk_styling(self, view_data: Dict[str, Any], config: Dict[str, Any]):
        """Apply WHK styling standards"""
        
        # Apply theme and color scheme
        theme = config.get('theme', 'whk_standard')
        
        def apply_styling_recursive(component):
            if 'props' not in component:
                component['props'] = {}
            
            # Apply WHK standard styles based on component type
            comp_type = component.get('type', '')
            whk_styles = self._get_whk_styles(comp_type, theme)
            
            if 'style' not in component['props']:
                component['props']['style'] = {}
            
            # Merge WHK styles (don't override existing styles)
            for style_key, style_value in whk_styles.items():
                if style_key not in component['props']['style']:
                    component['props']['style'][style_key] = style_value
            
            # Recursively apply to children
            for child in component.get('children', []):
                apply_styling_recursive(child)
        
        apply_styling_recursive(view_data['root'])
    
    def _get_whk_styles(self, component_type: str, theme: str) -> Dict[str, Any]:
        """Get WHK standard styles for component type"""
        
        whk_styles = {
            'ia.display.button': {
                'fontFamily': 'var(--whk-font-primary)',
                'borderRadius': '4px',
                'fontSize': '14px'
            },
            'ia.display.label': {
                'fontFamily': 'var(--whk-font-primary)',
                'color': 'var(--whk-text-primary)'
            },
            'ia.input.numeric-entry-field': {
                'fontFamily': 'var(--whk-font-mono)',
                'border': '1px solid var(--whk-border-primary)',
                'borderRadius': '2px'
            },
            'ia.display.table': {
                'fontFamily': 'var(--whk-font-primary)',
                'fontSize': '12px'
            }
        }
        
        return whk_styles.get(component_type, {})
    
    def _optimize_resource_structure(self, resource: Dict[str, Any]):
        """Optimize resource structure for performance"""
        
        view_data = resource['resource']['data']['view']
        
        # Remove empty objects
        self._remove_empty_objects(view_data)
        
        # Optimize binding structures
        self._optimize_bindings(view_data['root'])
        
        # Consolidate repeated styles
        self._consolidate_styles(view_data['root'])
    
    def _remove_empty_objects(self, obj: Any):
        """Remove empty objects and arrays recursively"""
        if isinstance(obj, dict):
            keys_to_remove = []
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    self._remove_empty_objects(value)
                    if not value:  # Empty after cleanup
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del obj[key]
        
        elif isinstance(obj, list):
            obj[:] = [item for item in obj if item or item == 0 or item is False]
```

### 3. Resource Optimization Patterns

#### Performance Optimization for Resources

```python
# optimization/resource_optimizer.py
from typing import Dict, List, Any
import json

class ResourceOptimizer:
    def __init__(self):
        self.optimization_rules = self._load_optimization_rules()
        
    def optimize_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Apply comprehensive optimizations to resource"""
        
        optimized = json.loads(json.dumps(resource))  # Deep copy
        
        optimizations_applied = []
        
        # Structural optimizations
        struct_opts = self._optimize_structure(optimized)
        optimizations_applied.extend(struct_opts)
        
        # Binding optimizations
        binding_opts = self._optimize_bindings(optimized)
        optimizations_applied.extend(binding_opts)
        
        # Style optimizations
        style_opts = self._optimize_styles(optimized)
        optimizations_applied.extend(style_opts)
        
        # Performance optimizations
        perf_opts = self._optimize_performance(optimized)
        optimizations_applied.extend(perf_opts)
        
        # Add optimization metadata
        if optimizations_applied:
            if 'custom' not in optimized['resource']['data']['view']:
                optimized['resource']['data']['view']['custom'] = {}
            
            optimized['resource']['data']['view']['custom']['optimizations'] = {
                'applied': optimizations_applied,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
        
        return optimized
    
    def _optimize_structure(self, resource: Dict[str, Any]) -> List[str]:
        """Optimize resource structure"""
        optimizations = []
        
        view_data = resource['resource']['data']['view']
        root = view_data['root']
        
        # Flatten unnecessary container nesting
        if self._has_single_child_containers(root):
            self._flatten_containers(root)
            optimizations.append('flattened_container_nesting')
        
        # Remove unused parameters
        unused_params = self._find_unused_parameters(view_data)
        if unused_params:
            for param in unused_params:
                del view_data['params'][param]
            optimizations.append(f'removed_unused_parameters: {", ".join(unused_params)}')
        
        return optimizations
    
    def _optimize_bindings(self, resource: Dict[str, Any]) -> List[str]:
        """Optimize binding configurations"""
        optimizations = []
        
        view_data = resource['resource']['data']['view']
        
        # Convert expression bindings to tag bindings where beneficial
        expr_to_tag = self._convert_expressions_to_tags(view_data['root'])
        if expr_to_tag > 0:
            optimizations.append(f'converted_{expr_to_tag}_expressions_to_tag_bindings')
        
        # Consolidate similar transform scripts
        consolidated = self._consolidate_transforms(view_data['root'])
        if consolidated > 0:
            optimizations.append(f'consolidated_{consolidated}_transform_scripts')
        
        return optimizations
    
    def _optimize_styles(self, resource: Dict[str, Any]) -> List[str]:
        """Optimize styling definitions"""
        optimizations = []
        
        view_data = resource['resource']['data']['view']
        
        # Extract common styles to CSS variables
        common_styles = self._extract_common_styles(view_data['root'])
        if common_styles:
            self._apply_css_variables(view_data['root'], common_styles)
            optimizations.append(f'extracted_{len(common_styles)}_common_styles_to_variables')
        
        # Remove redundant style properties
        redundant_removed = self._remove_redundant_styles(view_data['root'])
        if redundant_removed > 0:
            optimizations.append(f'removed_{redundant_removed}_redundant_style_properties')
        
        return optimizations
    
    def _optimize_performance(self, resource: Dict[str, Any]) -> List[str]:
        """Apply performance optimizations"""
        optimizations = []
        
        view_data = resource['resource']['data']['view']
        
        # Optimize polling bindings
        polling_optimized = self._optimize_polling_bindings(view_data['root'])
        if polling_optimized > 0:
            optimizations.append(f'optimized_{polling_optimized}_polling_bindings')
        
        # Add lazy loading for complex components
        lazy_loading = self._add_lazy_loading(view_data['root'])
        if lazy_loading > 0:
            optimizations.append(f'added_lazy_loading_to_{lazy_loading}_components')
        
        return optimizations
```

This comprehensive resource.json handling system ensures AI-generated Ignition resources are properly structured, validated, and optimized for production deployment while maintaining compatibility with Ignition's project structure and Git workflows.