# Perspective Component JSON Schema Specifications

## Overview

This document provides comprehensive JSON Schema specifications for all major Ignition Perspective components. These schemas enable strict validation of component configurations, ensuring generated components are syntactically correct, follow best practices, and integrate properly with the Ignition platform.

## 🎯 Schema Objectives

### Primary Goals
- **Strict Validation**: Ensure all component properties conform to Ignition specifications
- **Type Safety**: Validate data types, ranges, and formats for all properties
- **Binding Validation**: Verify binding configurations are valid and performant
- **Security Compliance**: Enforce security property requirements for sensitive components
- **Performance Optimization**: Detect configuration patterns that may impact performance

### Schema Features
- **Comprehensive Coverage**: All major Perspective components included
- **Context-Aware Validation**: Different validation rules based on component usage
- **Production Patterns**: Schemas include patterns learned from production systems
- **WHK-Specific Extensions**: Custom properties and validations for whiskey house operations

## 📋 Base Schema Definitions

### Core Component Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.whk.local/perspective/base-component.json",
  "title": "Perspective Base Component",
  "description": "Base schema for all Perspective components",
  "type": "object",
  "required": ["type", "props"],
  "properties": {
    "type": {
      "type": "string",
      "description": "Component type identifier",
      "pattern": "^ia\\.(display|input|chart|container|media)\\.[a-z-]+$"
    },
    "props": {
      "type": "object",
      "description": "Component properties",
      "additionalProperties": true
    },
    "position": {
      "$ref": "#/definitions/position"
    },
    "meta": {
      "$ref": "#/definitions/meta"
    },
    "events": {
      "$ref": "#/definitions/events"
    },
    "custom": {
      "type": "object",
      "description": "Custom component properties",
      "patternProperties": {
        "^[a-z][a-zA-Z0-9]*$": {
          "description": "Custom property with camelCase naming"
        }
      },
      "additionalProperties": false
    }
  },
  "definitions": {
    "position": {
      "type": "object",
      "properties": {
        "x": {"type": "integer", "minimum": 0},
        "y": {"type": "integer", "minimum": 0},
        "width": {"type": "integer", "minimum": 1},
        "height": {"type": "integer", "minimum": 1},
        "z": {"type": "integer", "minimum": 0}
      },
      "additionalProperties": false
    },
    "meta": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
          "description": "Component name using PascalCase or camelCase"
        },
        "security": {
          "$ref": "#/definitions/security"
        }
      }
    },
    "security": {
      "type": "object",
      "properties": {
        "roleAccess": {
          "type": "array",
          "items": {"type": "string"},
          "minItems": 1,
          "description": "Required roles for component access"
        },
        "zoneRestrictions": {
          "type": "array", 
          "items": {"type": "string"},
          "description": "Security zone restrictions"
        }
      }
    },
    "events": {
      "type": "object",
      "patternProperties": {
        "^on[A-Z][a-zA-Z0-9]*$": {
          "$ref": "#/definitions/eventHandler"
        }
      },
      "additionalProperties": false
    },
    "eventHandler": {
      "type": "object",
      "properties": {
        "config": {
          "type": "object",
          "properties": {
            "script": {
              "type": "string",
              "description": "Jython script for event handling"
            }
          },
          "required": ["script"]
        }
      },
      "required": ["config"]
    },
    "binding": {
      "type": "object",
      "required": ["type", "config"],
      "properties": {
        "type": {
          "enum": ["tag", "property", "expression", "transform"],
          "description": "Type of binding"
        },
        "config": {
          "type": "object",
          "description": "Binding configuration specific to type"
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {"type": {"const": "tag"}}
          },
          "then": {
            "properties": {
              "config": {
                "$ref": "#/definitions/tagBinding"
              }
            }
          }
        },
        {
          "if": {
            "properties": {"type": {"const": "expression"}}
          },
          "then": {
            "properties": {
              "config": {
                "$ref": "#/definitions/expressionBinding"
              }
            }
          }
        },
        {
          "if": {
            "properties": {"type": {"const": "transform"}}
          },
          "then": {
            "properties": {
              "config": {
                "$ref": "#/definitions/transformBinding"
              }
            }
          }
        }
      ]
    },
    "tagBinding": {
      "type": "object",
      "required": ["path"],
      "properties": {
        "path": {
          "type": "string",
          "pattern": "^\\[.+\\].+",
          "description": "Tag path in format [provider]folder/tagname"
        },
        "polling": {
          "enum": ["subscribe", "direct", "driven"],
          "default": "subscribe",
          "description": "Tag polling mode"
        },
        "deadband": {
          "type": "number",
          "minimum": 0,
          "description": "Deadband for numeric tags"
        },
        "indirect": {
          "type": "boolean",
          "default": false,
          "description": "Use indirect tag binding"
        }
      },
      "additionalProperties": false
    },
    "expressionBinding": {
      "type": "object",
      "required": ["expression"],
      "properties": {
        "expression": {
          "type": "string",
          "minLength": 1,
          "description": "Expression language binding"
        },
        "runScript": {
          "enum": ["gateway", "client"],
          "default": "gateway",
          "description": "Where to execute expression"
        }
      },
      "additionalProperties": false
    },
    "transformBinding": {
      "type": "object",
      "required": ["script"],
      "properties": {
        "script": {
          "type": "string",
          "minLength": 1,
          "description": "Transform script"
        },
        "runScript": {
          "enum": ["gateway", "client"], 
          "default": "gateway"
        }
      },
      "additionalProperties": false
    },
    "styleObject": {
      "type": "object",
      "properties": {
        "backgroundColor": {"$ref": "#/definitions/colorValue"},
        "color": {"$ref": "#/definitions/colorValue"},
        "fontSize": {"$ref": "#/definitions/sizeValue"},
        "fontWeight": {"enum": ["normal", "bold", "bolder", "lighter"]},
        "textAlign": {"enum": ["left", "center", "right", "justify"]},
        "border": {"type": "string"},
        "borderRadius": {"$ref": "#/definitions/sizeValue"},
        "margin": {"$ref": "#/definitions/sizeValue"},
        "padding": {"$ref": "#/definitions/sizeValue"},
        "width": {"$ref": "#/definitions/sizeValue"},
        "height": {"$ref": "#/definitions/sizeValue"}
      },
      "additionalProperties": false
    },
    "colorValue": {
      "anyOf": [
        {
          "type": "string",
          "pattern": "^#[0-9A-Fa-f]{6}$",
          "description": "Hex color value"
        },
        {
          "type": "string", 
          "pattern": "^var\\(--[a-zA-Z0-9-]+\\)$",
          "description": "CSS custom property (theme variable)"
        },
        {
          "type": "string",
          "pattern": "^rgb\\(\\d+,\\s*\\d+,\\s*\\d+\\)$",
          "description": "RGB color value"
        },
        {
          "type": "string",
          "pattern": "^rgba\\(\\d+,\\s*\\d+,\\s*\\d+,\\s*[0-1](?:\\.[0-9]+)?\\)$",
          "description": "RGBA color value"
        }
      ]
    },
    "sizeValue": {
      "anyOf": [
        {
          "type": "string",
          "pattern": "^\\d+(?:\\.\\d+)?(?:px|em|rem|%|vh|vw)$",
          "description": "CSS size value with units"
        },
        {
          "type": "number",
          "description": "Numeric size (pixels)"
        }
      ]
    }
  }
}
```

## 🔘 Button Component Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.whk.local/perspective/button.json",
  "title": "Perspective Button Component",
  "description": "Button component with production-grade validation",
  "allOf": [
    {"$ref": "base-component.json"},
    {
      "properties": {
        "type": {"const": "ia.display.button"},
        "props": {
          "type": "object",
          "required": ["text"],
          "properties": {
            "text": {
              "type": "string",
              "minLength": 1,
              "maxLength": 100,
              "description": "Button display text"
            },
            "enabled": {
              "type": "boolean",
              "default": true,
              "description": "Button enabled state"
            },
            "style": {
              "$ref": "base-component.json#/definitions/styleObject"
            },
            "confirm": {
              "type": "boolean",
              "default": false,
              "description": "Show confirmation dialog"
            },
            "confirmMessage": {
              "type": "string",
              "description": "Confirmation dialog message"
            },
            "variant": {
              "enum": ["primary", "secondary", "success", "danger", "warning", "info"],
              "default": "primary",
              "description": "Button style variant"
            }
          },
          "additionalProperties": false,
          "allOf": [
            {
              "if": {
                "properties": {"confirm": {"const": true}}
              },
              "then": {
                "required": ["confirmMessage"],
                "properties": {
                  "confirmMessage": {
                    "minLength": 1,
                    "description": "Confirmation message is required when confirm is true"
                  }
                }
              }
            }
          ]
        },
        "events": {
          "type": "object",
          "properties": {
            "onActionPerformed": {
              "$ref": "base-component.json#/definitions/eventHandler"
            }
          },
          "additionalProperties": false
        }
      },
      "whk_validations": {
        "production_control_button": {
          "description": "Buttons that control production equipment",
          "condition": "events.onActionPerformed.config.script contains tag write to Equipment or Process tags",
          "requirements": {
            "security_required": true,
            "confirmation_required": true,
            "audit_logging": true
          },
          "schema_extension": {
            "required": ["meta"],
            "properties": {
              "meta": {
                "required": ["security"],
                "properties": {
                  "security": {
                    "required": ["roleAccess"]
                  }
                }
              },
              "props": {
                "required": ["confirm"],
                "properties": {
                  "confirm": {"const": true}
                }
              }
            }
          }
        },
        "emergency_stop_button": {
          "description": "Emergency stop buttons",
          "condition": "props.text matches /(Emergency|E-Stop|STOP)/i",
          "requirements": {
            "no_confirmation": true,
            "immediate_action": true,
            "high_visibility": true
          },
          "schema_extension": {
            "properties": {
              "props": {
                "properties": {
                  "confirm": {"const": false},
                  "variant": {"const": "danger"},
                  "style": {
                    "properties": {
                      "backgroundColor": {"const": "#ff6b35"},
                      "fontSize": {"minimum": 16}
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  ]
}
```

