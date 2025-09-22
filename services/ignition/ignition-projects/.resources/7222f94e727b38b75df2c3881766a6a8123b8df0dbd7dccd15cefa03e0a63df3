"""WHK Validation Module
Provides validation logic, rules engine integration, and session management
for the WHK validation WebDev API.
"""

import system
from java.util import Date
from com.inductiveautomation.ignition.common.util import LoggerEx

# Central logger for validation operations
logger = LoggerEx.newBuilder().name("WHK.Validation").build()

# In-memory storage for validation sessions (lives in gateway scope)
validation_sessions = {}


class WHKValidationRules(object):
    """Local validation rules for scripts and Perspective components."""

    @staticmethod
    def validate_script(script_content, context=None):
        issues = []

        if "try:" not in script_content or "except" not in script_content:
            issues.append({
                "rule_id": "SCRIPT-001",
                "severity": "error",
                "message": "Production scripts must include try/except error handling",
                "suggested_fix": "Wrap critical operations in try/except blocks"
            })

        lowered = script_content.lower()
        if "logger" not in lowered or "whk" not in script_content:
            issues.append({
                "rule_id": "SCRIPT-002",
                "severity": "warning",
                "message": "Scripts should use WHK logging standards",
                "suggested_fix": "Use LoggerEx.newBuilder().name('WHK.Module').build()"
            })

        if "system.tag.write(" in script_content and "writeBlocking" not in script_content:
            issues.append({
                "rule_id": "SCRIPT-003",
                "severity": "error",
                "message": "Use writeBlocking for critical tag operations",
                "suggested_fix": "Replace system.tag.write with system.tag.writeBlocking"
            })

        if any(keyword in lowered for keyword in ["batch", "recipe", "production"]):
            if "audit" not in lowered:
                issues.append({
                    "rule_id": "SCRIPT-004",
                    "severity": "warning",
                    "message": "Production operations should include audit logging",
                    "suggested_fix": "Add audit trail logging for FDA compliance"
                })

        error_count = len([i for i in issues if i.get("severity") == "error"])
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
        issues = []
        component_type = component_data.get("type", "") if isinstance(component_data, dict) else ""

        meta = component_data.get("meta", {}) if isinstance(component_data, dict) else {}
        security = meta.get("security", {}) if isinstance(meta, dict) else {}
        if not security.get("roleAccess"):
            issues.append({
                "rule_id": "COMP-001",
                "severity": "error",
                "message": "Component missing security role access",
                "suggested_fix": "Add meta.security.roleAccess array"
            })

        custom = component_data.get("custom", {}) if isinstance(component_data, dict) else {}
        if not custom.get("whkStandard"):
            issues.append({
                "rule_id": "WHK-STD-001",
                "severity": "warning",
                "message": "Component should specify WHK standard version",
                "suggested_fix": "Add custom.whkStandard property"
            })

        if component_type == "ia.display.button":
            events = component_data.get("events", {})
            on_action = events.get("onActionPerformed", {}) if isinstance(events, dict) else {}
            script = on_action.get("config", {}).get("script", "")

            lower_script = script.lower()
            if any(keyword in lower_script for keyword in ["tag.write", "start", "stop", "control"]):
                if not security.get("roleAccess"):
                    issues.append({
                        "rule_id": "BTN-ADV-001",
                        "severity": "error",
                        "message": "Production control buttons require security role access",
                        "suggested_fix": "Add meta.security.roleAccess array with appropriate roles"
                    })

            props = component_data.get("props", {}) if isinstance(component_data, dict) else {}
            text = props.get("text", "")
            style = props.get("style", {}) if isinstance(props, dict) else {}

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

        error_count = len([i for i in issues if i.get("severity") == "error"])
        total_issues = len(issues)
        score = max(0.0, 1.0 - (error_count * 0.3 + (total_issues - error_count) * 0.1))

        return {
            "valid": error_count == 0,
            "issues": issues,
            "score": score,
            "validation_passed": error_count == 0,
            "timestamp": str(Date())
        }


