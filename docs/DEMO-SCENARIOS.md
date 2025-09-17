# Demo Scenarios - AI Context Engineering for Ignition

## Overview

This document provides comprehensive demo scenarios to showcase the AI Context Engineering system's capabilities for Ignition development. Each scenario includes setup instructions, execution steps, expected outcomes, and validation criteria.

## Demo Environment Setup

### Prerequisites

```bash
# Ensure all services are running
docker-compose up -d

# Verify service health
./scripts/health_check.sh

# Load demo data
./scripts/load_demo_data.sh
```

### Demo Data Sources

- **WHK-Global Project**: Production SCADA interface components
- **Reporting Project**: Dashboard and chart implementations
- **Community Examples**: Ignition Exchange patterns
- **Documentation Corpus**: Official Ignition documentation indexed

## Scenario 1: Context-Aware Perspective Component Generation

### Objective
Demonstrate how the AI system generates proper Perspective components with production-quality patterns and WHK-specific standards.

### Setup
```bash
# Ensure production code is indexed
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_path": "/demo/whk-global", "source_type": "ignition_project"}'

# Verify indexing completed
curl http://localhost:8001/stats
```

### Demo Steps

#### Step 1: Basic Button Component Request

**Prompt**: "Create a Perspective button component for starting a pump with proper tag binding"

**Expected AI Response**:
```json
{
  "type": "ia.display.button",
  "meta": {
    "name": "PumpStartButton"
  },
  "props": {
    "text": "Start Pump",
    "style": {
      "backgroundColor": "#28a745",
      "color": "white",
      "fontSize": "16px"
    }
  },
  "events": {
    "onActionPerformed": {
      "config": {
        "script": "system.tag.writeBlocking(['[default]Equipment/Pump_01/Start'], [True])"
      }
    }
  },
  "custom": {
    "tagBinding": "[default]Equipment/Pump_01/Start",
    "whkStandard": "pump_control_v2"
  }
}
```

**Validation**:
- ✅ Uses proper WHK color scheme (green for start actions)
- ✅ Follows WHK tag naming convention
- ✅ Includes proper event handling
- ✅ Uses `writeBlocking` for critical operations

#### Step 2: Complex Multi-Component Interface

**Prompt**: "Create a pump control panel with start/stop buttons, status indicator, and flow rate display following WHK standards"

**Expected AI Response**: Complete JSON structure with:
- Button group for start/stop
- LED indicator for status
- Numeric display for flow rate
- Proper tag bindings for all components
- WHK-specific styling and naming

**Live Validation**:
```bash
# Validate generated component through MCP tools
curl -X POST http://localhost:3333/validate/perspective \
  -H "Content-Type: application/json" \
  -d @generated_component.json
```

### Success Criteria
- Components follow WHK design standards
- Tag paths match production naming conventions
- Event handlers use proper Ignition syntax
- MCP validation returns no errors
- Rules engine confirms best practices compliance

## Scenario 2: Jython Scripting with Production Context

### Objective
Show how the AI generates Jython scripts that follow production patterns and handle real-world requirements.

### Demo Steps

#### Step 1: Gateway Event Script

**Prompt**: "Create a gateway timer script that checks pump status every 5 minutes and logs anomalies using WHK logging standards"

