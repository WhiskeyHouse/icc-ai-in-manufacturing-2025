#!/usr/bin/env python3
"""
Ignition Web Development Validation Endpoints
Provides doGet, doPost, doPatch validation endpoints for Jython scripts, components, and tag management.
"""

# These imports work in Ignition's Jython environment
import system
import json
from javax.servlet.http import HttpServletResponse
from java.util import Date
from com.inductiveautomation.ignition.common.util import LoggerEx

# Initialize logger
logger = LoggerEx.newBuilder().name("WHK.ValidationAPI").build()

# In-memory storage for validation sessions (in production, use database)
validation_sessions = {}

# Rules Engine Integration (simulated - in real deployment, call actual rules engine)
class WHKValidationRules:
    """WHK-specific validation rules for scripts and components."""
    
    @staticmethod
    def validate_script(script_content, context=None):
        """Validate Jython script content."""
        issues = []
        
        # Rule 1: Error handling check
        if "try:" not in script_content or "except" not in script_content:
            issues.append({
                "rule_id": "SCRIPT-001",
                "severity": "error",
                "message": "Production scripts must include try/except error handling",
                "suggested_fix": "Wrap critical operations in try/except blocks"
            })
        
        # Rule 2: WHK logging standards
        if "WHK" not in script_content or "logger" not in script_content.lower():
            issues.append({
                "rule_id": "SCRIPT-002", 
                "severity": "warning",
                "message": "Scripts should use WHK logging standards",
                "suggested_fix": "Use LoggerEx.newBuilder().name('WHK.ModuleName').build()"
            })
        
        # Rule 3: Tag write safety
        if "system.tag.write(" in script_content and "writeBlocking" not in script_content:
            issues.append({
                "rule_id": "SCRIPT-003",
                "severity": "error", 
                "message": "Use writeBlocking for critical tag operations",
                "suggested_fix": "Replace system.tag.write with system.tag.writeBlocking"
            })
        
        # Rule 4: FDA compliance logging
        if any(keyword in script_content.lower() for keyword in ["batch", "recipe", "production"]):
            if "audit" not in script_content.lower():
                issues.append({
                    "rule_id": "SCRIPT-004",
                    "severity": "warning",
                    "message": "Production operations should include audit logging",
                    "suggested_fix": "Add audit trail logging for FDA compliance"
                })
        
        # Calculate score
        error_count = len([i for i in issues if i["severity"] == "error"])
        total_issues = len(issues)
        score = max(0.0, 1.0 - (error_count * 0.3 + (total_issues - error_count) * 0.1))
        
        return {
            "valid": error_count == 0,
            "issues": issues,
            "score": score,
            "validation_passed": error_count == 0,
            "timestamp": str(Date())
        }
    
    @staticmethod
    def validate_component(component_data, context=None):
        """Validate Perspective component."""
        issues = []
        
        component_type = component_data.get("type", "")
        
        # Rule 1: Security role access
        meta = component_data.get("meta", {})
        security = meta.get("security", {})
        if not security.get("roleAccess"):
            issues.append({
                "rule_id": "COMP-001",
                "severity": "error",
                "message": "Component missing security role access", 
                "suggested_fix": "Add meta.security.roleAccess array"
            })
        
        # Rule 2: WHK standard version
        custom = component_data.get("custom", {})
        if not custom.get("whkStandard"):
            issues.append({
                "rule_id": "WHK-STD-001",
                "severity": "warning",
                "message": "Component should specify WHK standard version",
                "suggested_fix": "Add custom.whkStandard property"
            })
        
        # Button-specific rules
        if component_type == "ia.display.button":
            # Check for production control security
            events = component_data.get("events", {})
            script = events.get("onActionPerformed", {}).get("config", {}).get("script", "")
            
            if any(keyword in script.lower() for keyword in ["tag.write", "start", "stop", "control"]):
                if not security.get("roleAccess"):
                    issues.append({
                        "rule_id": "BTN-ADV-001",
                        "severity": "error", 
                        "message": "Production control buttons require security role access",
                        "suggested_fix": "Add meta.security.roleAccess array with appropriate roles"
                    })
            
            # Check button color standards
            text = component_data.get("props", {}).get("text", "")
            style = component_data.get("props", {}).get("style", {})
            
            if text.lower().startswith("start") and style.get("backgroundColor") != "#28a745":
                issues.append({
                    "rule_id": "BTN-ADV-002",
                    "severity": "warning",
                    "message": "Start buttons should use WHK success green (#28a745)",
                    "suggested_fix": "Set style.backgroundColor to '#28a745'"
                })
            
            if text.lower().startswith("stop") and style.get("backgroundColor") != "#dc3545":
                issues.append({
                    "rule_id": "BTN-ADV-002",
                    "severity": "warning", 
                    "message": "Stop buttons should use WHK danger red (#dc3545)",
                    "suggested_fix": "Set style.backgroundColor to '#dc3545'"
                })
        
        # Calculate score
        error_count = len([i for i in issues if i["severity"] == "error"])
        total_issues = len(issues)
        score = max(0.0, 1.0 - (error_count * 0.3 + (total_issues - error_count) * 0.1))
        
        return {
            "valid": error_count == 0,
            "issues": issues,
            "score": score,
            "validation_passed": error_count == 0,
            "timestamp": str(Date())
        }


