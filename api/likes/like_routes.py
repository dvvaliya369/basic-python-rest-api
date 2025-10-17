import uuid
from datetime import datetime
from flask import request, jsonify
from api import app
from api.models import LikeModel
from schematics.exceptions import ModelConversionError, ModelValidationError


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
        
        # Toggle like using MongoDB model
        like_data = {
            'post_id': post_id,
            'user_id': user_id
        }
        
        updated_like, action = LikeModel.toggle_like(like_data)
        
        app.logger.info(f'User {user_id} {action} post {post_id}')
        
        # Return success response
        response_data = {
            'success': True,
            'message': f'Post {action} successfully',
            'data': {
                'like': updated_like,
                'action': action
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
        
    except ValueError as ve:
        app.logger.exception(f'Value error: {str(ve)}')
        return jsonify({
            'success': False,
            'error': str(ve)
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
        likes = LikeModel.get_post_likes(post_id)
        total_likes = LikeModel.count_post_likes(post_id)
        
        app.logger.info(f'Fetching likes for post {post_id} - Total: {total_likes}')
        
        response_data = {
            'success': True,
            'message': f'Likes for post {post_id}',
            'data': {
                'post_id': post_id,
                'total_likes': total_likes,
                'likes': likes
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
        is_liked = LikeModel.get_like_status(post_id, user_id)
        
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
        likes = LikeModel.get_user_likes(user_id)
        total_likes = len(likes)
        
        app.logger.info(f'Fetching likes by user {user_id} - Total: {total_likes}')
        
        response_data = {
            'success': True,
            'message': f'Posts liked by user {user_id}',
            'data': {
                'user_id': user_id,
                'total_likes': total_likes,
                'liked_posts': likes
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.exception(f'Unexpected error fetching likes by user {user_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