def _call_rules_engine(path, payload):
    """Call the external rules engine, returning (success, result)."""
    url = "http://host.docker.internal:8087" + path
    headers = {"Content-Type": "application/json"}

    try:
        response = system.net.httpPost(url, headers, system.util.jsonEncode(payload))
        return True, system.util.jsonDecode(response)
    except Exception as exc:  # pragma: no cover - network failure path
        logger.warn("Rules engine call failed: {}".format(exc))
        fallback = {
            "valid": False,
            "error": str(exc),
            "issues": [{
                "rule_id": "RULES-ENGINE",
                "severity": "error",
                "message": "Failed to connect to rules engine",
                "details": str(exc)
            }],
            "score": 0.0,
            "validation_passed": False,
            "timestamp": str(Date())
        }
        return False, fallback


def validate_script_with_rules_engine(script_content, context=None, metadata=None, fallback_to_local=True):
    """Validate script content using the external rules engine with optional fallback."""
    payload = {
        "script": script_content,
        "context": context or {},
        "metadata": metadata or {}
    }

    success, result = _call_rules_engine("/validate/script", payload)
    if success or not fallback_to_local:
        return result

    local_result = WHKValidationRules.validate_script(script_content, context)
    local_result["rules_engine_error"] = result.get("error")
    local_result["fallback_used"] = True
    return local_result


def validate_component_with_rules_engine(component_data, context=None, metadata=None, fallback_to_local=True):
    """Validate component configuration using the external rules engine with optional fallback."""
    payload = {
        "component": component_data,
        "context": context or {},
        "metadata": metadata or {}
    }

    success, result = _call_rules_engine("/validate/component", payload)
    if success or not fallback_to_local:
        return result

    local_result = WHKValidationRules.validate_component(component_data, context)
    local_result["rules_engine_error"] = result.get("error")
    local_result["fallback_used"] = True
    return local_result


def validate_script_local(script_content, context=None):
    """Run validation rules without contacting the rules engine."""
    return WHKValidationRules.validate_script(script_content, context)


def validate_component_local(component_data, context=None):
    """Run component validation rules without contacting the rules engine."""
    return WHKValidationRules.validate_component(component_data, context)


def generate_session_id(content=None):
    """Generate a deterministic session ID when possible."""
    base = str(Date().getTime())
    if content:
        base = base + "_" + str(abs(hash(content)) % 10000)
    return base


def create_validation_session(validation_type, content, validation_result=None,
                              context=None, session_id=None, metadata=None):
    """Create or update a validation session record."""
    identifier = session_id or generate_session_id(content)
    now = str(Date())

    existing = validation_sessions.get(identifier, {})
    merged_metadata = {}
    if isinstance(existing.get("metadata"), dict):
        merged_metadata.update(existing["metadata"])
    if isinstance(metadata, dict):
        merged_metadata.update(metadata)

    context_value = context if context is not None else existing.get("context", {})
    session_record = {
        "id": identifier,
        "session_id": identifier,
        "type": validation_type,
        "content": content,
        "context": context_value,
        "metadata": merged_metadata,
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "status": existing.get("status", "pending"),
        "validation_result": validation_result or existing.get("validation_result"),
        "review_notes": existing.get("review_notes", []),
        "history": existing.get("history", [])
    }

    if validation_type == "script":
        session_record["script"] = content
    elif validation_type == "component":
        session_record["component"] = content

    if validation_result:
        session_record["status"] = "completed" if validation_result.get("valid", False) else "needs_review"
        session_record.setdefault("history", []).append({
            "timestamp": now,
            "event": "validation",
            "details": {
                "score": validation_result.get("score"),
                "valid": validation_result.get("valid", False)
            }
        })

    validation_sessions[identifier] = session_record
    logger.info("Validation session stored: {}".format(identifier))
    return session_record


def get_validation_session(session_id):
    """Retrieve validation session by ID."""
    return validation_sessions.get(session_id)


