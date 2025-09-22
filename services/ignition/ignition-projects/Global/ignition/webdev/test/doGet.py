"""
Simple WebDev test endpoint
"""

def doGet(request, session):
    """Simple test endpoint"""
    return {
        'json': {
            'message': 'Hello from WebDev!',
            'project': 'Global',
            'status': 'working'
        }
    }