"""MongoDB models for Posts, Comments, and Likes"""

from datetime import datetime
from bson import ObjectId
from schematics.models import Model
from schematics.types import StringType, DateTimeType, BooleanType, ListType
from schematics.exceptions import ModelConversionError, ModelValidationError
from api.database import get_db_manager, POSTS_COLLECTION, COMMENTS_COLLECTION, LIKES_COLLECTION
from api.database import serialize_doc, str_to_objectid, objectid_to_str
import logging

logger = logging.getLogger(__name__)


class PostModel(Model):
    """MongoDB model for Posts"""
    content = StringType(max_length=5000)  # Text content (optional)
    image_filename = StringType()  # Image filename (optional)
    author = StringType(max_length=100)  # Post author (optional)
    created_at = DateTimeType(default=datetime.utcnow)
    updated_at = DateTimeType()
    tags = ListType(StringType(max_length=50))  # Optional tags
    
    @classmethod
    def create(cls, data):
        """Create a new post in database"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(POSTS_COLLECTION)
            
            # Validate data
            post = cls(data)
            post.validate()
            
            # Prepare document for insertion
            doc = post.to_primitive()
            doc['created_at'] = datetime.utcnow()
            doc['updated_at'] = datetime.utcnow()
            
            # Insert into database
            result = collection.insert_one(doc)
            
            # Retrieve the created post
            created_post = collection.find_one({'_id': result.inserted_id})
            
            logger.info(f"Post created with ID: {result.inserted_id}")
            return serialize_doc(created_post)
            
        except (ModelConversionError, ModelValidationError) as e:
            logger.error(f"Post validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, post_id):
        """Get post by ID"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(POSTS_COLLECTION)
            
            # Convert string ID to ObjectId
            object_id = str_to_objectid(post_id)
            if not object_id:
                return None
            
            post = collection.find_one({'_id': object_id})
            return serialize_doc(post) if post else None
            
        except Exception as e:
            logger.error(f"Error fetching post {post_id}: {e}")
            raise
    
    @classmethod
    def get_all(cls, limit=50, skip=0):
        """Get all posts with pagination"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(POSTS_COLLECTION)
            
            cursor = collection.find().sort('created_at', -1).limit(limit).skip(skip)
            posts = list(cursor)
            
            return serialize_doc(posts)
            
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            raise
    
    @classmethod
    def delete_by_id(cls, post_id):
        """Delete post by ID"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(POSTS_COLLECTION)
            
            object_id = str_to_objectid(post_id)
            if not object_id:
                return False
            
            result = collection.delete_one({'_id': object_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting post {post_id}: {e}")
            raise


class CommentModel(Model):
    """MongoDB model for Comments"""
    post_id = StringType(required=True)  # Reference to post
    content = StringType(required=True, min_length=1, max_length=2000)
    author = StringType(max_length=100)  # Optional author name
    created_at = DateTimeType(default=datetime.utcnow)
    updated_at = DateTimeType()
    
    @classmethod
    def create(cls, data):
        """Create a new comment in database"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(COMMENTS_COLLECTION)
            
            # Validate data
            comment = cls(data)
            comment.validate()
            
            # Check if referenced post exists
            post_exists = PostModel.get_by_id(data['post_id'])
            if not post_exists:
                raise ValueError(f"Post with ID {data['post_id']} does not exist")
            
            # Prepare document for insertion
            doc = comment.to_primitive()
            doc['created_at'] = datetime.utcnow()
            doc['updated_at'] = datetime.utcnow()
            
            # Insert into database
            result = collection.insert_one(doc)
            
            # Retrieve the created comment
            created_comment = collection.find_one({'_id': result.inserted_id})
            
            logger.info(f"Comment created with ID: {result.inserted_id} for post: {data['post_id']}")
            return serialize_doc(created_comment)
            
        except (ModelConversionError, ModelValidationError) as e:
            logger.error(f"Comment validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            raise
    
    @classmethod
    def get_by_post_id(cls, post_id, limit=50, skip=0):
        """Get all comments for a specific post"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(COMMENTS_COLLECTION)
            
            cursor = collection.find({'post_id': post_id}).sort('created_at', -1).limit(limit).skip(skip)
            comments = list(cursor)
            
            return serialize_doc(comments)
            
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, comment_id):
        """Get comment by ID"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(COMMENTS_COLLECTION)
            
            object_id = str_to_objectid(comment_id)
            if not object_id:
                return None
            
            comment = collection.find_one({'_id': object_id})
            return serialize_doc(comment) if comment else None
            
        except Exception as e:
            logger.error(f"Error fetching comment {comment_id}: {e}")
            raise
    
    @classmethod
    def delete_by_id(cls, comment_id):
        """Delete comment by ID"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(COMMENTS_COLLECTION)
            
            object_id = str_to_objectid(comment_id)
            if not object_id:
                return False
            
            result = collection.delete_one({'_id': object_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting comment {comment_id}: {e}")
            raise
    
    @classmethod
    def count_by_post_id(cls, post_id):
        """Count comments for a specific post"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(COMMENTS_COLLECTION)
            
            return collection.count_documents({'post_id': post_id})
            
        except Exception as e:
            logger.error(f"Error counting comments for post {post_id}: {e}")
            raise


class LikeModel(Model):
    """MongoDB model for Likes"""
    post_id = StringType(required=True)  # Reference to post
    user_id = StringType(required=True)  # User who liked the post
    is_liked = BooleanType(default=True)  # True for like, False for unlike
    created_at = DateTimeType(default=datetime.utcnow)
    updated_at = DateTimeType()
    
    @classmethod
    def toggle_like(cls, data):
        """Toggle like/unlike for a post by a user"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(LIKES_COLLECTION)
            
            post_id = data['post_id']
            user_id = data['user_id']
            
            # Check if referenced post exists
            post_exists = PostModel.get_by_id(post_id)
            if not post_exists:
                raise ValueError(f"Post with ID {post_id} does not exist")
            
            # Check if like already exists
            existing_like = collection.find_one({
                'post_id': post_id,
                'user_id': user_id
            })
            
            if existing_like:
                # Toggle the like status
                new_status = not existing_like.get('is_liked', False)
                updated_doc = {
                    'is_liked': new_status,
                    'updated_at': datetime.utcnow()
                }
                
                collection.update_one(
                    {'_id': existing_like['_id']},
                    {'$set': updated_doc}
                )
                
                # Retrieve updated document
                updated_like = collection.find_one({'_id': existing_like['_id']})
                action = 'liked' if new_status else 'unliked'
                
            else:
                # Create new like
                like_data = {
                    'post_id': post_id,
                    'user_id': user_id,
                    'is_liked': True,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                
                result = collection.insert_one(like_data)
                updated_like = collection.find_one({'_id': result.inserted_id})
                action = 'liked'
            
            logger.info(f"User {user_id} {action} post {post_id}")
            return serialize_doc(updated_like), action
            
        except Exception as e:
            logger.error(f"Error toggling like for post {data.get('post_id')}: {e}")
            raise
    
    @classmethod
    def get_post_likes(cls, post_id):
        """Get all likes for a specific post"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(LIKES_COLLECTION)
            
            cursor = collection.find({
                'post_id': post_id,
                'is_liked': True
            }).sort('created_at', -1)
            
            likes = list(cursor)
            return serialize_doc(likes)
            
        except Exception as e:
            logger.error(f"Error fetching likes for post {post_id}: {e}")
            raise
    
    @classmethod
    def get_user_likes(cls, user_id):
        """Get all posts liked by a specific user"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(LIKES_COLLECTION)
            
            cursor = collection.find({
                'user_id': user_id,
                'is_liked': True
            }).sort('created_at', -1)
            
            likes = list(cursor)
            return serialize_doc(likes)
            
        except Exception as e:
            logger.error(f"Error fetching likes by user {user_id}: {e}")
            raise
    
    @classmethod
    def get_like_status(cls, post_id, user_id):
        """Check if a user has liked a specific post"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(LIKES_COLLECTION)
            
            like = collection.find_one({
                'post_id': post_id,
                'user_id': user_id
            })
            
            return like.get('is_liked', False) if like else False
            
        except Exception as e:
            logger.error(f"Error checking like status for post {post_id}, user {user_id}: {e}")
            raise
    
    @classmethod
    def count_post_likes(cls, post_id):
        """Count total likes for a specific post"""
        try:
            db_manager = get_db_manager()
            collection = db_manager.get_collection(LIKES_COLLECTION)
            
            return collection.count_documents({
                'post_id': post_id,
                'is_liked': True
            })
            
        except Exception as e:
            logger.error(f"Error counting likes for post {post_id}: {e}")
            raise