def doGet(request, session):
    """
    Handle GET requests for validation endpoints.
    
    Supported endpoints:
    - /validation/sessions - List all validation sessions
    - /validation/sessions/{session_id} - Get specific session
    - /validation/health - Health check
    """
    try:
        path_info = request.getPathInfo() or ""
        
        if path_info == "/health":
            return {
                "status": "healthy",
                "service": "whk-validation-api",
                "version": "1.0.0",
                "timestamp": str(Date()),
                "endpoints": [
                    "GET /validation/health",
                    "GET /validation/sessions", 
                    "GET /validation/sessions/{id}",
                    "POST /validation/scripts",
                    "POST /validation/components",
                    "POST /validation/tags",
                    "PATCH /validation/tags",
                    "PATCH /validation/sessions/{id}"
                ]
            }
        
        elif path_info == "/sessions":
            # List all validation sessions
            sessions = []
            for session_id, session_data in validation_sessions.items():
                sessions.append({
                    "session_id": session_id,
                    "type": session_data.get("type"),
                    "metadata": session_data.get("metadata", {}),
                    "has_validation": "validation_result" in session_data,
                    "created_at": session_data.get("created_at"),
                    "updated_at": session_data.get("updated_at")
                })
            
            return {
                "sessions": sessions,
                "total": len(sessions),
                "timestamp": str(Date())
            }
        
        elif path_info.startswith("/sessions/"):
            # Get specific session
            session_id = path_info.split("/sessions/")[1]
            
            if session_id in validation_sessions:
                return validation_sessions[session_id]
            else:
                return {
                    "error": "Session not found",
                    "session_id": session_id,
                    "status_code": 404
                }
        
        else:
            return {
                "error": "Endpoint not found",
                "path": path_info,
                "available_endpoints": ["/health", "/sessions", "/sessions/{id}"],
                "status_code": 404
            }
    
    except Exception as e:
        logger.error("Error in doGet: " + str(e))
        return {
            "error": "Internal server error",
            "message": str(e),
            "status_code": 500
        }


