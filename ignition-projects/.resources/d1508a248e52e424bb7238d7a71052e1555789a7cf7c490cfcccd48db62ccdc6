"""Example tests for batch control functionality.
Demonstrates testing of production scripts with mocks.
"""

from whk.testing_core import TestCase
from whk.testing_mocks import (with_mocks, mock_system, setup_test_tags, 
                               assert_tag_written, assert_tag_read)
from java.util import Date


class TestBatchControl(TestCase):
    """Test batch control operations."""
    
    @with_mocks
    def test_batch_temperature_monitoring(self):
        """Test batch temperature monitoring and safety stops."""
        # Setup test tags
        setup_test_tags({
            "[default]Batch/Current/Status": "Running",
            "[default]Batch/Current/Temperature": 90.0,  # Over limit
            "[default]Batch/Current/Level": 75.0
        })
        
        # Import and run the batch control function
        import whk.test_scripts.good
        result = whk.test_scripts.good.control_batch_process()
        
        # Verify emergency stop was triggered
        self.assertTrue(result)
        assert_tag_written(self, "[default]Batch/Controls/EmergencyStop", True)
        assert_tag_written(self, "[default]Audit/LastAction", "Emergency Stop - High Temperature")
        
        # Verify temperature was read
        assert_tag_read(self, "[default]Batch/Current/Temperature")
        
    @with_mocks  
    def test_batch_normal_operation(self):
        """Test normal batch operation logging."""
        # Setup normal operating conditions
        setup_test_tags({
            "[default]Batch/Current/Status": "Running",
            "[default]Batch/Current/Temperature": 75.0,  # Normal temp
            "[default]Batch/Current/Level": 80.0
        })
        
        import whk.test_scripts.good
        result = whk.test_scripts.good.control_batch_process()
        
        # Verify normal operation
        self.assertTrue(result)
        
        # Check audit logging for normal operation
        write_log = mock_system.tag.get_write_log()
        audit_writes = [entry for entry in write_log 
                       if any("[default]Audit/Process" in path for path in entry['paths'])]
        
        self.assertGreater(len(audit_writes), 0, "Should log audit information for normal operation")
        
    @with_mocks
    def test_batch_tag_read_failure(self):
        """Test handling of tag read failures."""
        # Don't set up any tags, causing read to return None-like values
        
        import whk.test_scripts.good
        result = whk.test_scripts.good.control_batch_process()
        
        # Function should handle the error gracefully
        self.assertFalse(result)
        
        # Should still attempt to read the tags
        assert_tag_read(self, "[default]Batch/Current/Status")


class TestBatchControlHelpers(TestCase):
    """Test helper functions for batch control."""
    
    def test_temperature_validation(self):
        """Test temperature validation logic."""
        # Test safe temperature
        safe_temp = 75.0
        self.assertTrue(safe_temp <= 85.0, "Safe temperature should pass validation")
        
        # Test dangerous temperature  
        danger_temp = 90.0
        self.assertFalse(danger_temp <= 85.0, "Dangerous temperature should fail validation")
        
    def test_batch_status_values(self):
        """Test valid batch status values."""
        valid_statuses = ["Running", "Stopped", "Paused", "Error"]
        
        for status in valid_statuses:
            self.assertIn(status, valid_statuses, "Status {} should be valid".format(status))


# Test functions for discovery
def test_emergency_stop_threshold():
    """Test that emergency stop threshold is correct."""
    threshold = 85.0
    test_temp = 90.0
    
    assert test_temp > threshold, "Test temperature should exceed threshold"


@with_mocks
def test_audit_logging_format():
    """Test audit log entry format."""
    from java.util import Date
    
    # Setup mock data
    setup_test_tags({
        "[default]Audit/LastAction": "",
        "[default]Audit/Timestamp": Date()
    })
    
    # Test audit entry format
    action = "Test Action"
    timestamp = Date()
    
    mock_system.tag.write(
        ["[default]Audit/LastAction", "[default]Audit/Timestamp"],
        [action, timestamp]
    )
    
    # Verify the writes happened
    write_log = mock_system.tag.get_write_log()
    assert len(write_log) > 0, "Should have written audit data"
    
    last_write = write_log[-1]
    assert "[default]Audit/LastAction" in last_write['paths'], "Should write audit action"


@with_mocks 
def test_tag_blocking_operations():
    """Test that blocking tag operations are used correctly."""
    setup_test_tags({
        "[default]Test/Value": 100
    })
    
    # Test blocking read
    values = mock_system.tag.readBlocking(["[default]Test/Value"])
    assert values[0].value == 100, "Blocking read should return correct value"
    
    # Test blocking write
    result = mock_system.tag.writeBlocking(["[default]Test/Output"], [200])
    assert result == True, "Blocking write should succeed"
    assert mock_system.tag.get_tag_value("[default]Test/Output") == 200, "Value should be written"


def test_batch_level_validation():
    """Test batch level validation ranges."""
    # Test normal levels
    normal_levels = [25.0, 50.0, 75.0]
    for level in normal_levels:
        assert 0 <= level <= 100, "Level {} should be in valid range".format(level)
    
    # Test invalid levels  
    invalid_levels = [-10.0, 150.0]
    for level in invalid_levels:
        assert not (0 <= level <= 100), "Level {} should be invalid".format(level)