**Expected AI Response**:
```python
# Gateway Timer Script - Pump Status Monitor
# Schedule: Fixed Rate, 300000ms (5 minutes)

import system
from com.inductiveautomation.ignition.common.util import LoggerEx

# Initialize WHK standard logger
logger = LoggerEx.newBuilder().name("WHK.PumpMonitor").build()

def checkPumpStatus():
    """
    Monitor pump operational status and log anomalies.
    Follows WHK logging and alerting standards.
    """
    try:
        # Read pump status tags
        pump_tags = [
            "[default]Equipment/Pump_01/Running",
            "[default]Equipment/Pump_01/FlowRate",
            "[default]Equipment/Pump_01/Pressure",
            "[default]Equipment/Pump_01/Temperature"
        ]
        
        values = system.tag.readBlocking(pump_tags)
        
        if values is None or len(values) != len(pump_tags):
            logger.error("Failed to read pump status tags")
            return
            
        running, flow_rate, pressure, temperature = [v.value for v in values]
        
        # Check for anomalies using WHK thresholds
        anomalies = []
        
        if running and flow_rate < 10.0:
            anomalies.append("Low flow rate: {} GPM".format(flow_rate))
            
        if running and pressure < 30.0:
            anomalies.append("Low pressure: {} PSI".format(pressure))
            
        if temperature > 180.0:
            anomalies.append("High temperature: {} °F".format(temperature))
            
        # Log anomalies with WHK format
        if anomalies:
            alert_msg = "Pump anomalies detected: {}".format(", ".join(anomalies))
            logger.warn(alert_msg)
            
            # Write to alert tag for operator notification
            system.tag.writeBlocking(
                ["[default]Alerts/Pump_01/Anomaly"], 
                [True]
            )
            
            # Store anomaly details
            system.tag.writeBlocking(
                ["[default]Alerts/Pump_01/Details"], 
                [alert_msg]
            )
        else:
            # Clear anomaly flags if no issues
            system.tag.writeBlocking(
                ["[default]Alerts/Pump_01/Anomaly", "[default]Alerts/Pump_01/Details"], 
                [False, ""]
            )
            
    except Exception as e:
        logger.error("Error in pump status check: {}".format(str(e)))

# Execute the check
checkPumpStatus()
```

**Live Validation**:
```bash
# Analyze script through MCP tools
curl -X POST http://localhost:3333/analyze/jython \
  -H "Content-Type: application/json" \
  -d '{"script": "..."}'
```

#### Step 2: Vision Window Script

**Prompt**: "Create a Vision window script for a batch recipe selection dialog with database integration"

**Expected AI Response**: Production-quality script with:
- Proper error handling
- Database connection management
- User permission validation
- Transaction safety
- WHK audit logging

### Success Criteria
- Scripts follow WHK coding standards
- Proper error handling and logging
- Database operations use transactions
- Security best practices implemented
- Performance considerations addressed

## Scenario 3: Real-Time Development Assistance

### Objective
Demonstrate live development assistance with context-aware suggestions and validation.

### Demo Steps

#### Step 1: Live Code Completion

**Setup**: Open development environment with AI assistant

**User Action**: Start typing in script editor
```python
system.tag.write
```

**Expected AI Suggestion**:
```python
system.tag.writeBlocking(
    ["[default]Equipment/Tank_01/SetPoint"], 
    [event.source.value]
)
```

**Context Source**: Production patterns showing preference for `writeBlocking` over `write` for critical operations

#### Step 2: Error Detection and Correction

**User Code** (with intentional error):
```python
system.tag.read("[default]Process/Value")
```

**AI Response**:
```
⚠️ Potential Issue Detected:
- Using 'read' instead of 'readBlocking' may cause timing issues
- Consider error handling for tag read operations

Suggested correction:
value = system.tag.readBlocking(["[default]Process/Value"])
if value and value[0].quality.isGood():
    result = value[0].value
else:
    logger.error("Failed to read tag: [default]Process/Value")
```

#### Step 3: Component Property Assistance

**User Action**: Adding binding to Perspective component

**AI Suggestion**:
```json
{
  "binding": {
    "type": "tag",
    "config": {
      "path": "[default]Equipment/Pump_01/Status",
      "deadband": 0.1,
      "polling": "subscribe"
    }
  }
}
```

**Context**: Production examples showing WHK deadband and polling preferences

### Success Criteria
- Suggestions match production patterns
- Context-aware recommendations
- Real-time error detection
- Performance optimization suggestions

## Scenario 4: Production Code Learning Demo

### Objective
Show how the system learns from production changes and incorporates new patterns.

### Demo Steps

#### Step 1: Production Code Analysis

**Action**: Simulate new production deployment

