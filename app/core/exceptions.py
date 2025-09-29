"""
Simple exception classes
"""


class RajnitiError(Exception):
    """Base exception for Rajniti API"""

    def __init__(self, message, code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)
