#!/usr/bin/env python3
"""
Test AI-Powered Component Generation
Demonstrates the complete workflow of AI component generation with validation
"""

import json
import requests
import time

# Service endpoints
RAG_BASE_URL = "http://localhost:8086"
RULES_BASE_URL = "http://localhost:8087"

def simulate_ai_generation(component_request):
    """
    Simulate AI-powered component generation using our demo patterns
    In a real implementation, this would use LLM with RAG to generate components
    """
    
    # For demo purposes, we'll use templates based on the request type
    if "button" in component_request.lower():
        return {
            "type": "ia.display.button",
            "meta": {
                "name": "GeneratedButton"
            },
            "props": {
                "text": "Generated Button",
                "style": {
                    "backgroundColor": "#007bff"
                }
            },
            "events": {
                "onActionPerformed": {
                    "config": {
                        "script": "system.tag.write(['[default]Process/Command'], [True])"
                    }
                }
            }
        }
    elif "tank" in component_request.lower():
        return {
            "type": "ia.display.tank", 
            "meta": {
                "name": "GeneratedTank",
                "security": {
                    "roleAccess": ["Operators", "Engineers"]
                }
            },
            "props": {
                "style": {
                    "backgroundColor": "#2c3e50"
                },
                "tankConfiguration": {
                    "fillBinding": {
                        "type": "tag",
                        "config": {
                            "path": "[default]Tank/Level"
                        }
                    }
                }
            },
            "custom": {
                "whkStandard": "tank_v1",
                "auditLogging": True
            }
        }
    else:
        return {
            "type": "ia.display.label",
            "meta": {
                "name": "GeneratedLabel"
            },
            "props": {
                "text": "Generated Component"
            }
        }

def validate_component(component):
    """Validate generated component using rules engine"""
    try:
        response = requests.post(
            f"{RULES_BASE_URL}/validate/component",
            json={"component": component},
            timeout=10
        )
        return response.json() if response.status_code == 200 else {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def improve_component_with_validation(component, validation_result):
    """Apply validation suggestions to improve the component"""
    if validation_result.get("valid"):
        return component
    
    improved = component.copy()
    
    # Apply common fixes based on validation issues
    for issue in validation_result.get("issues", []):
        rule_id = issue.get("rule_id")
        
        if rule_id == "COMP-001":  # Missing security roles
            if "meta" not in improved:
                improved["meta"] = {}
            if "security" not in improved["meta"]:
                improved["meta"]["security"] = {}
            improved["meta"]["security"]["roleAccess"] = ["Operators", "Engineers"]
            
        elif rule_id == "WHK-STD-001":  # Missing WHK standard
            if "custom" not in improved:
                improved["custom"] = {}
            improved["custom"]["whkStandard"] = "generic_v1"
            
        elif rule_id == "BTN-ADV-002" and "start" in component.get("props", {}).get("text", "").lower():
            # Fix start button color
            if "props" not in improved:
                improved["props"] = {}
            if "style" not in improved["props"]:
                improved["props"]["style"] = {}
            improved["props"]["style"]["backgroundColor"] = "#28a745"
    
    return improved

def test_ai_component_generation():
    """Test complete AI-powered component generation workflow"""
    
    print("🤖 Testing AI-Powered Component Generation")
    print("=" * 60)
    
    # Test cases
    test_requests = [
        "Create a start button for production control",
        "Generate a fermentation tank monitoring display",
        "Build a simple status label"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📝 Test {i}: {request}")
        print("-" * 40)
        
        # Step 1: Generate initial component
        print("🔧 Step 1: Generating component...")
        component = simulate_ai_generation(request)
        print(f"   Generated: {component['type']} - {component['meta']['name']}")
        
        # Step 2: Validate component
        print("🔍 Step 2: Validating component...")
        validation = validate_component(component)
        
        if "error" in validation:
            print(f"   ❌ Validation failed: {validation['error']}")
            continue
            
        issues = validation.get("issues", [])
        score = validation.get("score", 0)
        
        if validation.get("valid"):
            print(f"   ✅ Component valid! Score: {score:.2f}")
        else:
            print(f"   ⚠️  Issues found ({len(issues)}), Score: {score:.2f}")
            for issue in issues:
                print(f"      - {issue['severity'].upper()}: {issue['message']}")
        
        # Step 3: Improve component if needed
        if not validation.get("valid"):
            print("🔄 Step 3: Applying validation improvements...")
            improved_component = improve_component_with_validation(component, validation)
            
            # Re-validate improved component
            improved_validation = validate_component(improved_component)
            
            if improved_validation.get("valid"):
                print(f"   ✅ Component improved! New score: {improved_validation.get('score', 0):.2f}")
                
                # Show the final component
                print("🎉 Final validated component:")
                print(json.dumps(improved_component, indent=2)[:500] + "...")
            else:
                print(f"   ⚠️  Still has issues. Score: {improved_validation.get('score', 0):.2f}")
        
        time.sleep(0.5)  # Small delay between tests
    
    print("\n🎯 AI Component Generation Test Complete!")

if __name__ == "__main__":
    test_ai_component_generation()