```bash
# Add new production code
cp demo/new_production_patterns/* /production/whk-global/

# Trigger analysis
curl -X POST http://localhost:8001/analyze_changes \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/production/whk-global"}'
```

**Expected Output**:
```json
{
  "changes_detected": 15,
  "new_patterns": [
    {
      "type": "perspective_component",
      "pattern": "multi_state_indicator_v3",
      "confidence": 0.95,
      "usage_count": 8
    },
    {
      "type": "jython_function",
      "pattern": "batch_recipe_validator",
      "confidence": 0.88,
      "usage_count": 3
    }
  ],
  "updated_embeddings": 127
}
```

#### Step 2: Updated AI Responses

**Test Prompt**: "Create a multi-state indicator for pump status"

**AI Response** (now includes new v3 pattern):
```json
{
  "type": "ia.display.multistateIndicator",
  "meta": {
    "name": "PumpStatusIndicator_v3"
  },
  "props": {
    "states": [
      {
        "value": 0,
        "label": "Stopped",
        "style": {"backgroundColor": "#dc3545"}
      },
      {
        "value": 1,
        "label": "Starting",
        "style": {"backgroundColor": "#ffc107"}
      },
      {
        "value": 2,
        "label": "Running",
        "style": {"backgroundColor": "#28a745"}
      },
      {
        "value": 3,
        "label": "Fault",
        "style": {"backgroundColor": "#fd7e14", "animation": "blink"}
      }
    ]
  },
  "custom": {
    "whkVersion": "v3",
    "features": ["fault_animation", "auto_clear"]
  }
}
```

### Success Criteria
- System detects production changes
- New patterns automatically indexed
- AI responses incorporate latest patterns
- Performance metrics show improvement

## Scenario 5: Multi-Project Context Demo

### Objective
Demonstrate how the system handles context from multiple projects and suggests appropriate patterns.

### Demo Steps

#### Step 1: Project-Specific Patterns

**Context Setup**: Multiple projects indexed
- WHK-Global: Main SCADA interface
- Reporting: Dashboard and analytics
- Batch: Recipe management system

**Prompt**: "Create a recipe selector component"

**AI Analysis**:
1. Identifies "recipe" context relates to Batch project
2. Retrieves Batch project patterns
3. Suggests component following Batch project conventions

**Expected Response**: Recipe selector with batch-specific styling and data sources

#### Step 2: Cross-Project Pattern Synthesis

**Prompt**: "Create a dashboard showing pump data with drill-down capability"

**AI Analysis**:
1. Pump data context → WHK-Global patterns
2. Dashboard context → Reporting patterns  
3. Drill-down context → Combined approach

**Expected Response**: Dashboard component combining:
- WHK-Global pump data bindings
- Reporting project chart styles
- Navigation patterns from both projects

### Success Criteria
- Appropriate project context selection
- Cross-project pattern synthesis
- Consistent styling within project domains
- Proper data source integration

## Scenario 6: Performance and Optimization Demo

### Objective
Show how the system suggests performance optimizations based on production learnings.

### Demo Steps

#### Step 1: Query Optimization Suggestions

**User Code**:
```python
for tag in pump_tags:
    value = system.tag.readBlocking([tag])
    process_value(value[0].value)
```

**AI Suggestion**:
```python
# Optimized batch read approach (learned from production)
values = system.tag.readBlocking(pump_tags)
for i, value in enumerate(values):
    if value.quality.isGood():
        process_value(value.value)
    else:
        logger.warn("Poor quality reading for tag: {}".format(pump_tags[i]))
```

**Context**: Production code analysis showing batch reads perform 10x better

#### Step 2: Memory Usage Optimization

**AI Detection**: Large dataset binding in Perspective table

**AI Suggestion**:
```json
{
  "recommendation": "pagination",
  "reason": "Dataset exceeds 1000 rows - production analysis shows performance degradation",
  "solution": {
    "paging": {
      "enabled": true,
      "pageSize": 50
    },
    "virtualScrolling": true
  }
}
```

