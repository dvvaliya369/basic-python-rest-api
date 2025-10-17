"""Default configuration settings"""

import os

DEBUG = True
TESTING = False
LOGGER_NAME = 'api-server'
LOG_FILENAME = 'api-server.log'

# MongoDB Configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'social_media_db')
