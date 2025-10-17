import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request, jsonify
from api import app
from api.models import PostModel
from schematics.exceptions import ModelConversionError, ModelValidationError


# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/posts', methods=['POST'])
def create_post():
    """Create a new post - can be text only, image only, or both"""
    
    try:
        # Get form data
        content = request.form.get('content', '').strip()
        author = request.form.get('author', '').strip() or None
        image_filename = None
        
        # Handle file upload if present
        if 'image' in request.files:
            file = request.files['image']
            # If user does not select file, browser submits empty part without filename
            if file and file.filename != '' and allowed_file(file.filename):
                # Generate unique filename
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                secure_name = secure_filename(unique_filename)
                
                # Save file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
                file.save(file_path)
                image_filename = secure_name
                
                app.logger.info(f'Image saved: {secure_name}')
            elif file and file.filename != '' and not allowed_file(file.filename):
                app.logger.warning(f'Invalid file type attempted: {file.filename}')
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type. Allowed types: png, jpg, jpeg, gif, webp'
                }), 400
        
        # Validate that at least one type of content exists
        if not content and not image_filename:
            return jsonify({
                'success': False,
                'error': 'Post must contain either text content or an image'
            }), 400
        
        # Create post using MongoDB model
        post_data = {
            'content': content if content else None,
            'image_filename': image_filename,
            'author': author
        }
        
        created_post = PostModel.create(post_data)
        
        app.logger.info(f'Post created successfully in MongoDB - ID: {created_post["_id"]}')
        
        # Return success response
        response_data = {
            'success': True,
            'message': 'Post created successfully',
            'data': created_post
        }
        
        return jsonify(response_data), 201
        
    except ModelConversionError as mce:
        app.logger.exception(f'Model conversion error: {mce.messages}')
        return jsonify({
            'success': False,
            'error': 'Invalid data format',
            'details': mce.messages
        }), 400
        
    except ModelValidationError as mve:
        app.logger.exception(f'Model validation error: {mve.messages}')
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
        app.logger.exception(f'Unexpected error creating post: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post by ID"""
    try:
        post = PostModel.get_by_id(post_id)
        
        if not post:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Post retrieved successfully',
            'data': post
        }), 200
        
    except Exception as e:
        app.logger.exception(f'Error retrieving post {post_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/posts', methods=['GET'])
def get_all_posts():
    """Get all posts with pagination"""
    try:
        # Get pagination parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Validate pagination parameters
        limit = min(limit, 100)  # Maximum 100 posts per request
        skip = max(skip, 0)  # Skip cannot be negative
        
        posts = PostModel.get_all(limit=limit, skip=skip)
        
        return jsonify({
            'success': True,
            'message': 'Posts retrieved successfully',
            'data': {
                'posts': posts,
                'limit': limit,
                'skip': skip,
                'count': len(posts)
            }
        }), 200
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': 'Invalid pagination parameters'
        }), 400
        
    except Exception as e:
        app.logger.exception(f'Error retrieving posts: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a specific post by ID"""
    try:
        deleted = PostModel.delete_by_id(post_id)
        
        if not deleted:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Post deleted successfully'
        }), 200
        
    except Exception as e:
        app.logger.exception(f'Error deleting post {post_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
