import os

# Configuration settings
AWS_REGION = os.getenv('AWS_REGION', 'eu-north-1')
MAX_CONTENT_LENGTH = 100000  # Maximum characters to process
RATE_LIMIT = 10  # Requests per minute 