# Enhanced AI Rules Engine with Ignition-Specific Patterns

## Overview

This document extends the AI Rules Engine with comprehensive Ignition-specific patterns, advanced validation logic, and production-learned best practices. The enhanced engine focuses on deep Ignition knowledge, including component-specific validations, context-aware scripting patterns, and real-world production scenarios from the whiskey house operations.

## 🎯 Enhanced Objectives

### Advanced Goals
- **Deep Ignition Knowledge**: Comprehensive understanding of all Ignition components and their optimal usage patterns
- **Context-Aware Validation**: Different validation rules based on execution context (Gateway, Client, Perspective, Designer)
- **Industry-Specific Patterns**: Whiskey production, batch operations, and FDA compliance patterns
- **Performance Intelligence**: Rules based on actual performance data from production systems
- **Security-First Approach**: Built-in security validation for all industrial automation contexts

### Production Learning Integration
- **Pattern Recognition**: Automatic detection of successful patterns from production codebases
- **Anti-Pattern Detection**: Identification and prevention of problematic code patterns
- **Continuous Adaptation**: Rules that evolve based on production feedback and performance metrics
- **Context Switching**: Intelligent rule application based on development context

## 🧠 Enhanced Rule Categories

### 1. Component-Specific Perspective Rules

#### Button Component Advanced Rules

```yaml
# rules/enhanced-perspective-rules.yaml
perspective_enhanced_rules:
  button_component_advanced:
    - rule_id: "BTN-ADV-001"
      name: "Control Button Security Validation"
      description: "Production control buttons must have role-based security and confirmation dialogs"
      severity: "error"
      component_type: "ia.display.button"
      conditions:
        - affects_production_process: true
        - controls_equipment: true
      required_properties:
        - "meta.security.roleAccess"
        - "props.confirm"
      validation_logic: |
        # Check if button affects production
        if (component.events?.onActionPerformed?.config?.script?.includes('tag.write')) {
          const script = component.events.onActionPerformed.config.script;
          const productionTags = script.match(/\[default\](Equipment|Process|Control)/g);
          
          if (productionTags && productionTags.length > 0) {
            return {
              requires_security: true,
              requires_confirmation: script.includes('Start') || script.includes('Stop') || script.includes('Enable'),
              production_impact: 'high'
            };
          }
        }
        return { production_impact: 'low' };
      message: "Production control buttons require security roles and user confirmation"
      suggested_fix: |
        Add security configuration:
        "meta": {
          "security": {
            "roleAccess": ["Operators", "Engineers"]
          }
        },
        "props": {
          "confirm": true,
          "confirmMessage": "Are you sure you want to start this process?"
        }
      examples:
        correct: |
          {
            "type": "ia.display.button",
            "meta": {
              "security": {"roleAccess": ["Operators"]}
            },
            "props": {
              "text": "Start Pump",
              "confirm": true,
              "confirmMessage": "Start pump P-101?"
            }
          }
        
    - rule_id: "BTN-ADV-002"
      name: "WHK Process Button Patterns"
      description: "Buttons for whiskey production processes should follow established patterns"
      severity: "warning"
      component_type: "ia.display.button"
      context: ["whk-global", "distillation", "fermentation"]
      patterns:
        start_process:
          text_pattern: "^Start .+"
          color_scheme: "#28a745"  # Success green
          required_confirmation: true
          audit_logging: true
        stop_process:
          text_pattern: "^Stop .+"
          color_scheme: "#dc3545"  # Danger red
          required_confirmation: true
          emergency_stop: false
        emergency_stop:
          text_pattern: ".*(Emergency|E-Stop|STOP).*"
          color_scheme: "#ff6b35"  # Emergency orange
          size: "large"
          required_confirmation: false
          immediate_action: true
      validation_logic: |
        const text = component.props?.text || '';
        const isStartButton = /^Start /i.test(text);
        const isStopButton = /^Stop /i.test(text);
        const isEmergencyStop = /(Emergency|E-Stop|STOP)/i.test(text);
        
        if (isStartButton || isStopButton || isEmergencyStop) {
          return {
            pattern_detected: true,
            button_type: isEmergencyStop ? 'emergency_stop' : (isStartButton ? 'start_process' : 'stop_process'),
            follows_whk_standards: this.validateWHKButtonStandards(component, text)
          };
        }
        return { pattern_detected: false };
        
  numeric_entry_advanced:
    - rule_id: "NUM-ADV-001"
      name: "Recipe Parameter Validation"
      description: "Recipe parameters must have proper validation ranges and units"
      severity: "error"
      component_type: "ia.input.numeric-entry-field"
      context: ["batch_operations", "recipe_management"]
      conditions:
        - field_purpose: "recipe_parameter"
        - affects_product_quality: true
      required_properties:
        - "props.minValue"
        - "props.maxValue" 
        - "props.format"
        - "custom.engineeringUnits"
        - "custom.validationRules"
      validation_ranges:
        temperature:
          min: 32    # °F
          max: 220   # °F
          format: "0.0"
          units: "°F"
        pressure:
          min: 0     # PSI
          max: 150   # PSI
          format: "0.0"
          units: "PSI"
        flow_rate:
          min: 0     # GPM
          max: 500   # GPM
          format: "0.00"
          units: "GPM"
        time:
          min: 0     # minutes
          max: 1440  # 24 hours
          format: "0"
          units: "min"
      message: "Recipe parameters require validation ranges and engineering units"
      
    - rule_id: "NUM-ADV-002"
      name: "Critical Setpoint Protection"
      description: "Critical process setpoints require additional protection"
      severity: "error"
      component_type: "ia.input.numeric-entry-field"
      conditions:
        - binds_to_tag_pattern: ".*[Ss]etpoint.*"
        - process_critical: true
      required_features:
        - confirmation_dialog: true
        - value_history: true
        - change_logging: true
        - range_validation: true
      protection_levels:
        level_1: # Normal operation
          - confirmation: false
          - logging: true
        level_2: # Critical parameters
          - confirmation: true
          - logging: true
          - supervisor_approval: false
        level_3: # Safety critical
          - confirmation: true
          - logging: true
          - supervisor_approval: true
          - dual_authorization: true
```

