import uuid
from datetime import datetime
from flask import request, jsonify
from api import app
from api.models import CommentModel
from schematics.exceptions import ModelConversionError, ModelValidationError


@app.route('/posts/<post_id>/comments', methods=['POST'])
def add_comment_to_post(post_id):
    """Add a comment to a specific post"""
    
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
        
        # Extract comment data
        content = data.get('content', '').strip()
        author = data.get('author', '').strip() or None  # Optional field
        
        # Validate required fields
        if not content:
            return jsonify({
                'success': False,
                'error': 'Comment content is required'
            }), 400
        
        # Create comment using MongoDB model
        comment_data = {
            'post_id': post_id,
            'content': content,
            'author': author
        }
        
        created_comment = CommentModel.create(comment_data)
        
        app.logger.info(f'Comment added to post {post_id} - Author: {author or "Anonymous"}')
        
        # Return success response
        response_data = {
            'success': True,
            'message': 'Comment added successfully',
            'data': created_comment
        }
        
        return jsonify(response_data), 201
        
    except ModelConversionError as mce:
        app.logger.exception(f'Model conversion error for comment: {mce.messages}')
        return jsonify({
            'success': False,
            'error': 'Invalid data format',
            'details': mce.messages
        }), 400
        
    except ModelValidationError as mve:
        app.logger.exception(f'Model validation error for comment: {mve.messages}')
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
        app.logger.exception(f'Unexpected error adding comment: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/posts/<post_id>/comments', methods=['GET'])
def get_comments_for_post(post_id):
    """Get all comments for a specific post"""
    
    try:
        # Get pagination parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Validate pagination parameters
        limit = min(limit, 100)  # Maximum 100 comments per request
        skip = max(skip, 0)  # Skip cannot be negative
        
        comments = CommentModel.get_by_post_id(post_id, limit=limit, skip=skip)
        total_comments = CommentModel.count_by_post_id(post_id)
        
        app.logger.info(f'Fetching comments for post {post_id} - Total: {total_comments}')
        
        response_data = {
            'success': True,
            'message': f'Comments for post {post_id}',
            'data': {
                'post_id': post_id,
                'comments': comments,
                'total_comments': total_comments,
                'limit': limit,
                'skip': skip,
                'count': len(comments)
            }
        }
        
        return jsonify(response_data), 200
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': 'Invalid pagination parameters'
        }), 400
        
    except Exception as e:
        app.logger.exception(f'Unexpected error fetching comments for post {post_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/comments/<comment_id>', methods=['GET'])
def get_comment(comment_id):
    """Get a specific comment by ID"""
    
    try:
        comment = CommentModel.get_by_id(comment_id)
        
        if not comment:
            return jsonify({
                'success': False,
                'error': 'Comment not found'
            }), 404
        
        app.logger.info(f'Fetching comment {comment_id}')
        
        response_data = {
            'success': True,
            'message': 'Comment retrieved successfully',
            'data': comment
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.exception(f'Unexpected error fetching comment {comment_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete a specific comment by ID"""
    
    try:
        deleted = CommentModel.delete_by_id(comment_id)
        
        if not deleted:
            return jsonify({
                'success': False,
                'error': 'Comment not found'
            }), 404
        
        app.logger.info(f'Comment {comment_id} deleted successfully')
        
        response_data = {
            'success': True,
            'message': 'Comment deleted successfully'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.exception(f'Unexpected error deleting comment {comment_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
