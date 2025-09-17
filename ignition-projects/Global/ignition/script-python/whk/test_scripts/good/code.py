"""WHK Production Script - Good Example.
Demonstrates proper error handling, logging, and FDA audit trail.
"""

import system
from com.inductiveautomation.ignition.common.util import LoggerEx
from java.util import Date

logger = LoggerEx.newBuilder().name("WHK.BatchControl").build()


def control_batch_process():
    """Monitor fermentation process with safety checks and audit logging."""
    try:
        batch_tags = [
            "[default]Batch/Current/Status",
            "[default]Batch/Current/Temperature",
            "[default]Batch/Current/Level"
        ]

        values = system.tag.readBlocking(batch_tags)
        if values is None:
            logger.error("Failed to read batch status tags")
            return False

        status, temperature, level = [value.value for value in values]

        if temperature > 85.0:
            logger.warn("High temperature detected: %s °F" % temperature)
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
                "Temperature exceeded safe limit: %s °F" % temperature
            ])

        if status == "Running":
            logger.info(
                "Batch running normally - Temp: %s °F, Level: %s%%" % (temperature, level)
            )
            system.tag.writeBlocking([
                "[default]Audit/Process/LastCheck",
                "[default]Audit/Process/Temperature",
                "[default]Audit/Process/Level"
            ], [Date(), temperature, level])

        return True

    except Exception as err:
        logger.error("Error in batch control: %s" % err)
        system.tag.writeBlocking([
            "[default]Batch/Status/Error",
            "[default]Audit/Error/Details"
        ], [True, str(err)])
        return False


if __name__ == "__main__":
    control_batch_process()