#### Table Component Production Patterns

```yaml
  table_component_advanced:
    - rule_id: "TBL-ADV-001"
      name: "Batch History Table Configuration"
      description: "Batch history tables should follow WHK standards for data presentation"
      severity: "warning"
      component_type: "ia.display.table"
      context: ["batch_operations", "quality_control"]
      standard_columns:
        - field: "batch_id"
          header: "Batch ID"
          width: 120
          sortable: true
          filterable: true
        - field: "start_time"
          header: "Start Time"
          width: 150
          format: "MM/dd/yyyy HH:mm"
        - field: "end_time"
          header: "End Time" 
          width: 150
          format: "MM/dd/yyyy HH:mm"
        - field: "status"
          header: "Status"
          width: 100
          cell_renderer: "status_indicator"
        - field: "operator"
          header: "Operator"
          width: 120
        - field: "recipe_name"
          header: "Recipe"
          width: 150
      performance_settings:
        pagination_enabled: true
        page_size: 50
        virtual_scrolling: true
        max_rows_without_pagination: 100
      validation_logic: |
        if (component.props?.data?.binding?.config?.path?.includes('batch')) {
          const columns = component.props?.columns || [];
          const hasRequiredColumns = this.validateBatchTableColumns(columns);
          const hasPerformanceOptimization = this.validateTablePerformance(component);
          
          return {
            is_batch_table: true,
            has_required_columns: hasRequiredColumns,
            performance_optimized: hasPerformanceOptimization
          };
        }
        return { is_batch_table: false };
        
    - rule_id: "TBL-ADV-002"
      name: "Real-time Data Table Optimization"
      description: "Tables displaying real-time process data should be optimized for performance"
      severity: "warning"
      component_type: "ia.display.table"
      conditions:
        - data_update_frequency: "> 1Hz"
        - row_count: "> 50"
      optimization_requirements:
        - virtual_scrolling: true
        - update_throttling: "500ms"
        - selective_column_updates: true
        - row_recycling: true
      message: "Real-time tables require performance optimizations to prevent UI lag"
```

