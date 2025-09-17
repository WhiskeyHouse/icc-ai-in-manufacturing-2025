#!/usr/bin/env python3
"""
Demo RAG Service for Presentation
Provides mock responses for the demo scenarios without requiring real AI APIs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import time
import random

app = FastAPI(title="Demo RAG Service", description="Mock RAG service for presentation demos")

class QueryRequest(BaseModel):
    query: str
    context: str = "whk-global"
    limit: int = 5
    include_recent: bool = False

class QueryResponse(BaseModel):
    response: str
    context_used: str
    sources: List[Dict[str, Any]]
    confidence: float
    response_time_ms: int

# Mock production patterns database
PRODUCTION_PATTERNS = {
    "whk-global": {
        "fermentation_tank": {
            "component": {
                "type": "ia.display.tank",
                "meta": {
                    "name": "FermentationTankMonitor",
                    "security": {
                        "roleAccess": ["Operators", "Brewmasters"]
                    }
                },
                "props": {
                    "style": {
                        "backgroundColor": "#2c3e50",
                        "borderColor": "#e67e22"
                    },
                    "tankConfiguration": {
                        "fillBinding": "[default]Fermentation/Tank_01/Level",
                        "temperatureBinding": "[default]Fermentation/Tank_01/Temperature",
                        "statusBinding": "[default]Fermentation/Tank_01/Status"
                    }
                },
                "custom": {
                    "whkStandard": "fermentation_v2",
                    "auditLogging": True,
                    "complianceLevel": "FDA"
                }
            }
        },
        "pump_control": {
            "script": '''# WHK production pattern with safety checks
import system
from com.inductiveautomation.ignition.common.util import LoggerEx

logger = LoggerEx.newBuilder().name("WHK.PumpControl").build()

def startPump():
    try:
        # Pre-start safety checks
        interlocks = system.tag.readBlocking([
            "[default]Equipment/Pump_01/Interlock_OK",
            "[default]Equipment/Pump_01/Ready"
        ])
        
        if all(v.value for v in interlocks):
            system.tag.writeBlocking([
                "[default]Equipment/Pump_01/Start"
            ], [True])
            
            logger.info("Pump P-01 started successfully")
            
            # Update audit trail
            system.tag.writeBlocking([
                "[default]Audit/LastAction",
                "[default]Audit/Operator", 
                "[default]Audit/Timestamp"
            ], [
                "Pump Start",
                system.security.getUserName(),
                system.date.now()
            ])
        else:
            logger.warn("Pump start blocked by safety interlocks")
            
    except Exception as e:
        logger.error("Pump start failed: " + str(e))

startPump()'''
        }
    },
    "reporting": {
        "dashboard_styles": {
            "component": {
                "type": "ia.display.chart",
                "props": {
                    "style": {
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                    }
                }
            }
        }
    }
}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "demo-rag"}

@app.get("/patterns")
async def get_patterns():
    return {"patterns": list(PRODUCTION_PATTERNS.keys())}

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    start_time = time.time()
    
    # Add realistic delay for demo effect
    await asyncio.sleep(0.5 + random.uniform(0, 0.5))
    
    query_lower = request.query.lower()
    context = request.context
    
    # Pattern matching for demo scenarios
    if "fermentation" in query_lower and "tank" in query_lower:
        pattern = PRODUCTION_PATTERNS.get(context, {}).get("fermentation_tank", {})
        response = json.dumps(pattern.get("component", {}), indent=2)
        sources = [
            {
                "source": "WHK-Global Production Code",
                "file": "components/fermentation_tanks.json", 
                "confidence": 0.95,
                "last_updated": "2024-09-10"
            }
        ]
        confidence = 0.95
        
    elif "pump" in query_lower and "control" in query_lower:
        pattern = PRODUCTION_PATTERNS.get(context, {}).get("pump_control", {})
        response = pattern.get("script", "# No pattern found")
        sources = [
            {
                "source": "WHK-Global Production Scripts",
                "file": "scripts/pump_control.py",
                "confidence": 0.92,
                "last_updated": "2024-09-12"
            }
        ]
        confidence = 0.92
        
    elif "batch" in query_lower and "recipe" in query_lower:
        response = """{
  "type": "ia.display.dropdown",
  "meta": {
    "name": "BatchRecipeSelector",
    "security": {
      "roleAccess": ["Operators", "Brewmasters", "QualityControl"]
    }
  },
  "props": {
    "options": [
      {"label": "Bourbon Mash", "value": "bourbon_001"},
      {"label": "Rye Whiskey", "value": "rye_001"},
      {"label": "Wheat Whiskey", "value": "wheat_001"}
    ],
    "placeholder": "Select Recipe..."
  },
  "events": {
    "onSelectionChanged": {
      "config": {
        "script": "# FDA compliance validation\\nsystem.audit.logRecipeSelection(event.source.value)"
      }
    }
  },
  "custom": {
    "whkStandard": "batch_v3",
    "fdaCompliance": true,
    "auditRequired": true
  }
}"""
        sources = [
            {
                "source": "Batch Management System",
                "file": "components/recipe_selector.json",
                "confidence": 0.89,
                "last_updated": "2024-09-15"
            }
        ]
        confidence = 0.89
        
    else:
        response = "No specific pattern found for this query. Consider refining your request."
        sources = []
        confidence = 0.3
    
    response_time = int((time.time() - start_time) * 1000)
    
    return QueryResponse(
        response=response,
        context_used=context,
        sources=sources,
        confidence=confidence,
        response_time_ms=response_time
    )

@app.post("/ingest")
async def ingest_data(data: Dict[str, Any]):
    """Mock data ingestion endpoint for demo"""
    return {
        "status": "success",
        "message": f"Ingested {data.get('source_type', 'unknown')} data",
        "indexed_items": random.randint(10, 50)
    }

if __name__ == "__main__":
    import uvicorn
    import asyncio
    uvicorn.run(app, host="0.0.0.0", port=8080)