### Success Criteria
- Performance issues automatically detected
- Optimization suggestions based on production data
- Quantified performance improvements
- Memory and CPU usage considerations

## Demo Validation and Metrics

### Real-Time Validation

```bash
# Service health during demo
curl http://localhost:8001/health
curl http://localhost:3333/health
curl http://localhost:8002/health

# Performance metrics
curl http://localhost:8001/metrics | grep response_time
curl http://localhost:3333/metrics | grep validation_success_rate
```

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Context Retrieval Speed | <200ms | API response time |
| Validation Accuracy | >95% | MCP tool validation rate |
| Pattern Recognition | >90% | Production pattern matching |
| Code Quality Score | >8.5/10 | Rules engine assessment |

### Demo Environment Monitoring

```bash
# Monitor resource usage during demo
docker stats

# Check vector database performance
docker exec ai-context-db psql -U postgres -c "
SELECT 
  schemaname,
  tablename,
  n_tup_ins as inserts,
  n_tup_upd as updates,
  n_tup_del as deletes
FROM pg_stat_user_tables 
WHERE tablename = 'embeddings';"
```

## Troubleshooting Demo Issues

### Common Demo Problems

#### 1. Slow Context Retrieval

**Symptoms**: AI responses taking >5 seconds
**Solution**:
```bash
# Check vector index
docker exec ai-context-db psql -U postgres -c "REINDEX TABLE embeddings;"

# Restart RAG service
docker-compose restart rag-service
```

#### 2. MCP Tool Validation Failures

**Symptoms**: False positive validation errors
**Solution**:
```bash
# Update MCP tool rules
curl -X POST http://localhost:3333/reload_rules

# Check tool configuration
curl http://localhost:3333/config/status
```

#### 3. Missing Production Context

**Symptoms**: AI suggestions don't match production patterns
**Solution**:
```bash
# Force re-index production code
curl -X POST http://localhost:8001/reindex \
  -d '{"force": true, "source": "production"}'
```

## Demo Customization

### Custom Demo Data

```bash
# Add specific demo scenarios
cp custom_scenarios/* /demo/data/

# Re-index with custom data
./scripts/index_demo_data.sh
```

### Demo Configuration

```yaml
# demo_config.yml
demo:
  mode: presentation
  response_delay: 1000  # Add dramatic pause
  verbose_explanations: true
  show_context_sources: true
  
scenarios:
  - name: "Basic Component Generation"
    enabled: true
    complexity: "beginner"
  - name: "Production Integration"
    enabled: true
    complexity: "advanced"
```

## Presentation Tips

### 1. Pre-Demo Checklist

- [ ] All services running and healthy
- [ ] Demo data loaded and indexed
- [ ] Network connectivity verified
- [ ] Backup demo environment ready
- [ ] Presentation slides synchronized

### 2. Demo Flow Recommendations

1. **Start Simple**: Basic component generation
2. **Add Complexity**: Multi-component interfaces
3. **Show Intelligence**: Context-aware suggestions
4. **Demonstrate Learning**: Production pattern adaptation
5. **Highlight Performance**: Optimization suggestions

### 3. Audience Engagement

- Show real production code examples
- Explain WHK-specific patterns
- Demonstrate time savings
- Highlight quality improvements
- Invite questions throughout

### 4. Recovery Strategies

- Have pre-generated responses ready
- Use recorded demos for critical sections
- Prepare simplified examples as backup
- Keep troubleshooting commands handy

## Conclusion

These demo scenarios provide comprehensive coverage of the AI Context Engineering system's capabilities. Each scenario builds upon the previous one, creating a compelling narrative of how AI can transform Ignition development workflows.

The demos emphasize:
- **Production-Quality Output**: All generated code follows real production patterns
- **Context Awareness**: AI understands project-specific requirements
- **Continuous Learning**: System improves with production feedback
- **Performance Focus**: Optimizations based on real-world learnings
- **Developer Experience**: Seamless integration with existing workflows

Use these scenarios to showcase the system's value proposition and demonstrate measurable improvements in development efficiency and code quality.