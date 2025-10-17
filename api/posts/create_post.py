import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request, jsonify
from api import app
from schematics.models import Model
from schematics.types import StringType, DateTimeType
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


class Post(Model):
    """Validation model for Post"""
    content = StringType(max_length=5000)  # Text content (optional)
    image_filename = StringType()  # Image filename (optional)
    created_at = DateTimeType()


@app.route('/posts', methods=['POST'])
def create_post():
    """Create a new post - can be text only, image only, or both"""
    
    try:
        # Get form data
        content = request.form.get('content', '').strip()
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
        
        # Create and validate the post model
        post_data = {
            'content': content if content else None,
            'image_filename': image_filename,
            'created_at': datetime.utcnow()
        }
        
        post = Post(post_data)
        post.validate()
        
        app.logger.info(f'Post created successfully - Content: {bool(content)}, Image: {bool(image_filename)}')
        
        # Return success response
        response_data = {
            'success': True,
            'message': 'Post created successfully',
            'data': {
                'id': str(uuid.uuid4()),  # In a real app, this would come from the database
                'content': post.content,
                'image_filename': post.image_filename,
                'created_at': post.created_at.isoformat() if post.created_at else None
            }
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
        
    except Exception as e:
        app.logger.exception(f'Unexpected error creating post: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post by ID (placeholder implementation)"""
    # This would normally query a database
    return jsonify({
        'success': True,
        'message': f'This would return post with ID: {post_id}',
        'note': 'This is a placeholder - implement with actual database'
    })


@app.route('/posts', methods=['GET'])
def get_all_posts():
    """Get all posts (placeholder implementation)"""
    # This would normally query a database
    return jsonify({
        'success': True,
        'message': 'This would return all posts',
        'note': 'This is a placeholder - implement with actual database'
    })