### 2. Advanced Jython Scripting Patterns

#### Production-Specific Script Patterns

```yaml
# rules/enhanced-jython-rules.yaml
jython_enhanced_rules:
  batch_operations:
    - rule_id: "BATCH-SCR-001"
      name: "Batch State Transition Validation"
      description: "Batch state changes must follow proper validation and logging"
      severity: "error"
      script_context: ["gateway_timer", "button_event", "tag_change"]
      applies_to_functions: ["changeBatchState", "startBatch", "completeBatch"]
      required_patterns:
        - validation_before_change: true
        - state_transition_logging: true
        - error_rollback: true
        - notification_system: true
      code_template: |
        def changeBatchState(batchId, newState, operator):
            """
            Change batch state with proper validation and logging.
            
            Args:
                batchId (str): Batch identifier
                newState (str): Target state
                operator (str): Operator making the change
            """
            logger = system.util.getLogger("BatchOperations")
            
            try:
                # Validate state transition
                currentState = system.tag.readBlocking(['[default]Batches/{}/State'.format(batchId)])[0].value
                
                if not isValidTransition(currentState, newState):
                    logger.error("Invalid state transition: {} -> {} for batch {}".format(
                        currentState, newState, batchId))
                    return False
                
                # Perform state change
                tagPaths = [
                    '[default]Batches/{}/State'.format(batchId),
                    '[default]Batches/{}/StateChangeTime'.format(batchId),
                    '[default]Batches/{}/StateChangeOperator'.format(batchId)
                ]
                
                values = [newState, system.date.now(), operator]
                
                success = system.tag.writeBlocking(tagPaths, values)
                
                if success:
                    # Log to batch historian
                    logBatchEvent(batchId, "StateChange", {
                        'from_state': currentState,
                        'to_state': newState,
                        'operator': operator,
                        'timestamp': system.date.now()
                    })
                    
                    # Send notifications
                    notifyStateChange(batchId, newState, operator)
                    
                    logger.info("Batch {} state changed from {} to {} by {}".format(
                        batchId, currentState, newState, operator))
                    return True
                else:
                    logger.error("Failed to write batch state tags for batch {}".format(batchId))
                    return False
                    
            except Exception as e:
                logger.error("Error changing batch state: {}".format(str(e)))
                return False
                
    - rule_id: "BATCH-SCR-002"
      name: "Recipe Parameter Validation"
      description: "Recipe parameter changes require validation against acceptable ranges"
      severity: "error"
      script_context: ["perspective_event", "gateway_script"]
      pattern_detection: |
        # Detect recipe parameter modification scripts
        if ('recipe' in script.lower() and 
            ('setpoint' in script.lower() or 'parameter' in script.lower()) and
            'system.tag.write' in script):
          return True
        return False
      required_validations:
        - range_checking: true
        - unit_validation: true
        - change_authorization: true
        - audit_logging: true
      validation_template: |
        def validateRecipeParameter(parameterName, newValue, recipeId, operator):
            """
            Validate recipe parameter change against acceptable ranges.
            """
            logger = system.util.getLogger("RecipeValidation")
            
            try:
                # Get parameter specifications
                paramSpec = getParameterSpecs(recipeId, parameterName)
                
                if not paramSpec:
                    logger.error("No specification found for parameter: {}".format(parameterName))
                    return False, "Parameter specification not found"
                
                # Validate range
                if newValue < paramSpec['minValue'] or newValue > paramSpec['maxValue']:
                    logger.warning("Parameter {} value {} outside acceptable range [{}, {}]".format(
                        parameterName, newValue, paramSpec['minValue'], paramSpec['maxValue']))
                    return False, "Value outside acceptable range"
                
                # Check authorization level
                if paramSpec['criticalLevel'] > 1:
                    if not hasAuthorization(operator, paramSpec['criticalLevel']):
                        logger.warning("Operator {} lacks authorization for critical parameter {}".format(
                            operator, parameterName))
                        return False, "Insufficient authorization"
                
                # Log parameter change
                logParameterChange(recipeId, parameterName, newValue, operator)
                
                return True, "Validation passed"
                
            except Exception as e:
                logger.error("Parameter validation error: {}".format(str(e)))
                return False, "Validation error"
                
  equipment_control:
    - rule_id: "EQUIP-SCR-001"
      name: "Equipment Interlock Validation"
      description: "Equipment control scripts must check safety interlocks"
      severity: "error"
      script_context: ["button_event", "gateway_timer"]
      equipment_types: ["pumps", "valves", "motors", "heaters"]
      required_interlock_checks:
        - safety_systems: true
        - equipment_ready: true
        - process_conditions: true
        - operator_permissions: true
      interlock_template: |
        def startEquipment(equipmentId, operator):
            """
            Start equipment with proper interlock checking.
            
            Args:
                equipmentId (str): Equipment identifier (e.g., 'PMP-101')
                operator (str): Operator starting equipment
            """
            logger = system.util.getLogger("EquipmentControl")
            
            try:
                # Check safety interlocks
                interlockStatus = checkSafetyInterlocks(equipmentId)
                
                if not interlockStatus['safe']:
                    logger.error("Safety interlock violation for {}: {}".format(
                        equipmentId, interlockStatus['violation']))
                    
                    # Trigger alarm
                    system.tag.writeBlocking([
                        '[default]Alarms/{}/InterlockViolation'.format(equipmentId)
                    ], [True])
                    
                    return False, interlockStatus['violation']
                
                # Check equipment ready status
                equipmentReady = system.tag.readBlocking([
                    '[default]Equipment/{}/Ready'.format(equipmentId),
                    '[default]Equipment/{}/Fault'.format(equipmentId),
                    '[default]Equipment/{}/MaintenanceMode'.format(equipmentId)
                ])
                
                if not equipmentReady[0].value:
                    return False, "Equipment not ready"
                    
                if equipmentReady[1].value:
                    return False, "Equipment in fault state"
                    
                if equipmentReady[2].value:
                    return False, "Equipment in maintenance mode"
                
                # Check operator permissions
                if not hasEquipmentPermission(operator, equipmentId):
                    logger.warning("Operator {} lacks permission for equipment {}".format(
                        operator, equipmentId))
                    return False, "Insufficient permissions"
                
                # Start equipment
                success = system.tag.writeBlocking([
                    '[default]Equipment/{}/Start'.format(equipmentId),
                    '[default]Equipment/{}/StartOperator'.format(equipmentId),
                    '[default]Equipment/{}/StartTime'.format(equipmentId)
                ], [True, operator, system.date.now()])
                
                if success:
                    logger.info("Equipment {} started by {}".format(equipmentId, operator))
                    
                    # Log to equipment historian
                    logEquipmentEvent(equipmentId, "Start", operator)
                    
                    return True, "Equipment started successfully"
                else:
                    logger.error("Failed to start equipment {}".format(equipmentId))
                    return False, "Failed to write start command"
                    
            except Exception as e:
                logger.error("Equipment start error: {}".format(str(e)))
                return False, "Equipment start error"

  database_operations:
    - rule_id: "DB-SCR-001"
      name: "Transactional Database Operations"
      description: "Database operations affecting batch records must be transactional"
      severity: "error"
      script_context: ["gateway_script", "perspective_event"]
      applies_to_operations: ["INSERT", "UPDATE", "DELETE"]
      tables: ["batch_records", "recipe_data", "quality_results", "equipment_logs"]
      required_patterns:
        - transaction_management: true
        - error_rollback: true
        - audit_logging: true
        - connection_handling: true
      transaction_template: |
        def updateBatchRecord(batchId, updateData, operator):
            """
            Update batch record with transactional safety.
            
            Args:
                batchId (str): Batch identifier
                updateData (dict): Data to update
                operator (str): Operator making update
            """
            logger = system.util.getLogger("DatabaseOperations")
            db = "production_db"
            
            try:
                # Begin transaction
                system.db.beginTransaction(db)
                
                # Update batch record
                updateQuery = """
                    UPDATE batch_records 
                    SET temperature = ?, pressure = ?, updated_by = ?, updated_at = NOW()
                    WHERE batch_id = ?
                """
                
                updateParams = [
                    updateData.get('temperature'),
                    updateData.get('pressure'),
                    operator,
                    batchId
                ]
                
                updateResult = system.db.runPrepUpdate(updateQuery, updateParams, db)
                
                if updateResult == 0:
                    raise Exception("No batch record found for batch ID: {}".format(batchId))
                
                # Log the change
                auditQuery = """
                    INSERT INTO batch_audit_log (batch_id, change_type, changed_by, change_time, old_values, new_values)
                    VALUES (?, ?, ?, NOW(), ?, ?)
                """
                
                # Get old values for audit
                oldValues = getBatchCurrentValues(batchId)
                
                auditParams = [
                    batchId,
                    'update',
                    operator,
                    system.util.jsonEncode(oldValues),
                    system.util.jsonEncode(updateData)
                ]
                
                system.db.runPrepUpdate(auditQuery, auditParams, db)
                
                # Commit transaction
                system.db.commitTransaction(db)
                
                logger.info("Batch record updated for batch {} by {}".format(batchId, operator))
                return True, "Update successful"
                
            except Exception as e:
                # Rollback on any error
                try:
                    system.db.rollbackTransaction(db)
                except:
                    pass
                    
                logger.error("Failed to update batch record: {}".format(str(e)))
                return False, str(e)
```

