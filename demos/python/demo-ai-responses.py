#!/usr/bin/env python3
"""
Demo AI Response Generator
Simulates AI responses for the presentation based on predefined patterns
"""

import json
import time
import random

class DemoAIResponses:
    def __init__(self):
        self.patterns = self.load_patterns()
    
    def load_patterns(self):
        """Load predefined patterns for demo responses"""
        patterns = {}
        
        # Load fermentation tank pattern
        try:
            with open('demo-patterns/fermentation-tank-component.json', 'r') as f:
                patterns['fermentation_tank'] = json.load(f)
        except FileNotFoundError:
            patterns['fermentation_tank'] = {"error": "Pattern file not found"}
        
        # Load pump control pattern
        try:
            with open('demo-patterns/pump-control-script.py', 'r') as f:
                patterns['pump_control'] = f.read()
        except FileNotFoundError:
            patterns['pump_control'] = "# Pattern file not found"
        
        # Load batch recipe pattern
        try:
            with open('demo-patterns/batch-recipe-selector.json', 'r') as f:
                patterns['batch_recipe'] = json.load(f)
        except FileNotFoundError:
            patterns['batch_recipe'] = {"error": "Pattern file not found"}
        
        return patterns
    
    def simulate_ai_response(self, prompt):
        """Simulate AI response based on prompt content"""
        prompt_lower = prompt.lower()
        
        # Add realistic delay
        time.sleep(random.uniform(1.0, 2.5))
        
        if "fermentation" in prompt_lower and "tank" in prompt_lower:
            return {
                "response": json.dumps(self.patterns['fermentation_tank'], indent=2),
                "context_used": "WHK-Global Production Patterns",
                "confidence": 0.95,
                "sources": [
                    {
                        "file": "components/fermentation_tanks.json",
                        "confidence": 0.95,
                        "last_updated": "2024-09-15"
                    }
                ]
            }
        
        elif "pump" in prompt_lower and "control" in prompt_lower:
            return {
                "response": self.patterns['pump_control'],
                "context_used": "WHK-Global Production Scripts",
                "confidence": 0.92,
                "sources": [
                    {
                        "file": "scripts/pump_control.py", 
                        "confidence": 0.92,
                        "last_updated": "2024-09-12"
                    }
                ]
            }
        
        elif "batch" in prompt_lower and "recipe" in prompt_lower:
            return {
                "response": json.dumps(self.patterns['batch_recipe'], indent=2),
                "context_used": "Batch Management System",
                "confidence": 0.89,
                "sources": [
                    {
                        "file": "components/recipe_selector.json",
                        "confidence": 0.89, 
                        "last_updated": "2024-09-15"
                    }
                ]
            }
        
        else:
            return {
                "response": "I can help you create Ignition components. Try asking about fermentation tanks, pump control, or batch recipes.",
                "context_used": "General",
                "confidence": 0.3,
                "sources": []
            }
    
    def demo_validation(self, component_json):
        """Simulate MCP validation response"""
        try:
            component = json.loads(component_json)
            issues = []
            
            # Check for security roles
            if 'meta' not in component or 'security' not in component.get('meta', {}):
                issues.append({
                    "severity": "error",
                    "rule": "SECURITY-001",
                    "message": "Component missing security role access",
                    "suggested_fix": "Add meta.security.roleAccess array"
                })
            
            # Check for WHK standards
            if 'custom' not in component or 'whkStandard' not in component.get('custom', {}):
                issues.append({
                    "severity": "warning",
                    "rule": "WHK-STD-001", 
                    "message": "Component should specify WHK standard version",
                    "suggested_fix": "Add custom.whkStandard property"
                })
            
            return {
                "valid": len([i for i in issues if i['severity'] == 'error']) == 0,
                "issues": issues,
                "validation_passed": len(issues) == 0
            }
            
        except json.JSONDecodeError:
            return {
                "valid": False,
                "issues": [{
                    "severity": "error",
                    "rule": "SYNTAX-001",
                    "message": "Invalid JSON syntax",
                    "suggested_fix": "Check JSON formatting"
                }],
                "validation_passed": False
            }

def main():
    """Demo script for testing AI responses"""
    demo = DemoAIResponses()
    
    print("🤖 Demo AI Response Generator")
    print("=" * 50)
    
    test_prompts = [
        "Create a fermentation tank control panel following WHK standards",
        "Generate a pump control script with safety interlocks",
        "Design a batch recipe selector with FDA compliance",
        "Create something random"
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt: {prompt}")
        print("-" * 30)
        
        response = demo.simulate_ai_response(prompt)
        print(f"🎯 Context: {response['context_used']}")
        print(f"📊 Confidence: {response['confidence']}")
        print(f"📁 Sources: {len(response['sources'])}")
        
        if len(response['response']) > 200:
            print(f"📄 Response: {response['response'][:200]}...")
        else:
            print(f"📄 Response: {response['response']}")

if __name__ == "__main__":
    main()