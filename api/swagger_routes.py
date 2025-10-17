"""
Swagger-documented API routes for Posts and Comments
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request
from flask_restx import Resource
from api.swagger_config import (
    api, posts_ns, comments_ns, likes_ns,
    post_model, post_response_model, comment_model, comment_response_model, 
    comment_input_model, comments_list_response_model, error_model, file_upload,
    like_model, like_input_model, like_response_model, likes_list_response_model,
    like_status_response_model
)
from schematics.models import Model
from schematics.types import StringType, DateTimeType, UUIDType
from schematics.exceptions import ModelConversionError, ModelValidationError

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Post(Model):
    """Validation model for Post"""
    content = StringType(max_length=5000)  # Text content (optional)
    image_filename = StringType()  # Image filename (optional)
    created_at = DateTimeType()


class Comment(Model):
    """Validation model for Comment"""
    id = UUIDType()
    post_id = StringType(required=True, max_length=100)
    content = StringType(required=True, min_length=1, max_length=2000)
    author = StringType(max_length=100)  # Optional author name
    created_at = DateTimeType()


@posts_ns.route('/')
class PostList(Resource):
    @posts_ns.doc('create_post')
    @posts_ns.expect(file_upload)
    @posts_ns.marshal_with(post_response_model, code=201, description='Post created successfully')
    @posts_ns.marshal_with(error_model, code=400, description='Bad request')
    @posts_ns.marshal_with(error_model, code=500, description='Internal server error')
    def post(self):
        """Create a new post - can be text only, image only, or both"""
        
        try:
            from api import app
            
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
                    file_path = os.path.join(UPLOAD_FOLDER, secure_name)
                    file.save(file_path)
                    image_filename = secure_name
                    
                    app.logger.info(f'Image saved: {secure_name}')
                elif file and file.filename != '' and not allowed_file(file.filename):
                    app.logger.warning(f'Invalid file type attempted: {file.filename}')
                    return {
                        'success': False,
                        'error': 'Invalid file type. Allowed types: png, jpg, jpeg, gif, webp'
                    }, 400
            
            # Validate that at least one type of content exists
            if not content and not image_filename:
                return {
                    'success': False,
                    'error': 'Post must contain either text content or an image'
                }, 400
            
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
            
            return response_data, 201
            
        except ModelConversionError as mce:
            return {
                'success': False,
                'error': 'Invalid data format',
                'details': mce.messages
            }, 400
            
        except ModelValidationError as mve:
            return {
                'success': False,
                'error': 'Validation failed',
                'details': mve.messages
            }, 400
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500

    @posts_ns.doc('get_all_posts')
    @posts_ns.marshal_with(post_response_model, code=200, description='Success')
    def get(self):
        """Get all posts (placeholder implementation)"""
        # This would normally query a database
        return {
            'success': True,
            'message': 'This would return all posts',
            'note': 'This is a placeholder - implement with actual database'
        }


@posts_ns.route('/<string:post_id>')
@posts_ns.param('post_id', 'The post identifier')
class PostDetail(Resource):
    @posts_ns.doc('get_post')
    @posts_ns.marshal_with(post_response_model, code=200, description='Success')
    @posts_ns.marshal_with(error_model, code=404, description='Post not found')
    def get(self, post_id):
        """Get a specific post by ID"""
        # This would normally query a database
        return {
            'success': True,
            'message': f'This would return post with ID: {post_id}',
            'note': 'This is a placeholder - implement with actual database'
        }


@posts_ns.route('/<string:post_id>/comments')
@posts_ns.param('post_id', 'The post identifier')
class PostComments(Resource):
    @posts_ns.doc('add_comment_to_post')
    @posts_ns.expect(comment_input_model)
    @posts_ns.marshal_with(comment_response_model, code=201, description='Comment added successfully')
    @posts_ns.marshal_with(error_model, code=400, description='Bad request')
    @posts_ns.marshal_with(error_model, code=500, description='Internal server error')
    def post(self, post_id):
        """Add a comment to a specific post"""
        
        try:
            from api import app
            
            # Get JSON data from request
            data = request.get_json()
            if not data:
                return {
                    'success': False,
                    'error': 'No data provided'
                }, 400
            
            # Extract comment data
            content = data.get('content', '').strip()
            author = data.get('author', '').strip() or None  # Optional field
            
            # Validate required fields
            if not content:
                return {
                    'success': False,
                    'error': 'Comment content is required'
                }, 400
            
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
            
            return response_data, 201
            
        except ModelConversionError as mce:
            return {
                'success': False,
                'error': 'Invalid data format',
                'details': mce.messages
            }, 400
            
        except ModelValidationError as mve:
            return {
                'success': False,
                'error': 'Validation failed',
                'details': mve.messages
            }, 400
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500

    @posts_ns.doc('get_comments_for_post')
    @posts_ns.marshal_with(comments_list_response_model, code=200, description='Success')
    @posts_ns.marshal_with(error_model, code=500, description='Internal server error')
    def get(self, post_id):
        """Get all comments for a specific post"""
        
        try:
            from api import app
            
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
            
            return response_data, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500


@comments_ns.route('/<string:comment_id>')
@comments_ns.param('comment_id', 'The comment identifier')
class CommentDetail(Resource):
    @comments_ns.doc('get_comment')
    @comments_ns.marshal_with(comment_response_model, code=200, description='Success')
    @comments_ns.marshal_with(error_model, code=404, description='Comment not found')
    def get(self, comment_id):
        """Get a specific comment by ID"""
        
        try:
            from api import app
            
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
            
            return response_data, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500

    @comments_ns.doc('delete_comment')
    @comments_ns.marshal_with(comment_response_model, code=200, description='Comment deleted successfully')
    @comments_ns.marshal_with(error_model, code=404, description='Comment not found')
    @comments_ns.marshal_with(error_model, code=500, description='Internal server error')
    def delete(self, comment_id):
        """Delete a specific comment by ID"""
        
        try:
            from api import app
            
            app.logger.info(f'Deleting comment {comment_id}')
            
            # Placeholder response - in real implementation, delete from database
            response_data = {
                'success': True,
                'message': f'Comment {comment_id} deleted successfully',
                'note': 'This is a placeholder - implement with actual database'
            }
            
            return response_data, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500


# Like Models for Swagger routes
from schematics.types import BooleanType

class Like(Model):
    """Validation model for Like"""
    id = UUIDType()
    post_id = StringType(required=True, max_length=100)
    user_id = StringType(required=True, max_length=100)
    is_liked = BooleanType(default=True)
    created_at = DateTimeType()
    updated_at = DateTimeType()


# In-memory storage for likes (in a real app, this would be a database)
likes_storage = {}


def get_like_key(post_id, user_id):
    """Generate a key for like storage"""
    return f"{post_id}:{user_id}"


@posts_ns.route('/<string:post_id>/like')
@posts_ns.param('post_id', 'The post identifier')
class PostLike(Resource):
    @posts_ns.doc('toggle_post_like')
    @posts_ns.expect(like_input_model)
    @posts_ns.marshal_with(like_response_model, code=200, description='Post like toggled successfully')
    @posts_ns.marshal_with(error_model, code=400, description='Bad request')
    @posts_ns.marshal_with(error_model, code=500, description='Internal server error')
    def post(self, post_id):
        """Toggle like/unlike for a specific post by a user"""
        
        try:
            from api import app
            
            # Get JSON data from request
            data = request.get_json()
            if not data:
                return {
                    'success': False,
                    'error': 'No data provided'
                }, 400
            
            # Extract user ID (required)
            user_id = data.get('user_id', '').strip()
            
            # Validate required fields
            if not user_id:
                return {
                    'success': False,
                    'error': 'User ID is required'
                }, 400
            
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
            
            return response_data, 200
            
        except ModelConversionError as mce:
            return {
                'success': False,
                'error': 'Invalid data format',
                'details': mce.messages
            }, 400
            
        except ModelValidationError as mve:
            return {
                'success': False,
                'error': 'Validation failed',
                'details': mve.messages
            }, 400
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500


@posts_ns.route('/<string:post_id>/likes')
@posts_ns.param('post_id', 'The post identifier')
class PostLikes(Resource):
    @posts_ns.doc('get_post_likes')
    @posts_ns.marshal_with(likes_list_response_model, code=200, description='Success')
    @posts_ns.marshal_with(error_model, code=500, description='Internal server error')
    def get(self, post_id):
        """Get all likes for a specific post"""
        
        try:
            from api import app
            
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
            
            return response_data, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500


@posts_ns.route('/<string:post_id>/like/status')
@posts_ns.param('post_id', 'The post identifier')
@posts_ns.param('user_id', 'The user identifier', _in='query')
class PostLikeStatus(Resource):
    @posts_ns.doc('get_user_like_status')
    @posts_ns.marshal_with(like_status_response_model, code=200, description='Success')
    @posts_ns.marshal_with(error_model, code=400, description='Bad request')
    @posts_ns.marshal_with(error_model, code=500, description='Internal server error')
    def get(self, post_id):
        """Check if a user has liked a specific post"""
        
        try:
            from api import app
            
            # Get user_id from query parameters
            user_id = request.args.get('user_id')
            
            if not user_id:
                return {
                    'success': False,
                    'error': 'User ID is required as query parameter'
                }, 400
            
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
            
            return response_data, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500


@likes_ns.route('/users/<string:user_id>')
@likes_ns.param('user_id', 'The user identifier')
class UserLikes(Resource):
    @likes_ns.doc('get_user_likes')
    @likes_ns.marshal_with(likes_list_response_model, code=200, description='Success')
    @likes_ns.marshal_with(error_model, code=500, description='Internal server error')
    def get(self, user_id):
        """Get all posts liked by a specific user"""
        
        try:
            from api import app
            
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
            
            return response_data, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Internal server error'
            }, 500
