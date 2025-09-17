#!/usr/bin/env python3
"""
WHK Rules Engine Service
Validates Ignition components against WHK standards and best practices
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="WHK Rules Engine", description="Validation service for Ignition components")

@dataclass
class ValidationIssue:
    rule_id: str
    severity: str  # "error", "warning", "info"
    message: str
    suggested_fix: str
    line_number: Optional[int] = None

class ComponentValidationRequest(BaseModel):
    component: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class ScriptValidationRequest(BaseModel):
    script: str
    context: Optional[Dict[str, Any]] = None

class ValidationResponse(BaseModel):
    valid: bool
    issues: List[Dict[str, Any]]
    score: float
    validation_passed: bool

class WHKRulesEngine:
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load WHK-specific validation rules"""
        return {
            "perspective_components": {
                "BTN-ADV-001": {
                    "name": "Production Control Security",
                    "description": "Production control buttons must have role-based security",
                    "severity": "error",
                    "applies_to": ["ia.display.button"],
                    "check": self._check_production_button_security
                },
                "BTN-ADV-002": {
                    "name": "WHK Process Button Patterns",
                    "description": "Buttons should follow WHK color and naming standards",
                    "severity": "warning", 
                    "applies_to": ["ia.display.button"],
                    "check": self._check_whk_button_patterns
                },
                "COMP-001": {
                    "name": "Security Role Access",
                    "description": "All production components must specify security roles",
                    "severity": "error",
                    "applies_to": ["*"],
                    "check": self._check_security_roles
                },
                "WHK-STD-001": {
                    "name": "WHK Standard Version",
                    "description": "Components should specify WHK standard version",
                    "severity": "warning",
                    "applies_to": ["*"],
                    "check": self._check_whk_standard
                }
            },
            "jython_scripts": {
                "SCRIPT-001": {
                    "name": "Error Handling Required",
                    "description": "Production scripts must include error handling",
                    "severity": "error",
                    "check": self._check_error_handling
                },
                "SCRIPT-002": {
                    "name": "WHK Logging Standards",
                    "description": "Scripts should use WHK logging patterns",
                    "severity": "warning",
                    "check": self._check_whk_logging
                },
                "SCRIPT-003": {
                    "name": "Tag Write Safety",
                    "description": "Use writeBlocking for critical operations",
                    "severity": "error",
                    "check": self._check_tag_write_safety
                }
            }
        }
    
    def validate_component(self, component: Dict[str, Any], context: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate a Perspective component"""
        issues = []
        component_type = component.get("type", "")
        
        # Apply component-specific rules
        for rule_id, rule in self.rules["perspective_components"].items():
            if self._rule_applies(rule, component_type):
                issue = rule["check"](component, context)
                if issue:
                    issues.append(issue)
        
        return issues
    
    def validate_script(self, script: str, context: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate a Jython script"""
        issues = []
        
        # Apply script rules
        for rule_id, rule in self.rules["jython_scripts"].items():
            issue = rule["check"](script, context)
            if issue:
                issues.append(issue)
        
        return issues
    
    def _rule_applies(self, rule: Dict[str, Any], component_type: str) -> bool:
        """Check if a rule applies to the component type"""
        applies_to = rule.get("applies_to", [])
        return "*" in applies_to or component_type in applies_to
    
    # Component validation methods
    def _check_production_button_security(self, component: Dict[str, Any], context: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Check if production control buttons have proper security"""
        if component.get("type") != "ia.display.button":
            return None
        
        # Check if button affects production
        events = component.get("events", {})
        script = events.get("onActionPerformed", {}).get("config", {}).get("script", "")
        
        if any(keyword in script.lower() for keyword in ["tag.write", "start", "stop", "control"]):
            # This is a production control button
            meta = component.get("meta", {})
            security = meta.get("security", {})
            
            if not security.get("roleAccess"):
                return ValidationIssue(
                    rule_id="BTN-ADV-001",
                    severity="error",
                    message="Production control buttons require security role access",
                    suggested_fix="Add meta.security.roleAccess array with appropriate roles"
                )
        
        return None
    
    def _check_whk_button_patterns(self, component: Dict[str, Any], context: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Check WHK button patterns"""
        if component.get("type") != "ia.display.button":
            return None
        
        text = component.get("props", {}).get("text", "")
        style = component.get("props", {}).get("style", {})
        
        # Check for start/stop button colors
        if text.lower().startswith("start") and style.get("backgroundColor") != "#28a745":
            return ValidationIssue(
                rule_id="BTN-ADV-002",
                severity="warning",
                message="Start buttons should use WHK success green (#28a745)",
                suggested_fix="Set style.backgroundColor to '#28a745'"
            )
        
        if text.lower().startswith("stop") and style.get("backgroundColor") != "#dc3545":
            return ValidationIssue(
                rule_id="BTN-ADV-002", 
                severity="warning",
                message="Stop buttons should use WHK danger red (#dc3545)",
                suggested_fix="Set style.backgroundColor to '#dc3545'"
            )
        
        return None
    
    def _check_security_roles(self, component: Dict[str, Any], context: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Check if component has security roles"""
        meta = component.get("meta", {})
        security = meta.get("security", {})
        
        if not security.get("roleAccess"):
            return ValidationIssue(
                rule_id="COMP-001",
                severity="error", 
                message="Component missing security role access",
                suggested_fix="Add meta.security.roleAccess array"
            )
        
        return None
    
    def _check_whk_standard(self, component: Dict[str, Any], context: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Check if component specifies WHK standard"""
        custom = component.get("custom", {})
        
        if not custom.get("whkStandard"):
            return ValidationIssue(
                rule_id="WHK-STD-001",
                severity="warning",
                message="Component should specify WHK standard version",
                suggested_fix="Add custom.whkStandard property"
            )
        
        return None
    
    # Script validation methods
    def _check_error_handling(self, script: str, context: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Check if script has error handling"""
        if "try:" not in script or "except" not in script:
            return ValidationIssue(
                rule_id="SCRIPT-001",
                severity="error",
                message="Production scripts must include try/except error handling",
                suggested_fix="Wrap critical operations in try/except blocks"
            )
        
        return None
    
    def _check_whk_logging(self, script: str, context: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Check if script uses WHK logging standards"""
        if "WHK" not in script or "logger" not in script.lower():
            return ValidationIssue(
                rule_id="SCRIPT-002",
                severity="warning",
                message="Scripts should use WHK logging standards",
                suggested_fix="Use LoggerEx.newBuilder().name('WHK.ModuleName').build()"
            )
        
        return None
    
    def _check_tag_write_safety(self, script: str, context: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Check if script uses safe tag writing"""
        if "system.tag.write(" in script and "writeBlocking" not in script:
            return ValidationIssue(
                rule_id="SCRIPT-003",
                severity="error",
                message="Use writeBlocking for critical tag operations",
                suggested_fix="Replace system.tag.write with system.tag.writeBlocking"
            )
        
        return None

# Initialize rules engine
rules_engine = WHKRulesEngine()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "whk-rules-engine"}

@app.post("/validate/component", response_model=ValidationResponse)
async def validate_component(request: ComponentValidationRequest):
    """Validate a Perspective component"""
    try:
        issues = rules_engine.validate_component(request.component, request.context)
        
        # Convert issues to dict format
        issue_dicts = []
        error_count = 0
        
        for issue in issues:
            issue_dict = {
                "rule_id": issue.rule_id,
                "severity": issue.severity,
                "message": issue.message,
                "suggested_fix": issue.suggested_fix
            }
            if issue.line_number:
                issue_dict["line_number"] = issue.line_number
            
            issue_dicts.append(issue_dict)
            
            if issue.severity == "error":
                error_count += 1
        
        # Calculate validation score
        total_issues = len(issues)
        score = max(0.0, 1.0 - (error_count * 0.3 + (total_issues - error_count) * 0.1))
        
        return ValidationResponse(
            valid=error_count == 0,
            issues=issue_dicts,
            score=score,
            validation_passed=error_count == 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate/script", response_model=ValidationResponse)
async def validate_script(request: ScriptValidationRequest):
    """Validate a Jython script"""
    try:
        issues = rules_engine.validate_script(request.script, request.context)
        
        # Convert issues to dict format
        issue_dicts = []
        error_count = 0
        
        for issue in issues:
            issue_dict = {
                "rule_id": issue.rule_id,
                "severity": issue.severity,
                "message": issue.message,
                "suggested_fix": issue.suggested_fix
            }
            if issue.line_number:
                issue_dict["line_number"] = issue.line_number
            
            issue_dicts.append(issue_dict)
            
            if issue.severity == "error":
                error_count += 1
        
        # Calculate validation score
        total_issues = len(issues)
        score = max(0.0, 1.0 - (error_count * 0.3 + (total_issues - error_count) * 0.1))
        
        return ValidationResponse(
            valid=error_count == 0,
            issues=issue_dicts,
            score=score,
            validation_passed=error_count == 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules")
async def get_rules():
    """Get available validation rules"""
    return {
        "perspective_components": list(rules_engine.rules["perspective_components"].keys()),
        "jython_scripts": list(rules_engine.rules["jython_scripts"].keys())
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8087)