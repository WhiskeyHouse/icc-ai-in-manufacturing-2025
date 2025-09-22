"""WHK Test Result Reporting
Formats test results for different output formats and integrations.
"""

import json
from java.util import Date
from com.inductiveautomation.ignition.common.util import LoggerEx

logger = LoggerEx.newBuilder().name("WHK.Testing.Reporting").build()


class TestReporter(object):
    """Base class for test result reporting."""
    
    def __init__(self, verbosity=1):
        self.verbosity = verbosity
        
    def format_results(self, test_result):
        """Format test results - to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement format_results")


class JSONReporter(TestReporter):
    """Reports test results in JSON format."""
    
    def format_results(self, test_result):
        """Format results as JSON."""
        summary = test_result.summary()
        
        formatted_failures = []
        for test, failure_info in test_result.failures:
            formatted_failures.append({
                'test': str(test),
                'type': 'failure',
                'message': failure_info.get('message', ''),
                'traceback': failure_info.get('traceback', ''),
                'exception_type': failure_info.get('type', 'AssertionError')
            })
            
        formatted_errors = []
        for test, error_info in test_result.errors:
            formatted_errors.append({
                'test': str(test),
                'type': 'error', 
                'message': error_info.get('message', ''),
                'traceback': error_info.get('traceback', ''),
                'exception_type': error_info.get('type', 'Exception')
            })
            
        formatted_skipped = []
        for test, reason in test_result.skipped:
            formatted_skipped.append({
                'test': str(test),
                'type': 'skipped',
                'reason': reason
            })
            
        return {
            'summary': summary,
            'failures': formatted_failures,
            'errors': formatted_errors,
            'skipped': formatted_skipped,
            'format': 'json',
            'timestamp': str(Date())
        }


class JUnitXMLReporter(TestReporter):
    """Reports test results in JUnit XML format for CI/CD integration."""
    
    def format_results(self, test_result):
        """Format results as JUnit XML."""
        summary = test_result.summary()
        
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        
        # Testsuite element
        xml_lines.append('<testsuite name="WHK.Tests" tests="{}" failures="{}" errors="{}" skipped="{}" time="{:.3f}">'.format(
            summary['tests_run'],
            summary['failures'], 
            summary['errors'],
            summary['skipped'],
            summary['duration_ms'] / 1000.0
        ))
        
        # Add testcase elements for all tests
        all_tests = []
        
        # Add failed tests
        for test, failure_info in test_result.failures:
            all_tests.append({
                'name': str(test),
                'status': 'failure',
                'details': failure_info
            })
            
        # Add error tests  
        for test, error_info in test_result.errors:
            all_tests.append({
                'name': str(test),
                'status': 'error',
                'details': error_info
            })
            
        # Add skipped tests
        for test, reason in test_result.skipped:
            all_tests.append({
                'name': str(test),
                'status': 'skipped',
                'details': {'reason': reason}
            })
            
        # Add successful tests (we need to infer these)
        successful_count = summary['tests_run'] - summary['failures'] - summary['errors'] - summary['skipped']
        for i in range(successful_count):
            all_tests.append({
                'name': 'test_{}'.format(i),
                'status': 'passed',
                'details': {}
            })
            
        # Generate testcase XML
        for test_info in all_tests:
            xml_lines.append('  <testcase name="{}" classname="WHK.Tests">'.format(
                self._escape_xml(test_info['name'])
            ))
            
            if test_info['status'] == 'failure':
                xml_lines.append('    <failure message="{}" type="{}">'.format(
                    self._escape_xml(test_info['details'].get('message', '')),
                    self._escape_xml(test_info['details'].get('type', 'AssertionError'))
                ))
                xml_lines.append('      {}'.format(self._escape_xml(test_info['details'].get('traceback', ''))))
                xml_lines.append('    </failure>')
                
            elif test_info['status'] == 'error':
                xml_lines.append('    <error message="{}" type="{}">'.format(
                    self._escape_xml(test_info['details'].get('message', '')),
                    self._escape_xml(test_info['details'].get('type', 'Exception'))
                ))
                xml_lines.append('      {}'.format(self._escape_xml(test_info['details'].get('traceback', ''))))
                xml_lines.append('    </error>')
                
            elif test_info['status'] == 'skipped':
                xml_lines.append('    <skipped message="{}"/>'.format(
                    self._escape_xml(test_info['details'].get('reason', 'Test skipped'))
                ))
                
            xml_lines.append('  </testcase>')
            
        xml_lines.append('</testsuite>')
        
        return {
            'xml': '\n'.join(xml_lines),
            'format': 'junit_xml',
            'summary': summary,
            'timestamp': str(Date())
        }
        
    def _escape_xml(self, text):
        """Escape XML special characters."""
        if not isinstance(text, str):
            text = str(text)
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))


class TextReporter(TestReporter):
    """Reports test results in human-readable text format."""
    
    def format_results(self, test_result):
        """Format results as readable text."""
        summary = test_result.summary()
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("WHK Test Results")
        lines.append("=" * 70)
        
        # Summary
        lines.append("")
        lines.append("Summary:")
        lines.append("  Tests run: {}".format(summary['tests_run']))
        lines.append("  Failures: {}".format(summary['failures']))
        lines.append("  Errors: {}".format(summary['errors']))
        lines.append("  Skipped: {}".format(summary['skipped']))
        lines.append("  Duration: {:.3f}s".format(summary['duration_ms'] / 1000.0))
        lines.append("  Success: {}".format(summary['success']))
        
        # Failures
        if test_result.failures:
            lines.append("")
            lines.append("FAILURES:")
            lines.append("-" * 50)
            for test, failure_info in test_result.failures:
                lines.append("")
                lines.append("FAIL: {}".format(test))
                lines.append("  Message: {}".format(failure_info.get('message', '')))
                if self.verbosity >= 2:
                    lines.append("  Traceback:")
                    lines.append("    {}".format(failure_info.get('traceback', '').replace('\n', '\n    ')))
                    
        # Errors  
        if test_result.errors:
            lines.append("")
            lines.append("ERRORS:")
            lines.append("-" * 50)
            for test, error_info in test_result.errors:
                lines.append("")
                lines.append("ERROR: {}".format(test))
                lines.append("  Message: {}".format(error_info.get('message', '')))
                if self.verbosity >= 2:
                    lines.append("  Traceback:")
                    lines.append("    {}".format(error_info.get('traceback', '').replace('\n', '\n    ')))
                    
        # Skipped
        if test_result.skipped:
            lines.append("")
            lines.append("SKIPPED:")
            lines.append("-" * 50)
            for test, reason in test_result.skipped:
                lines.append("SKIP: {} ({})".format(test, reason))
                
        # Footer
        lines.append("")
        lines.append("=" * 70)
        if summary['success']:
            lines.append("ALL TESTS PASSED")
        else:
            lines.append("SOME TESTS FAILED")
        lines.append("=" * 70)
        
        return {
            'text': '\n'.join(lines),
            'format': 'text',
            'summary': summary,
            'timestamp': str(Date())
        }


class HTMLReporter(TestReporter):
    """Reports test results in HTML format for web display."""
    
    def format_results(self, test_result):
        """Format results as HTML."""
        summary = test_result.summary()
        
        html_lines = ['<!DOCTYPE html>']
        html_lines.append('<html><head><title>WHK Test Results</title>')
        html_lines.append('<style>')
        html_lines.append('body { font-family: Arial, sans-serif; margin: 20px; }')
        html_lines.append('.summary { background: #f0f0f0; padding: 15px; border-radius: 5px; }')
        html_lines.append('.success { color: green; }')
        html_lines.append('.failure { color: red; }')
        html_lines.append('.error { color: orange; }')
        html_lines.append('.skipped { color: blue; }')
        html_lines.append('.details { margin-top: 20px; }')
        html_lines.append('.test-case { margin: 10px 0; padding: 10px; border-left: 3px solid #ddd; }')
        html_lines.append('.traceback { background: #f8f8f8; padding: 10px; font-family: monospace; }')
        html_lines.append('</style></head><body>')
        
        # Title and summary
        html_lines.append('<h1>WHK Test Results</h1>')
        html_lines.append('<div class="summary">')
        html_lines.append('<h2>Summary</h2>')
        html_lines.append('<p><strong>Tests run:</strong> {}</p>'.format(summary['tests_run']))
        html_lines.append('<p><strong>Failures:</strong> <span class="failure">{}</span></p>'.format(summary['failures']))
        html_lines.append('<p><strong>Errors:</strong> <span class="error">{}</span></p>'.format(summary['errors']))
        html_lines.append('<p><strong>Skipped:</strong> <span class="skipped">{}</span></p>'.format(summary['skipped']))
        html_lines.append('<p><strong>Duration:</strong> {:.3f}s</p>'.format(summary['duration_ms'] / 1000.0))
        
        if summary['success']:
            html_lines.append('<p><strong>Result:</strong> <span class="success">ALL TESTS PASSED</span></p>')
        else:
            html_lines.append('<p><strong>Result:</strong> <span class="failure">SOME TESTS FAILED</span></p>')
        html_lines.append('</div>')
        
        # Detailed results
        if test_result.failures or test_result.errors or test_result.skipped:
            html_lines.append('<div class="details">')
            
            if test_result.failures:
                html_lines.append('<h2>Failures</h2>')
                for test, failure_info in test_result.failures:
                    html_lines.append('<div class="test-case">')
                    html_lines.append('<h3 class="failure">FAIL: {}</h3>'.format(self._escape_html(str(test))))
                    html_lines.append('<p><strong>Message:</strong> {}</p>'.format(self._escape_html(failure_info.get('message', ''))))
                    if failure_info.get('traceback'):
                        html_lines.append('<div class="traceback">{}</div>'.format(self._escape_html(failure_info['traceback'])))
                    html_lines.append('</div>')
                    
            if test_result.errors:
                html_lines.append('<h2>Errors</h2>')
                for test, error_info in test_result.errors:
                    html_lines.append('<div class="test-case">')
                    html_lines.append('<h3 class="error">ERROR: {}</h3>'.format(self._escape_html(str(test))))
                    html_lines.append('<p><strong>Message:</strong> {}</p>'.format(self._escape_html(error_info.get('message', ''))))
                    if error_info.get('traceback'):
                        html_lines.append('<div class="traceback">{}</div>'.format(self._escape_html(error_info['traceback'])))
                    html_lines.append('</div>')
                    
            if test_result.skipped:
                html_lines.append('<h2>Skipped Tests</h2>')
                for test, reason in test_result.skipped:
                    html_lines.append('<div class="test-case">')
                    html_lines.append('<h3 class="skipped">SKIP: {}</h3>'.format(self._escape_html(str(test))))
                    html_lines.append('<p><strong>Reason:</strong> {}</p>'.format(self._escape_html(reason)))
                    html_lines.append('</div>')
                    
            html_lines.append('</div>')
            
        html_lines.append('<p><em>Generated at {}</em></p>'.format(Date()))
        html_lines.append('</body></html>')
        
        return {
            'html': '\n'.join(html_lines),
            'format': 'html',
            'summary': summary,
            'timestamp': str(Date())
        }
        
    def _escape_html(self, text):
        """Escape HTML special characters."""
        if not isinstance(text, str):
            text = str(text)
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;')
                   .replace('\n', '<br>'))


class ReportingManager(object):
    """Manages different test result reporters."""
    
    def __init__(self):
        self.reporters = {
            'json': JSONReporter,
            'junit_xml': JUnitXMLReporter,
            'text': TextReporter,
            'html': HTMLReporter
        }
        
    def format_results(self, test_result, format_type='json', verbosity=1):
        """Format test results in the specified format."""
        if format_type not in self.reporters:
            logger.error("Unknown report format: {}".format(format_type))
            format_type = 'json'
            
        reporter_class = self.reporters[format_type]
        reporter = reporter_class(verbosity=verbosity)
        
        try:
            return reporter.format_results(test_result)
        except Exception as e:
            logger.error("Failed to format results as {}: {}".format(format_type, e))
            # Fall back to JSON format
            fallback_reporter = JSONReporter(verbosity=verbosity)
            result = fallback_reporter.format_results(test_result)
            result['format_error'] = "Failed to format as {}: {}".format(format_type, str(e))
            return result
            
    def get_available_formats(self):
        """Get list of available report formats."""
        return list(self.reporters.keys())
        
    def add_reporter(self, name, reporter_class):
        """Add a custom reporter class."""
        self.reporters[name] = reporter_class


# Global reporting manager
reporting_manager = ReportingManager()


def format_test_results(test_result, format_type='json', verbosity=1):
    """Convenience function to format test results."""
    return reporting_manager.format_results(test_result, format_type, verbosity)


def get_report_formats():
    """Get available report formats."""
    return reporting_manager.get_available_formats()