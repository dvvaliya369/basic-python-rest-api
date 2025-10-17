"""MongoDB database configuration and connection setup"""

import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
import datetime

# Configure logging
logger = logging.getLogger(__name__)

# MongoDB Configuration
# In production, these should come from environment variables
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'social_media_db')

# Connection timeout settings
CONNECTION_TIMEOUT_MS = 5000
SERVER_SELECTION_TIMEOUT_MS = 5000

# Global MongoDB client and database instances
_client = None
_database = None


def get_mongodb_client():
    """
    Get MongoDB client instance (singleton pattern)
    """
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                MONGODB_URL,
                connectTimeoutMS=CONNECTION_TIMEOUT_MS,
                serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
                maxPoolSize=50,
                retryWrites=True
            )
            # Test connection
            _client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB at {MONGODB_URL}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            _client = None
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            _client = None
            raise
    
    return _client


def get_database():
    """
    Get database instance
    """
    global _database
    if _database is None:
        client = get_mongodb_client()
        _database = client[DATABASE_NAME]
        logger.info(f"Connected to database: {DATABASE_NAME}")
    
    return _database


def close_mongodb_connection():
    """
    Close MongoDB connection (useful for cleanup)
    """
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")


# Collection names
POSTS_COLLECTION = 'posts'
COMMENTS_COLLECTION = 'comments'
LIKES_COLLECTION = 'likes'


class DatabaseManager:
    """
    Database manager class to handle all database operations
    """
    
    def __init__(self):
        self.db = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and collections"""
        try:
            self.db = get_database()
            self._create_indexes()
            logger.info("Database manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary database indexes for better performance"""
        try:
            # Posts collection indexes
            posts_collection = self.db[POSTS_COLLECTION]
            posts_collection.create_index([("created_at", -1)])  # For sorting by creation time
            
            # Comments collection indexes
            comments_collection = self.db[COMMENTS_COLLECTION]
            comments_collection.create_index([("post_id", 1)])  # For finding comments by post
            comments_collection.create_index([("created_at", -1)])  # For sorting comments
            
            # Likes collection indexes
            likes_collection = self.db[LIKES_COLLECTION]
            likes_collection.create_index([("post_id", 1)])  # For finding likes by post
            likes_collection.create_index([("user_id", 1)])  # For finding likes by user
            likes_collection.create_index([("post_id", 1), ("user_id", 1)], unique=True)  # Unique constraint
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
            # Don't raise exception here as indexes are optional for basic functionality
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        if not self.db:
            self._initialize_database()
        return self.db[collection_name]
    
    def is_connected(self):
        """Check if database connection is active"""
        try:
            if self.db:
                self.db.command('ping')
                return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
        return False


# Utility functions for ObjectId handling
def str_to_objectid(id_string):
    """
    Convert string to ObjectId, return None if invalid
    """
    try:
        if isinstance(id_string, str) and len(id_string) == 24:
            return ObjectId(id_string)
    except Exception:
        pass
    return None


def objectid_to_str(object_id):
    """
    Convert ObjectId to string
    """
    return str(object_id) if object_id else None


def serialize_doc(doc):
    """
    Serialize a MongoDB document by converting ObjectId to string
    """
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif isinstance(value, datetime.datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = serialize_doc(value)
            elif isinstance(value, list):
                serialized[key] = serialize_doc(value)
            else:
                serialized[key] = value
        return serialized
    
    return doc


# Global database manager instance
db_manager = None


def get_db_manager():
    """
    Get database manager instance (singleton pattern)
    """
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager


# Health check function
def check_database_health():
    """
    Check database health and return status
    """
    try:
        manager = get_db_manager()
        if manager.is_connected():
            return {
                'status': 'healthy',
                'database': DATABASE_NAME,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }
        else:
            return {
                'status': 'unhealthy',
                'error': 'Database connection failed',
                'timestamp': datetime.datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