def list_validation_sessions():
    """Return a list of session summaries."""
    summaries = []
    for session_id, data in validation_sessions.items():
        result = data.get("validation_result") or {}
        summaries.append({
            "session_id": session_id,
            "type": data.get("type"),
            "status": data.get("status"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "has_result": bool(result),
            "score": result.get("score"),
            "last_reviewer": data.get("last_reviewer")
        })
    return summaries


def update_validation_session(session_id, script_updates=None, component_updates=None,
                              content=None, context=None, metadata=None, status=None,
                              notes=None, reviewer=None, revalidate=False,
                              validation_mode="local"):
    """Update a validation session record and optionally revalidate."""
    session = validation_sessions.get(session_id)
    if not session:
        return None

    now = str(Date())
    updated_content = None

    if script_updates is not None:
        session["script"] = script_updates
        updated_content = script_updates
    if component_updates is not None:
        session["component"] = component_updates
        updated_content = component_updates
    if content is not None:
        updated_content = content

    if updated_content is not None:
        session["content"] = updated_content

    if context is not None:
        session["context"] = context

    if metadata and isinstance(metadata, dict):
        session.setdefault("metadata", {}).update(metadata)

    validation_result = None
    should_revalidate = revalidate or script_updates is not None or component_updates is not None or (content is not None)

    if should_revalidate:
        session_type = session.get("type")
        run_mode = validation_mode or "local"
        if session_type == "script":
            if run_mode == "rules" or run_mode == "rules_engine":
                validation_result = validate_script_with_rules_engine(session.get("script"), session.get("context"))
            elif run_mode == "auto":
                validation_result = validate_script_with_rules_engine(session.get("script"), session.get("context"))
            else:
                validation_result = validate_script_local(session.get("script"), session.get("context"))
        elif session_type == "component":
            if run_mode == "rules" or run_mode == "rules_engine":
                validation_result = validate_component_with_rules_engine(session.get("component"), session.get("context"))
            elif run_mode == "auto":
                validation_result = validate_component_with_rules_engine(session.get("component"), session.get("context"))
            else:
                validation_result = validate_component_local(session.get("component"), session.get("context"))

    if validation_result is not None:
        session["validation_result"] = validation_result
        session["status"] = "completed" if validation_result.get("valid", False) else "needs_review"
        session.setdefault("history", []).append({
            "timestamp": now,
            "event": "validation",
            "details": {
                "score": validation_result.get("score"),
                "valid": validation_result.get("valid", False)
            }
        })

    if status:
        session["status"] = status
        session.setdefault("history", []).append({
            "timestamp": now,
            "event": "status_change",
            "details": {"status": status}
        })

    if notes:
        note_entry = {
            "timestamp": now,
            "note": notes,
            "reviewer": reviewer or "system"
        }
        session.setdefault("review_notes", []).append(note_entry)
        session["last_reviewer"] = reviewer or "system"
    elif reviewer:
        session["last_reviewer"] = reviewer

    session["updated_at"] = now
    validation_sessions[session_id] = session
    logger.info("Validation session updated: {}".format(session_id))
    return session


def normalize_tag_config_results(configure_result):
    """Normalize Ignition tag configure results into JSON-friendly structures."""
    normalized = []
    if not configure_result:
        return normalized

    try:
        for entry in configure_result:
            if isinstance(entry, dict):
                entry_dict = entry
            else:
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
    except Exception as exc:  # pragma: no cover - defensive
        logger.warn("Unable to normalize tag configure results: {}".format(exc))

    return normalized


def get_rules_engine_health():
    """Check if the external rules engine is reachable."""
    url = "http://host.docker.internal:8087/health"
    try:
        response = system.net.httpGet(url)
        return True, response
    except Exception as exc:  # pragma: no cover - network failure path
        logger.warn("Rules engine health check failed: {}".format(exc))
        return False, str(exc)


def get_service_health():
    """Return service health information for dashboards."""
    rules_ok, details = get_rules_engine_health()
    return {
        "status": "healthy" if rules_ok else "degraded",
        "rules_engine": rules_ok,
        "rules_engine_details": details,
        "webdev_module": True,
        "session_count": len(validation_sessions)
    }


def reset_sessions():  # pragma: no cover - utility helper for testing
    """Utility helper to clear all validation sessions."""
    validation_sessions.clear()
    logger.info("Validation sessions reset")