### 3. Context-Aware Rule Application

#### Execution Context Rules

```yaml
context_aware_rules:
  gateway_context:
    available_functions:
      - "system.tag.*"
      - "system.db.*"
      - "system.util.*"
      - "system.date.*"
      - "system.security.*"
    restrictions:
      - no_gui_functions: true
      - no_client_scope: true
    performance_considerations:
      - max_execution_time: "30s"
      - memory_limit: "256MB"
      - avoid_blocking_operations: true
      
  perspective_context:
    available_functions:
      - "system.perspective.*"
      - "system.tag.read*"
      - "system.util.*"
      - "system.date.*"
    restrictions:
      - no_tag_writes_in_transforms: true
      - no_long_running_operations: true
    performance_considerations:
      - max_execution_time: "1s"
      - avoid_complex_calculations: true
      - prefer_bindings_over_scripts: true
      
  client_context:
    available_functions:
      - "system.gui.*"
      - "system.tag.*"
      - "system.util.*"
      - "system.nav.*"
    restrictions:
      - limited_database_access: true
      - no_gateway_functions: true
    performance_considerations:
      - max_execution_time: "5s"
      - minimize_network_calls: true
```

### 4. Performance Intelligence Rules

#### Performance Pattern Detection

```yaml
performance_intelligence:
  tag_operation_patterns:
    - rule_id: "PERF-TAG-001"
      name: "Batch Tag Operations"
      description: "Detect opportunities for batching tag operations"
      pattern_detection: |
        # Detect multiple individual tag reads/writes
        tag_operations = []
        for line in script_lines:
          if 'system.tag.read(' in line or 'system.tag.write(' in line:
            tag_operations.append(line)
        
        if len(tag_operations) > 3:
          return {
            'optimization_opportunity': True,
            'current_operations': len(tag_operations),
            'estimated_improvement': '70% faster execution'
          }
        return {'optimization_opportunity': False}
      optimization_template: |
        # Instead of multiple individual operations:
        # value1 = system.tag.read('[default]Tag1')
        # value2 = system.tag.read('[default]Tag2')
        # value3 = system.tag.read('[default]Tag3')
        
        # Use batch operation:
        tagPaths = ['[default]Tag1', '[default]Tag2', '[default]Tag3']
        values = system.tag.readBlocking(tagPaths)
        
        for i, value in enumerate(values):
          if value.quality.isGood():
            # Process value.value
            pass
            
    - rule_id: "PERF-DB-001"
      name: "Database Query Optimization"
      description: "Detect suboptimal database query patterns"
      pattern_detection: |
        # Detect queries in loops
        query_in_loop = False
        loop_depth = 0
        
        for line in script_lines:
          if 'for ' in line or 'while ' in line:
            loop_depth += 1
          elif 'system.db.run' in line and loop_depth > 0:
            query_in_loop = True
            
        return {'query_in_loop': query_in_loop, 'optimization_needed': query_in_loop}
      optimization_advice: |
        # Avoid running queries inside loops
        # Instead of:
        for batchId in batchList:
          result = system.db.runQuery("SELECT * FROM batches WHERE id = ?", [batchId])
        
        # Use batch query:
        batchIds = "','".join(batchList)
        results = system.db.runQuery("SELECT * FROM batches WHERE id IN ('{}')".format(batchIds))
        
  binding_optimization:
    - rule_id: "PERF-BIND-001"
      name: "Expression Binding Complexity"
      description: "Detect overly complex expression bindings"
      severity: "warning"
      complexity_threshold: 100  # characters
      optimization_suggestions:
        - use_transform_script: "complexity > 100"
        - split_into_multiple_bindings: "multiple_operations"
        - cache_intermediate_values: "repeated_calculations"
```

