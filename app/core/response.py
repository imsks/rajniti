"""
Simple response utilities
"""

from flask import jsonify


def success_response(data, message="Success", total=None):
    """Create standardized success response"""
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    
    if total is not None:
        response['total'] = total
    
    return jsonify(response)


def error_response(message, code=500):
    """Create standardized error response"""
    response = {
        'success': False,
        'error': message
    }
    
    return jsonify(response), code