def doPost(request, session):
    """
    Handle POST requests for validation.
    
    Supported endpoints:
    - /validation/scripts - Validate Jython script
    - /validation/components - Validate Perspective component
    - /validation/tags - Create Ignition tags
    """
    try:
        path_info = request.getPathInfo() or ""
        
        # Parse request body
        request_body = request.getReader().lines()
        body_text = '\n'.join([line for line in request_body])
        request_data = json.loads(body_text) if body_text else {}
        
        if path_info == "/scripts":
            # Validate Jython script
            script_content = request_data.get("script")
            context = request_data.get("context", {})
            metadata = request_data.get("metadata", {})
            
            if not script_content:
                return {
                    "error": "Script content is required",
                    "status_code": 400
                }
            
            # Generate session ID
            session_id = str(system.date.now().time) + "_" + str(hash(script_content) % 10000)
            now = str(Date())
            
            # Validate the script
            validation_result = WHKValidationRules.validate_script(script_content, context)
            
            # Store session
            validation_sessions[session_id] = {
                "session_id": session_id,
                "type": "script",
                "script": script_content,
                "context": context,
                "metadata": metadata,
                "validation_result": validation_result,
                "created_at": now,
                "updated_at": now
            }
            
            logger.info("Script validation session created: " + session_id)
            
            return {
                "session_id": session_id,
                "validation_result": validation_result,
                "created_at": now
            }
        
        elif path_info == "/components":
            # Validate Perspective component
            component_data = request_data.get("component")
            context = request_data.get("context", {})
            
            if not component_data:
                return {
                    "error": "Component data is required",
                    "status_code": 400
                }
            
            # Validate the component
            validation_result = WHKValidationRules.validate_component(component_data, context)
            
            logger.info("Component validation completed for type: " + component_data.get("type", "unknown"))
            
            return {
                "component_type": component_data.get("type", "unknown"),
                "validation_result": validation_result,
                "timestamp": str(Date())
            }

        elif path_info == "/tags":
            # Create new Ignition tags
            tag_definitions = request_data.get("tags")
            base_path = request_data.get("basePath", "")
            collision_policy = request_data.get("collisionPolicy", "a")  # default to abort on conflict
            metadata = request_data.get("metadata", {})

            if not tag_definitions or not isinstance(tag_definitions, list):
                return {
                    "error": "Tag definitions list is required",
                    "status_code": 400
                }

            try:
                configure_result = system.tag.configure(base_path, tag_definitions, collision_policy)
                normalized_result = normalize_tag_config_results(configure_result)
                logger.info("Created tags under base path '{}', count={}".format(base_path or "[project root]", len(tag_definitions)))
            except Exception as tag_error:
                logger.error("Error creating tags: " + str(tag_error))
                return {
                    "error": "Failed to create tags",
                    "message": str(tag_error),
                    "status_code": 500
                }

            return {
                "operation": "create",
                "base_path": base_path,
                "collision_policy": collision_policy,
                "metadata": metadata,
                "results": normalized_result,
                "timestamp": str(Date())
            }
        
        else:
            return {
                "error": "Endpoint not found",
                "path": path_info,
                "available_endpoints": ["/scripts", "/components", "/tags"],
                "status_code": 404
            }
    
    except Exception as e:
        logger.error("Error in doPost: " + str(e))
        return {
            "error": "Internal server error",
            "message": str(e),
            "status_code": 500
        }


def doPatch(request, session):
    """
    Handle PATCH requests for updating validation sessions.
    
    Supported endpoints:
    - /validation/tags - Update Ignition tags (merge/overwrite)
    - /validation/sessions/{session_id} - Update validation session
    """
    try:
        path_info = request.getPathInfo() or ""

        # Parse request body once for all PATCH handlers
        request_body = request.getReader().lines()
        body_text = '\n'.join([line for line in request_body])
        request_data = json.loads(body_text) if body_text else {}

        if path_info == "/tags":
            tag_definitions = request_data.get("tags")
            base_path = request_data.get("basePath", "")
            collision_policy = request_data.get("collisionPolicy", "m")  # merge into existing tags by default
            metadata = request_data.get("metadata", {})

            if not tag_definitions or not isinstance(tag_definitions, list):
                return {
                    "error": "Tag definitions list is required",
                    "status_code": 400
                }

            try:
                configure_result = system.tag.configure(base_path, tag_definitions, collision_policy)
                normalized_result = normalize_tag_config_results(configure_result)
                logger.info("Updated tags under base path '{}', count={}".format(base_path or "[project root]", len(tag_definitions)))
            except Exception as tag_error:
                logger.error("Error updating tags: " + str(tag_error))
                return {
                    "error": "Failed to update tags",
                    "message": str(tag_error),
                    "status_code": 500
                }

            return {
                "operation": "update",
                "base_path": base_path,
                "collision_policy": collision_policy,
                "metadata": metadata,
                "results": normalized_result,
                "timestamp": str(Date())
            }

        elif path_info.startswith("/sessions/"):
            session_id = path_info.split("/sessions/")[1]
            
            if session_id not in validation_sessions:
                return {
                    "error": "Session not found",
                    "session_id": session_id,
                    "status_code": 404
                }
            
            session_data = validation_sessions[session_id]
            now = str(Date())
            
            # Update fields if provided
            if "script_updates" in request_data:
                session_data["script"] = request_data["script_updates"]
                
                # Re-validate script
                validation_result = WHKValidationRules.validate_script(
                    session_data["script"],
                    session_data.get("context", {})
                )
                session_data["validation_result"] = validation_result
            
            if "context" in request_data:
                session_data["context"] = request_data["context"]
            
            if "metadata" in request_data:
                session_data["metadata"].update(request_data["metadata"])
            
            session_data["updated_at"] = now
            
            logger.info("Validation session updated: " + session_id)
            
            return {
                "session_id": session_id,
                "updated_at": now,
                "validation_result": session_data.get("validation_result"),
                "message": "Session updated successfully"
            }
        
        else:
            return {
                "error": "Endpoint not found",
                "path": path_info,
                "available_endpoints": ["/tags", "/sessions/{id}"],
                "status_code": 404
            }
    
    except Exception as e:
        logger.error("Error in doPatch: " + str(e))
        return {
            "error": "Internal server error",
            "message": str(e),
            "status_code": 500
        }


