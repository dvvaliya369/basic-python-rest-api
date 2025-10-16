import uuid
from datetime import datetime
from flask import request, jsonify
from api import app
from schematics.models import Model
from schematics.types import StringType, DateTimeType, UUIDType, BooleanType
from schematics.exceptions import ModelConversionError, ModelValidationError


class Like(Model):
    """Validation model for Like"""
    id = UUIDType()
    post_id = StringType(required=True, max_length=100)
    user_id = StringType(required=True, max_length=100)  # User who liked the post
    is_liked = BooleanType(default=True)  # True for like, False for unlike
    created_at = DateTimeType()
    updated_at = DateTimeType()


# In-memory storage for likes (in a real app, this would be a database)
likes_storage = {}


def get_like_key(post_id, user_id):
    """Generate a key for like storage"""
    return f"{post_id}:{user_id}"


@app.route('/posts/<post_id>/like', methods=['POST'])
def toggle_post_like(post_id):
    """Toggle like/unlike for a specific post by a user"""
    
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract user ID (required)
        user_id = data.get('user_id', '').strip()
        
        # Validate required fields
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID is required'
            }), 400
        
        # Check if user has already liked this post
        like_key = get_like_key(post_id, user_id)
        existing_like = likes_storage.get(like_key)
        
        if existing_like and existing_like.get('is_liked'):
            # User has already liked this post - unlike it
            like_data = {
                'id': existing_like['id'],
                'post_id': post_id,
                'user_id': user_id,
                'is_liked': False,
                'created_at': existing_like['created_at'],
                'updated_at': datetime.utcnow()
            }
            action = 'unliked'
        else:
            # User hasn't liked this post or had unliked it - like it
            like_data = {
                'id': uuid.uuid4(),
                'post_id': post_id,
                'user_id': user_id,
                'is_liked': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            action = 'liked'
        
        # Validate the like model
        like = Like(like_data)
        like.validate()
        
        # Store the like (update or create)
        likes_storage[like_key] = {
            'id': str(like.id),
            'post_id': like.post_id,
            'user_id': like.user_id,
            'is_liked': like.is_liked,
            'created_at': like.created_at,
            'updated_at': like.updated_at
        }
        
        app.logger.info(f'User {user_id} {action} post {post_id}')
        
        # Return success response
        response_data = {
            'success': True,
            'message': f'Post {action} successfully',
            'data': {
                'id': str(like.id),
                'post_id': like.post_id,
                'user_id': like.user_id,
                'is_liked': like.is_liked,
                'action': action,
                'created_at': like.created_at.isoformat() if like.created_at else None,
                'updated_at': like.updated_at.isoformat() if like.updated_at else None
            }
        }
        
        return jsonify(response_data), 200
        
    except ModelConversionError as mce:
        app.logger.exception(f'Model conversion error for like: {mce.messages}')
        return jsonify({
            'success': False,
            'error': 'Invalid data format',
            'details': mce.messages
        }), 400
        
    except ModelValidationError as mve:
        app.logger.exception(f'Model validation error for like: {mve.messages}')
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': mve.messages
        }), 400
        
    except Exception as e:
        app.logger.exception(f'Unexpected error toggling like for post {post_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/posts/<post_id>/likes', methods=['GET'])
def get_post_likes(post_id):
    """Get all likes for a specific post"""
    
    try:
        # Filter likes for this post
        post_likes = [
            like for like in likes_storage.values() 
            if like['post_id'] == post_id and like['is_liked']
        ]
        
        # Count total likes
        total_likes = len(post_likes)
        
        app.logger.info(f'Fetching likes for post {post_id} - Total: {total_likes}')
        
        response_data = {
            'success': True,
            'message': f'Likes for post {post_id}',
            'data': {
                'post_id': post_id,
                'total_likes': total_likes,
                'likes': post_likes
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.exception(f'Unexpected error fetching likes for post {post_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/posts/<post_id>/like/status', methods=['GET'])
def get_user_like_status(post_id):
    """Check if a user has liked a specific post"""
    
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID is required as query parameter'
            }), 400
        
        # Check like status
        like_key = get_like_key(post_id, user_id)
        existing_like = likes_storage.get(like_key)
        
        is_liked = existing_like and existing_like.get('is_liked', False)
        
        app.logger.info(f'Checking like status for user {user_id} on post {post_id}: {is_liked}')
        
        response_data = {
            'success': True,
            'message': 'Like status retrieved',
            'data': {
                'post_id': post_id,
                'user_id': user_id,
                'is_liked': is_liked
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.exception(f'Unexpected error checking like status for post {post_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/users/<user_id>/likes', methods=['GET'])
def get_user_likes(user_id):
    """Get all posts liked by a specific user"""
    
    try:
        # Filter likes for this user
        user_likes = [
            like for like in likes_storage.values() 
            if like['user_id'] == user_id and like['is_liked']
        ]
        
        # Count total likes by user
        total_likes = len(user_likes)
        
        app.logger.info(f'Fetching likes by user {user_id} - Total: {total_likes}')
        
        response_data = {
            'success': True,
            'message': f'Posts liked by user {user_id}',
            'data': {
                'user_id': user_id,
                'total_likes': total_likes,
                'liked_posts': user_likes
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.exception(f'Unexpected error fetching likes by user {user_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
