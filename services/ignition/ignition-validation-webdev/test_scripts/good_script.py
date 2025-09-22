# WHK Production Script - Good Example
# Gateway Timer Script for Batch Control

import system
from com.inductiveautomation.ignition.common.util import LoggerEx
from java.util import Date

# Initialize WHK logger
logger = LoggerEx.newBuilder().name("WHK.BatchControl").build()

def controlBatchProcess():
    """
    Control batch fermentation process with proper error handling and audit logging.
    Follows WHK production standards and FDA compliance requirements.
    """
    try:
        # Read batch status
        batch_tags = [
            "[default]Batch/Current/Status",
            "[default]Batch/Current/Temperature", 
            "[default]Batch/Current/Level"
        ]
        
        values = system.tag.readBlocking(batch_tags)
        
        if values is None:
            logger.error("Failed to read batch status tags")
            return
            
        status, temperature, level = [v.value for v in values]
        
        # Safety checks
        if temperature > 85.0:
            logger.warn("High temperature detected: {} °F".format(temperature))
            
            # Safe shutdown with audit logging
            system.tag.writeBlocking([
                "[default]Batch/Controls/EmergencyStop",
                "[default]Audit/LastAction",
                "[default]Audit/Operator", 
                "[default]Audit/Timestamp",
                "[default]Audit/Reason"
            ], [
                True,
                "Emergency Stop - High Temperature",
                system.security.getUserName(),
                Date(),
                "Temperature exceeded safe limit: {} °F".format(temperature)
            ])
            
        # Normal batch monitoring with audit trail
        if status == "Running":
            logger.info("Batch process running normally - Temp: {} °F, Level: {}%".format(
                temperature, level))
            
            # Update audit log for FDA compliance
            system.tag.writeBlocking([
                "[default]Audit/Process/LastCheck",
                "[default]Audit/Process/Temperature",
                "[default]Audit/Process/Level"
            ], [Date(), temperature, level])
                
    except Exception as e:
        logger.error("Error in batch control: {}".format(str(e)))
        
        # Set error status with audit trail
        system.tag.writeBlocking([
            "[default]Batch/Status/Error",
            "[default]Audit/Error/Details"
        ], [True, str(e)])

# Execute batch control
controlBatchProcess()