# Helper utilities shared by multiple endpoints
def normalize_tag_config_results(configure_result):
    """Convert Ignition tag configure results into JSON-friendly data."""
    normalized = []

    if not configure_result:
        return normalized

    try:
        for entry in configure_result:
            entry_dict = {}

            if isinstance(entry, dict):
                entry_dict = entry
            else:
                # Fallback for Java objects returned from Ignition APIs
                entry_dict = {
                    "path": getattr(entry, "fullPath", None) or getattr(entry, "path", None) or getattr(entry, "tagPath", None),
                    "status": getattr(entry, "status", None) or getattr(entry, "result", None),
                    "message": getattr(entry, "message", None) or getattr(entry, "errorMessage", None) or getattr(entry, "error", None)
                }

            normalized.append({
                "path": entry_dict.get("fullPath") or entry_dict.get("path") or entry_dict.get("tagPath"),
                "status": entry_dict.get("status") or entry_dict.get("result"),
                "message": entry_dict.get("message") or entry_dict.get("errorMessage")
            })
    except Exception as normalize_error:
        logger.warn("Unable to normalize tag configure results: " + str(normalize_error))

    return normalized


def set_json_response_headers(response):
    """Set appropriate headers for JSON responses."""
    response.setContentType("application/json")
    response.setHeader("Access-Control-Allow-Origin", "*")
    response.setHeader("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
    response.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization")


# Main request handler (called by Ignition's web dev module)
def handleRequest(request, response):
    """Main request handler for validation API."""
    try:
        method = request.getMethod()
        result = None
        
        if method == "GET":
            result = doGet(request, None)
        elif method == "POST":
            result = doPost(request, None)
        elif method == "PATCH":
            result = doPatch(request, None)
        elif method == "OPTIONS":
            # Handle preflight requests
            set_json_response_headers(response)
            response.setStatus(200)
            return
        else:
            result = {
                "error": "Method not allowed",
                "method": method,
                "allowed_methods": ["GET", "POST", "PATCH", "OPTIONS"],
                "status_code": 405
            }
        
        # Set response headers
        set_json_response_headers(response)
        
        # Set status code if provided
        if result and "status_code" in result:
            response.setStatus(result["status_code"])
        else:
            response.setStatus(200)
        
        # Write response
        response.getWriter().write(json.dumps(result, indent=2))
        
        # Log the request
        logger.trace("API request handled: {} {} - Status: {}".format(
            method,
            request.getPathInfo() or "/",
            result.get("status_code", 200) if result else 200
        ))
    
    except Exception as e:
        logger.error("Critical error in handleRequest: " + str(e))
        set_json_response_headers(response)
        response.setStatus(500)
        response.getWriter().write(json.dumps({
            "error": "Critical server error",
            "message": str(e)
        }))
