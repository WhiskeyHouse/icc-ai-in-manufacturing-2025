"""Example tests for WHK Validation module.
Demonstrates testing of existing validation functionality.
"""

from whk.testing_core import TestCase
from whk.testing_mocks import with_mocks, mock_system, setup_test_responses
import whk.validation


class TestValidationRules(TestCase):
    """Test the WHK validation rules."""
    
    def test_script_validation_good(self):
        """Test validation of a well-formed script."""
        good_script = '''
try:
    logger = LoggerEx.newBuilder().name("WHK.Test").build()
    batch_data = system.tag.readBlocking("[default]Batch/Status")
    
    if batch_data.value == "Running":
        system.tag.writeBlocking("[default]Batch/LastCheck", Date())
        audit_log = "Batch check completed"
        logger.info(audit_log)
        
except Exception as e:
    logger.error("Error: {}".format(e))
'''
        
        result = whk.validation.validate_script_local(good_script)
        
        self.assertTrue(result['valid'])
        self.assertTrue(result['validation_passed'])
        self.assertEqual(len(result['issues']), 0)
        self.assertGreater(result['score'], 0.9)
        
    def test_script_validation_missing_error_handling(self):
        """Test validation catches missing error handling."""
        bad_script = '''
logger = LoggerEx.newBuilder().name("WHK.Test").build()
batch_data = system.tag.read("[default]Batch/Status")
logger.info("Batch status: {}".format(batch_data.value))
'''
        
        result = whk.validation.validate_script_local(bad_script)
        
        self.assertFalse(result['valid'])
        self.assertFalse(result['validation_passed'])
        self.assertGreater(len(result['issues']), 0)
        
        # Check for specific error
        error_found = False
        for issue in result['issues']:
            if issue['rule_id'] == 'SCRIPT-001':
                error_found = True
                break
        self.assertTrue(error_found, "Missing error handling rule not triggered")
        
    def test_script_validation_non_blocking_writes(self):
        """Test validation catches non-blocking tag writes."""
        bad_script = '''
try:
    system.tag.write("[default]Batch/Status", "Running")
    logger.info("Batch started")
except Exception as e:
    logger.error("Error: {}".format(e))
'''
        
        result = whk.validation.validate_script_local(bad_script)
        
        self.assertFalse(result['valid'])
        
        # Check for tag write rule
        write_error_found = False
        for issue in result['issues']:
            if issue['rule_id'] == 'SCRIPT-003':
                write_error_found = True
                break
        self.assertTrue(write_error_found, "Non-blocking write rule not triggered")
        
    def test_component_validation_missing_security(self):
        """Test component validation catches missing security."""
        component = {
            "type": "ia.display.button",
            "props": {
                "text": "Start Batch"
            },
            "events": {
                "onActionPerformed": {
                    "config": {
                        "script": "system.tag.write('[default]Batch/Start', True)"
                    }
                }
            },
            "meta": {}
        }
        
        result = whk.validation.validate_component_local(component)
        
        self.assertFalse(result['valid'])
        
        # Check for security rule
        security_error_found = False
        for issue in result['issues']:
            if issue['rule_id'] == 'COMP-001':
                security_error_found = True
                break
        self.assertTrue(security_error_found, "Missing security rule not triggered")


class TestValidationWithRulesEngine(TestCase):
    """Test validation with rules engine integration."""
    
    @with_mocks
    def test_rules_engine_fallback(self):
        """Test fallback to local validation when rules engine fails."""
        # Setup mock to simulate rules engine failure
        setup_test_responses({
            "http://host.docker.internal:8087/validate/script": None  # This will cause an exception
        })
        
        script = '''
try:
    logger = LoggerEx.newBuilder().name("WHK.Test").build()
    system.tag.writeBlocking("[default]Test", 123)
except Exception as e:
    logger.error("Error: {}".format(e))
'''
        
        result = whk.validation.validate_script_with_rules_engine(script, fallback_to_local=True)
        
        # Should succeed with local validation despite rules engine failure
        self.assertTrue(result['valid'])
        self.assertTrue(result.get('fallback_used', False))
        self.assertIsNotNone(result.get('rules_engine_error'))


class TestValidationSessions(TestCase):
    """Test validation session management."""
    
    def setUp(self):
        """Clean up validation sessions before each test."""
        whk.validation.reset_sessions()
        
    def test_create_validation_session(self):
        """Test creating a validation session."""
        script = "print('test')"
        validation_result = {'valid': True, 'score': 1.0}
        
        session = whk.validation.create_validation_session(
            'script', 
            script, 
            validation_result,
            context={'module': 'test'},
            metadata={'author': 'test_user'}
        )
        
        self.assertIsNotNone(session)
        self.assertEqual(session['type'], 'script')
        self.assertEqual(session['content'], script)
        self.assertEqual(session['validation_result'], validation_result)
        self.assertEqual(session['context']['module'], 'test')
        self.assertEqual(session['metadata']['author'], 'test_user')
        
    def test_list_validation_sessions(self):
        """Test listing validation sessions."""
        # Create a few sessions
        for i in range(3):
            whk.validation.create_validation_session(
                'script',
                'test_script_{}'.format(i),
                {'valid': True, 'score': 1.0}
            )
            
        sessions = whk.validation.list_validation_sessions()
        
        self.assertEqual(len(sessions), 3)
        for session in sessions:
            self.assertIn('session_id', session)
            self.assertIn('type', session)
            self.assertIn('status', session)
            
    def test_update_validation_session(self):
        """Test updating a validation session."""
        script = "print('test')"
        session = whk.validation.create_validation_session(
            'script', 
            script, 
            {'valid': True, 'score': 1.0}
        )
        
        session_id = session['session_id']
        
        updated = whk.validation.update_validation_session(
            session_id,
            script_updates="print('updated')",
            status='reviewed',
            notes='Updated by test',
            reviewer='test_user'
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated['script'], "print('updated')")
        self.assertEqual(updated['status'], 'reviewed')
        self.assertEqual(updated['last_reviewer'], 'test_user')
        self.assertGreater(len(updated['review_notes']), 0)


# Test functions for discovery
def test_simple_validation():
    """Simple test function for validation rules."""
    result = whk.validation.WHKValidationRules.validate_script("print('hello')", {})
    assert not result['valid'], "Script without error handling should fail validation"


def test_tag_config_normalization():
    """Test tag configuration result normalization."""
    mock_results = [
        {'path': '/test/tag1', 'status': 'Success'},
        {'path': '/test/tag2', 'status': 'Error', 'message': 'Duplicate tag'}
    ]
    
    normalized = whk.validation.normalize_tag_config_results(mock_results)
    
    assert len(normalized) == 2, "Should normalize all results"
    assert normalized[0]['path'] == '/test/tag1', "Should preserve path"
    assert normalized[1]['message'] == 'Duplicate tag', "Should preserve error message"


def test_service_health():
    """Test service health check."""
    health = whk.validation.get_service_health()
    
    assert 'status' in health, "Health check should include status"
    assert 'session_count' in health, "Health check should include session count"
    assert health['webdev_module'] == True, "WebDev module should be available"