### 5. Security-First Industrial Automation Rules

#### Security Validation Patterns

```yaml
security_industrial_rules:
  access_control:
    - rule_id: "SEC-IND-001"
      name: "Critical Control Security"
      description: "All critical industrial controls must have proper security"
      severity: "error"
      applies_to: ["equipment_control", "process_control", "safety_systems"]
      security_requirements:
        role_based_access: true
        audit_logging: true
        confirmation_dialogs: true
        session_validation: true
      critical_operations:
        - pattern: ".*[Ss]tart.*"
          security_level: 2
          requires_confirmation: true
        - pattern: ".*[Ss]top.*"
          security_level: 2
          requires_confirmation: true
        - pattern: ".*(Emergency|SCRAM|Shutdown).*"
          security_level: 3
          requires_confirmation: false
          immediate_execution: true
      validation_template: |
        def validateSecurityForOperation(operation, operator, component):
            """
            Validate security requirements for industrial operations.
            """
            # Check user roles
            userRoles = system.security.getUserRoles(operator)
            requiredRoles = getRequiredRoles(operation)
            
            if not any(role in userRoles for role in requiredRoles):
                return False, "Insufficient role permissions"
            
            # Check session validity
            if not isSessionValid(operator):
                return False, "Session expired or invalid"
            
            # Log security check
            logSecurityCheck(operation, operator, component, True)
            
            return True, "Security validation passed"
            
  data_integrity:
    - rule_id: "SEC-IND-002"
      name: "Process Data Integrity"
      description: "Process data modifications must maintain integrity"
      severity: "error"
      data_types: ["setpoints", "recipe_parameters", "alarm_limits"]
      integrity_checks:
        - range_validation: true
        - checksum_verification: true
        - change_authorization: true
        - backup_before_change: true
      validation_logic: |
        def validateDataIntegrity(dataType, oldValue, newValue, operator):
            """
            Validate data integrity for process modifications.
            """
            # Range validation
            if not isValueInRange(dataType, newValue):
                return False, "Value outside acceptable range"
            
            # Calculate checksum
            checksum = calculateChecksum(dataType, newValue)
            
            # Verify authorization
            if not hasChangeAuthorization(operator, dataType):
                return False, "Change authorization required"
            
            # Create backup
            createDataBackup(dataType, oldValue, operator)
            
            return True, checksum
```

This enhanced rules engine provides comprehensive, production-tested patterns specifically tailored for Ignition development in industrial automation environments, with special focus on whiskey production operations and FDA compliance requirements.