## 🔢 Numeric Entry Field Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.whk.local/perspective/numeric-entry.json",
  "title": "Perspective Numeric Entry Field",
  "description": "Numeric input component with validation for process control",
  "allOf": [
    {"$ref": "base-component.json"},
    {
      "properties": {
        "type": {"const": "ia.input.numeric-entry-field"},
        "props": {
          "type": "object",
          "required": ["value"],
          "properties": {
            "value": {
              "type": "number",
              "description": "Current numeric value"
            },
            "minValue": {
              "type": "number",
              "description": "Minimum allowed value"
            },
            "maxValue": {
              "type": "number",
              "description": "Maximum allowed value"
            },
            "format": {
              "type": "string",
              "pattern": "^[0-9#.,]+$",
              "description": "Number format pattern",
              "examples": ["0", "0.0", "0.00", "#,##0.00"]
            },
            "readOnly": {
              "type": "boolean",
              "default": false,
              "description": "Field is read-only"
            },
            "placeholder": {
              "type": "string",
              "description": "Placeholder text"
            },
            "style": {
              "$ref": "base-component.json#/definitions/styleObject"
            }
          },
          "additionalProperties": false,
          "allOf": [
            {
              "if": {
                "properties": {
                  "minValue": {"type": "number"},
                  "maxValue": {"type": "number"}
                }
              },
              "then": {
                "properties": {
                  "minValue": {
                    "description": "minValue must be less than maxValue"
                  }
                },
                "if": {
                  "properties": {
                    "minValue": {"type": "number"},
                    "maxValue": {"type": "number"}
                  }
                },
                "then": {
                  "properties": {
                    "value": {
                      "minimum": {"$data": "1/minValue"},
                      "maximum": {"$data": "1/maxValue"}
                    }
                  }
                }
              }
            }
          ]
        },
        "events": {
          "type": "object",
          "properties": {
            "onTextChanged": {
              "$ref": "base-component.json#/definitions/eventHandler"
            },
            "onActionPerformed": {
              "$ref": "base-component.json#/definitions/eventHandler"
            }
          },
          "additionalProperties": false
        }
      },
      "whk_validations": {
        "recipe_parameter": {
          "description": "Recipe parameter inputs",
          "condition": "custom.parameterType exists or binding path contains 'recipe'",
          "requirements": {
            "range_validation": true,
            "engineering_units": true,
            "change_logging": true
          },
          "schema_extension": {
            "required": ["custom"],
            "properties": {
              "props": {
                "required": ["minValue", "maxValue", "format"]
              },
              "custom": {
                "required": ["engineeringUnits", "parameterType"],
                "properties": {
                  "engineeringUnits": {
                    "type": "string",
                    "enum": ["°F", "°C", "PSI", "GPM", "RPM", "%", "pH"],
                    "description": "Engineering units for the parameter"
                  },
                  "parameterType": {
                    "enum": ["temperature", "pressure", "flow", "speed", "percentage", "ph"],
                    "description": "Type of process parameter"
                  },
                  "criticalLevel": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 3,
                    "description": "Criticality level (1=normal, 2=important, 3=critical)"
                  }
                }
              }
            }
          },
          "validation_ranges": {
            "temperature": {"min": -40, "max": 300, "units": "°F"},
            "pressure": {"min": 0, "max": 150, "units": "PSI"},
            "flow": {"min": 0, "max": 1000, "units": "GPM"},
            "speed": {"min": 0, "max": 3600, "units": "RPM"},
            "percentage": {"min": 0, "max": 100, "units": "%"},
            "ph": {"min": 0, "max": 14, "units": "pH"}
          }
        },
        "critical_setpoint": {
          "description": "Critical process setpoints",
          "condition": "binding path contains 'setpoint' and custom.criticalLevel >= 2",
          "requirements": {
            "confirmation_required": true,
            "supervisor_approval": "criticalLevel === 3",
            "audit_logging": true,
            "backup_value": true
          },
          "schema_extension": {
            "required": ["meta"],
            "properties": {
              "meta": {
                "required": ["security"],
                "properties": {
                  "security": {
                    "required": ["roleAccess"],
                    "properties": {
                      "roleAccess": {
                        "minItems": 1,
                        "items": {
                          "enum": ["Operators", "Engineers", "Supervisors"]
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  ]
}
```

## 📊 Table Component Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.whk.local/perspective/table.json",
  "title": "Perspective Table Component",
  "description": "Table component optimized for process data display",
  "allOf": [
    {"$ref": "base-component.json"},
    {
      "properties": {
        "type": {"const": "ia.display.table"},
        "props": {
          "type": "object",
          "required": ["data"],
          "properties": {
            "data": {
              "oneOf": [
                {
                  "type": "array",
                  "description": "Direct data array",
                  "maxItems": 1000
                },
                {
                  "type": "object",
                  "description": "Data binding",
                  "properties": {
                    "binding": {
                      "$ref": "base-component.json#/definitions/binding"
                    }
                  },
                  "required": ["binding"]
                }
              ]
            },
            "columns": {
              "type": "array",
              "minItems": 1,
              "maxItems": 20,
              "items": {
                "$ref": "#/definitions/tableColumn"
              },
              "description": "Table column definitions"
            },
            "selection": {
              "enum": ["none", "single", "multiple"],
              "default": "none",
              "description": "Row selection mode"
            },
            "paginationEnabled": {
              "type": "boolean",
              "default": false,
              "description": "Enable pagination"
            },
            "pageSize": {
              "type": "integer",
              "minimum": 10,
              "maximum": 100,
              "default": 25,
              "description": "Number of rows per page"
            },
            "virtualScrolling": {
              "type": "boolean",
              "default": false,
              "description": "Enable virtual scrolling for large datasets"
            },
            "sortable": {
              "type": "boolean",
              "default": true,
              "description": "Enable column sorting"
            },
            "filterable": {
              "type": "boolean",
              "default": false,
              "description": "Enable column filtering"
            },
            "style": {
              "$ref": "base-component.json#/definitions/styleObject"
            }
          },
          "additionalProperties": false,
          "allOf": [
            {
              "if": {
                "properties": {
                  "data": {"type": "array"},
                  "virtualScrolling": {"const": false}
                }
              },
              "then": {
                "properties": {
                  "data": {
                    "maxItems": 100,
                    "description": "Large datasets require virtual scrolling or pagination"
                  }
                }
              }
            },
            {
              "if": {
                "properties": {"paginationEnabled": {"const": true}}
              },
              "then": {
                "required": ["pageSize"]
              }
            }
          ]
        },
        "events": {
          "type": "object",
          "properties": {
            "onRowClick": {
              "$ref": "base-component.json#/definitions/eventHandler"
            },
            "onSelectionChanged": {
              "$ref": "base-component.json#/definitions/eventHandler"
            }
          },
          "additionalProperties": false
        }
      },
      "definitions": {
        "tableColumn": {
          "type": "object",
          "required": ["field", "header"],
          "properties": {
            "field": {
              "type": "string",
              "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
              "description": "Data field name"
            },
            "header": {
              "type": "string",
              "minLength": 1,
              "maxLength": 50,
              "description": "Column header text"
            },
            "width": {
              "type": "integer",
              "minimum": 50,
              "maximum": 500,
              "description": "Column width in pixels"
            },
            "sortable": {
              "type": "boolean",
              "default": true,
              "description": "Column is sortable"
            },
            "filterable": {
              "type": "boolean", 
              "default": false,
              "description": "Column is filterable"
            },
            "editable": {
              "type": "boolean",
              "default": false,
              "description": "Column cells are editable"
            },
            "render": {
              "enum": ["auto", "date", "number", "boolean", "link", "status"],
              "default": "auto",
              "description": "Cell render type"
            },
            "number": {
              "type": "object",
              "description": "Number formatting options",
              "properties": {
                "format": {
                  "type": "string",
                  "pattern": "^[0-9#.,]+$",
                  "description": "Number format pattern"
                },
                "units": {
                  "type": "string",
                  "description": "Engineering units display"
                }
              }
            },
            "date": {
              "type": "object",
              "description": "Date formatting options",
              "properties": {
                "format": {
                  "type": "string",
                  "enum": ["MM/dd/yyyy", "yyyy-MM-dd", "MM/dd/yyyy HH:mm", "yyyy-MM-dd HH:mm:ss"],
                  "description": "Date format pattern"
                }
              }
            }
          },
          "additionalProperties": false
        }
      },
      "whk_validations": {
        "batch_history_table": {
          "description": "Batch history and production data tables",
          "condition": "data binding path contains 'batch' or columns include batch_id",
          "required_columns": [
            {"field": "batch_id", "header": "Batch ID", "required": true},
            {"field": "start_time", "header": "Start Time", "render": "date"},
            {"field": "status", "header": "Status", "render": "status"}
          ],
          "performance_requirements": {
            "pagination_required": "row_count > 100",
            "virtual_scrolling_recommended": "row_count > 500"
          },
          "schema_extension": {
            "properties": {
              "props": {
                "required": ["paginationEnabled"],
                "properties": {
                  "paginationEnabled": {"const": true},
                  "pageSize": {"maximum": 50}
                }
              }
            }
          }
        },
        "real_time_data_table": {
          "description": "Tables displaying real-time process data",
          "condition": "data binding polling != 'subscribe' or update frequency > 1Hz",
          "performance_requirements": {
            "virtual_scrolling": true,
            "update_throttling": "500ms",
            "max_visible_rows": 100
          },
          "schema_extension": {
            "properties": {
              "props": {
                "required": ["virtualScrolling"],
                "properties": {
                  "virtualScrolling": {"const": true}
                }
              }
            }
          }
        }
      }
    }
  ]
}
```

## 📈 Chart Component Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.whk.local/perspective/chart.json",
  "title": "Perspective Chart Components",
  "description": "Chart components for process data visualization",
  "oneOf": [
    {"$ref": "#/definitions/timeSeriesChart"},
    {"$ref": "#/definitions/barChart"},
    {"$ref": "#/definitions/pieChart"}
  ],
  "definitions": {
    "timeSeriesChart": {
      "allOf": [
        {"$ref": "base-component.json"},
        {
          "properties": {
            "type": {"const": "ia.chart.timeseries"},
            "props": {
              "type": "object",
              "required": ["series"],
              "properties": {
                "series": {
                  "type": "array",
                  "minItems": 1,
                  "maxItems": 10,
                  "items": {
                    "$ref": "#/definitions/timeSeries"
                  },
                  "description": "Chart data series"
                },
                "xAxis": {
                  "$ref": "#/definitions/timeAxis"
                },
                "yAxes": {
                  "type": "array",
                  "minItems": 1,
                  "maxItems": 4,
                  "items": {
                    "$ref": "#/definitions/valueAxis"
                  }
                },
                "legend": {
                  "$ref": "#/definitions/chartLegend"
                },
                "tooltip": {
                  "$ref": "#/definitions/chartTooltip"
                },
                "realTimeEnabled": {
                  "type": "boolean",
                  "default": false,
                  "description": "Enable real-time data updates"
                },
                "timeWindow": {
                  "type": "string",
                  "pattern": "^\\d+[smhdw]$",
                  "description": "Time window for real-time charts (e.g., '1h', '30m')"
                }
              },
              "additionalProperties": false
            }
          }
        }
      ]
    },
    "timeSeries": {
      "type": "object",
      "required": ["name", "data"],
      "properties": {
        "name": {
          "type": "string",
          "minLength": 1,
          "maxLength": 50,
          "description": "Series name"
        },
        "data": {
          "oneOf": [
            {
              "type": "array",
              "description": "Direct data array"
            },
            {
              "type": "object",
              "properties": {
                "binding": {
                  "$ref": "base-component.json#/definitions/binding"
                }
              },
              "required": ["binding"]
            }
          ]
        },
        "yAxis": {
          "type": "integer",
          "minimum": 0,
          "maximum": 3,
          "default": 0,
          "description": "Y-axis index for this series"
        },
        "color": {
          "$ref": "base-component.json#/definitions/colorValue",
          "description": "Series color"
        },
        "lineStyle": {
          "enum": ["solid", "dashed", "dotted"],
          "default": "solid"
        },
        "marker": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean", "default": false},
            "symbol": {"enum": ["circle", "square", "diamond", "triangle"]},
            "size": {"type": "integer", "minimum": 2, "maximum": 10}
          }
        }
      },
      "additionalProperties": false
    },
    "timeAxis": {
      "type": "object",
      "properties": {
        "label": {"type": "string"},
        "format": {
          "enum": ["auto", "HH:mm", "MM/dd HH:mm", "MM/dd/yyyy"],
          "default": "auto"
        },
        "gridLines": {"type": "boolean", "default": true}
      }
    },
    "valueAxis": {
      "type": "object",
      "properties": {
        "label": {"type": "string"},
        "min": {"type": "number"},
        "max": {"type": "number"},
        "units": {"type": "string"},
        "gridLines": {"type": "boolean", "default": true},
        "position": {"enum": ["left", "right"], "default": "left"}
      }
    },
    "chartLegend": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean", "default": true},
        "position": {"enum": ["top", "bottom", "left", "right"], "default": "bottom"}
      }
    },
    "chartTooltip": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean", "default": true},
        "format": {"type": "string"}
      }
    }
  },
  "whk_validations": {
    "process_trend_chart": {
      "description": "Charts displaying process trends",
      "condition": "series data binding contains process tags",
      "requirements": {
        "time_range_appropriate": true,
        "axis_labels_with_units": true,
        "performance_optimized": true
      },
      "recommendations": {
        "max_data_points": 1000,
        "update_frequency": "≤ 1Hz",
        "time_window": "≤ 24h for real-time"
      }
    },
    "batch_process_chart": {
      "description": "Charts for batch process visualization",
      "condition": "data relates to batch operations",
      "required_features": {
        "batch_boundaries": true,
        "phase_annotations": true,
        "recipe_setpoints": true
      },
      "standard_series": [
        {"name": "Temperature", "units": "°F", "color": "#ff6b35"},
        {"name": "Pressure", "units": "PSI", "color": "#4dabf7"},
        {"name": "Flow Rate", "units": "GPM", "color": "#51cf66"}
      ]
    }
  }
}
```

## 🎛️ Container Component Schemas

### Flex Container Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.whk.local/perspective/flex-container.json",
  "title": "Perspective Flex Container",
  "description": "Flexible layout container with responsive capabilities",
  "allOf": [
    {"$ref": "base-component.json"},
    {
      "properties": {
        "type": {"const": "ia.container.flex"},
        "props": {
          "type": "object",
          "properties": {
            "direction": {
              "enum": ["row", "column", "row-reverse", "column-reverse"],
              "default": "row",
              "description": "Flex direction"
            },
            "justify": {
              "enum": ["flex-start", "flex-end", "center", "space-between", "space-around", "space-evenly"],
              "default": "flex-start",
              "description": "Justify content alignment"
            },
            "align": {
              "enum": ["flex-start", "flex-end", "center", "stretch", "baseline"],
              "default": "stretch",
              "description": "Align items"
            },
            "wrap": {
              "enum": ["nowrap", "wrap", "wrap-reverse"],
              "default": "nowrap",
              "description": "Flex wrap behavior"
            },
            "gap": {
              "type": "string",
              "pattern": "^\\d+(?:\\.\\d+)?(?:px|em|rem|%)$",
              "description": "Gap between flex items"
            },
            "style": {
              "$ref": "base-component.json#/definitions/styleObject"
            }
          },
          "additionalProperties": false
        }
      },
      "whk_validations": {
        "responsive_layout": {
          "description": "Responsive layouts for different screen sizes",
          "recommendations": {
            "use_relative_units": "Use em, rem, or % instead of px",
            "flexible_gaps": "Use relative gap values",
            "wrap_for_mobile": "Consider wrap for mobile layouts"
          }
        },
        "control_panel_layout": {
          "description": "Control panel layouts",
          "condition": "contains control components",
          "standard_patterns": {
            "button_group": {"direction": "row", "gap": "0.5rem", "justify": "center"},
            "form_layout": {"direction": "column", "gap": "1rem", "align": "stretch"},
            "toolbar": {"direction": "row", "justify": "space-between", "align": "center"}
          }
        }
      }
    }
  ]
}
```

## 🔧 Schema Validation Implementation

### Schema Loader and Validator

```python
# validation/schema_loader.py
import json
import jsonschema
from typing import Dict, List, Any, Optional
from pathlib import Path

class PerspectiveSchemaLoader:
    def __init__(self, schema_directory: str):
        self.schema_directory = Path(schema_directory)
        self.schemas = {}
        self.resolvers = {}
        self._load_all_schemas()
    
    def _load_all_schemas(self):
        """Load all schema files and create resolvers"""
        # Load base schema first
        base_schema_path = self.schema_directory / "base-component.json"
        with open(base_schema_path, 'r') as f:
            self.schemas['base-component'] = json.load(f)
        
        # Load component-specific schemas
        for schema_file in self.schema_directory.glob("*.json"):
            if schema_file.name == "base-component.json":
                continue
                
            with open(schema_file, 'r') as f:
                schema_name = schema_file.stem
                self.schemas[schema_name] = json.load(f)
        
        # Create resolver for schema references
        self._create_resolvers()
    
    def _create_resolvers(self):
        """Create JSON Schema resolvers for $ref resolution"""
        for schema_name, schema in self.schemas.items():
            store = {
                f"https://schemas.whk.local/perspective/{schema_name}.json": schema
            }
            
            # Add base schema to all resolvers
            store["https://schemas.whk.local/perspective/base-component.json"] = self.schemas['base-component']
            
            resolver = jsonschema.RefResolver.from_schema(schema, store=store)
            self.resolvers[schema_name] = resolver
    
    def get_schema_for_component(self, component_type: str) -> Optional[Dict]:
        """Get appropriate schema for component type"""
        type_mapping = {
            'ia.display.button': 'button',
            'ia.input.numeric-entry-field': 'numeric-entry',
            'ia.display.table': 'table',
            'ia.chart.timeseries': 'chart',
            'ia.container.flex': 'flex-container'
        }
        
        schema_name = type_mapping.get(component_type, 'base-component')
        return self.schemas.get(schema_name)
    
    def validate_component(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component against appropriate schema"""
        component_type = component.get('type', '')
        schema = self.get_schema_for_component(component_type)
        
        if not schema:
            return {
                'valid': False,
                'errors': [{'message': f'No schema found for component type: {component_type}'}],
                'warnings': [],
                'whk_violations': []
            }
        
        # Get resolver for this schema
        schema_name = self._get_schema_name_from_type(component_type)
        resolver = self.resolvers.get(schema_name)
        
        # Validate against JSON Schema
        result = self._validate_json_schema(component, schema, resolver)
        
        # Validate WHK-specific rules
        whk_violations = self._validate_whk_rules(component, schema)
        result['whk_violations'] = whk_violations
        
        return result
    
    def _validate_json_schema(self, component: Dict, schema: Dict, resolver: jsonschema.RefResolver) -> Dict:
        """Validate component against JSON schema"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            validator = jsonschema.Draft7Validator(schema, resolver=resolver)
            errors = list(validator.iter_errors(component))
            
            for error in errors:
                result['errors'].append({
                    'message': error.message,
                    'path': '.'.join(str(p) for p in error.absolute_path),
                    'schema_path': '.'.join(str(p) for p in error.schema_path),
                    'invalid_value': error.instance if hasattr(error, 'instance') else None
                })
            
            result['valid'] = len(result['errors']) == 0
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'message': f'Schema validation error: {str(e)}',
                'path': '',
                'schema_path': ''
            })
        
        return result
    
    def _validate_whk_rules(self, component: Dict, schema: Dict) -> List[Dict]:
        """Validate WHK-specific business rules"""
        violations = []
        whk_validations = schema.get('whk_validations', {})
        
        for rule_name, rule_config in whk_validations.items():
            if self._rule_applies(component, rule_config):
                violation = self._check_whk_rule(component, rule_name, rule_config)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _rule_applies(self, component: Dict, rule_config: Dict) -> bool:
        """Check if WHK rule applies to component"""
        condition = rule_config.get('condition', '')
        
        # Simple condition evaluation - in production would use proper parser
        if 'tag write to Equipment' in condition:
            script = component.get('events', {}).get('onActionPerformed', {}).get('config', {}).get('script', '')
            return 'system.tag.write' in script and ('Equipment' in script or 'Process' in script)
        
        if 'Emergency' in condition:
            text = component.get('props', {}).get('text', '')
            return any(word in text for word in ['Emergency', 'E-Stop', 'STOP'])
        
        if 'batch' in condition:
            # Check for batch-related content
            return self._contains_batch_content(component)
        
        return False
    
    def _check_whk_rule(self, component: Dict, rule_name: str, rule_config: Dict) -> Optional[Dict]:
        """Check specific WHK rule"""
        schema_extension = rule_config.get('schema_extension', {})
        
        if not schema_extension:
            return None
        
        # Validate against extended schema requirements
        try:
            extended_validator = jsonschema.Draft7Validator(schema_extension)
            errors = list(extended_validator.iter_errors(component))
            
            if errors:
                return {
                    'rule': rule_name,
                    'description': rule_config.get('description', ''),
                    'violations': [error.message for error in errors],
                    'requirements': rule_config.get('requirements', {}),
                    'severity': 'error'
                }
        except Exception as e:
            return {
                'rule': rule_name,
                'description': f'Rule validation error: {str(e)}',
                'violations': [],
                'severity': 'warning'
            }
        
        return None
```

This comprehensive schema system provides strict validation for all Perspective components while incorporating production-learned patterns and WHK-specific requirements for whiskey house operations.