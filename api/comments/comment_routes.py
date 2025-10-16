import uuid
from datetime import datetime
from flask import request, jsonify
from api import app
from schematics.models import Model
from schematics.types import StringType, DateTimeType, UUIDType
from schematics.exceptions import ModelConversionError, ModelValidationError


class Comment(Model):
    """Validation model for Comment"""
    id = UUIDType()
    post_id = StringType(required=True, max_length=100)
    content = StringType(required=True, min_length=1, max_length=2000)
    author = StringType(max_length=100)  # Optional author name
    created_at = DateTimeType()


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
        
        # Create comment data
        comment_data = {
            'id': uuid.uuid4(),
            'post_id': post_id,
            'content': content,
            'author': author,
            'created_at': datetime.utcnow()
        }
        
        # Validate the comment model
        comment = Comment(comment_data)
        comment.validate()
        
        app.logger.info(f'Comment added to post {post_id} - Author: {author or "Anonymous"}')
        
        # Return success response
        response_data = {
            'success': True,
            'message': 'Comment added successfully',
            'data': {
                'id': str(comment.id),
                'post_id': comment.post_id,
                'content': comment.content,
                'author': comment.author,
                'created_at': comment.created_at.isoformat() if comment.created_at else None
            }
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
        # In a real implementation, this would query a database
        # For now, return a placeholder response
        
        app.logger.info(f'Fetching comments for post {post_id}')
        
        # Placeholder response - in real implementation, query database
        response_data = {
            'success': True,
            'message': f'Comments for post {post_id}',
            'data': {
                'post_id': post_id,
                'comments': [],  # This would contain actual comments from database
                'total_comments': 0
            },
            'note': 'This is a placeholder - implement with actual database to store and retrieve comments'
        }
        
        return jsonify(response_data), 200
        
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
        # In a real implementation, this would query a database
        
        app.logger.info(f'Fetching comment {comment_id}')
        
        # Placeholder response - in real implementation, query database
        response_data = {
            'success': True,
            'message': f'Comment {comment_id}',
            'data': {
                'id': comment_id,
                'post_id': 'placeholder-post-id',
                'content': 'This would be the actual comment content from database',
                'author': 'Placeholder Author',
                'created_at': datetime.utcnow().isoformat()
            },
            'note': 'This is a placeholder - implement with actual database'
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
        # In a real implementation, this would delete from database
        
        app.logger.info(f'Deleting comment {comment_id}')
        
        # Placeholder response - in real implementation, delete from database
        response_data = {
            'success': True,
            'message': f'Comment {comment_id} deleted successfully',
            'note': 'This is a placeholder - implement with actual database'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        app.logger.exception(f'Unexpected error deleting comment {comment_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
