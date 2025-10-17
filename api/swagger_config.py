"""
Swagger configuration for the API
"""

try:
    from flask_restx import Api, Resource, fields, Namespace
except ImportError:
    # If flask-restx is not available, use mock implementations
    from api.mock_flask_restx import MockApi as Api, MockResource as Resource, MockFields as fields, MockNamespace as Namespace

from flask import Blueprint

# Create a blueprint for API
api_blueprint = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Initialize Flask-RESTX API with the blueprint
try:
    api = Api(
        api_blueprint,
        version='1.0',
        title='Posts and Comments API',
        description='A simple API for managing posts and comments',
        doc='/docs/',
        prefix='/api/v1'
    )
except Exception:
    # Fallback for when flask-restx is not available
    api = Api(api_blueprint)

# Create namespaces for organizing the API
posts_ns = Namespace('posts', description='Post operations', path='/posts')
comments_ns = Namespace('comments', description='Comment operations', path='/comments')
likes_ns = Namespace('likes', description='Like operations', path='/likes')

# Register namespaces
api.add_namespace(posts_ns)
api.add_namespace(comments_ns)
api.add_namespace(likes_ns)

# Define Swagger models for request/response documentation

# Post Models
post_model = api.model('Post', {
    'id': fields.String(required=True, description='Post unique identifier'),
    'content': fields.String(description='Text content of the post (optional if image provided)'),
    'image_filename': fields.String(description='Filename of uploaded image (optional if content provided)'),
    'created_at': fields.DateTime(required=True, description='Creation timestamp')
})

post_input_model = api.model('PostInput', {
    'content': fields.String(description='Text content of the post (required if no image)')
})

post_response_model = api.model('PostResponse', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'message': fields.String(required=True, description='Response message'),
    'data': fields.Nested(post_model, description='Post data')
})

# Comment Models
comment_model = api.model('Comment', {
    'id': fields.String(required=True, description='Comment unique identifier'),
    'post_id': fields.String(required=True, description='ID of the post this comment belongs to'),
    'content': fields.String(required=True, description='Comment text content'),
    'author': fields.String(description='Comment author name (optional)'),
    'created_at': fields.DateTime(required=True, description='Creation timestamp')
})

comment_input_model = api.model('CommentInput', {
    'content': fields.String(required=True, description='Comment text content', min_length=1, max_length=2000),
    'author': fields.String(description='Comment author name (optional)', max_length=100)
})

comment_response_model = api.model('CommentResponse', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'message': fields.String(required=True, description='Response message'),
    'data': fields.Nested(comment_model, description='Comment data')
})

comments_list_response_model = api.model('CommentsListResponse', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'message': fields.String(required=True, description='Response message'),
    'data': fields.Raw(description='Comments list data')
})

# Error Models
error_model = api.model('Error', {
    'success': fields.Boolean(required=True, description='Operation success status (always false for errors)'),
    'error': fields.String(required=True, description='Error message'),
    'details': fields.Raw(description='Additional error details (optional)')
})

# Like Models
like_model = api.model('Like', {
    'id': fields.String(required=True, description='Like unique identifier'),
    'post_id': fields.String(required=True, description='ID of the post that was liked'),
    'user_id': fields.String(required=True, description='ID of the user who liked the post'),
    'is_liked': fields.Boolean(required=True, description='Like status (true for liked, false for unliked)'),
    'action': fields.String(description='Action performed (liked/unliked)'),
    'created_at': fields.DateTime(required=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp')
})

like_input_model = api.model('LikeInput', {
    'user_id': fields.String(required=True, description='ID of the user performing the like action', max_length=100)
})

like_response_model = api.model('LikeResponse', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'message': fields.String(required=True, description='Response message'),
    'data': fields.Nested(like_model, description='Like data')
})

likes_list_response_model = api.model('LikesListResponse', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'message': fields.String(required=True, description='Response message'),
    'data': fields.Raw(description='Likes list data')
})

like_status_model = api.model('LikeStatus', {
    'post_id': fields.String(required=True, description='Post ID'),
    'user_id': fields.String(required=True, description='User ID'),
    'is_liked': fields.Boolean(required=True, description='Whether the user has liked this post')
})

like_status_response_model = api.model('LikeStatusResponse', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'message': fields.String(required=True, description='Response message'),
    'data': fields.Nested(like_status_model, description='Like status data')
})

# File upload parser for posts with images
try:
    file_upload = api.parser()
    file_upload.add_argument('content', type=str, help='Text content of the post (optional if image provided)', location='form')
    file_upload.add_argument('image', type='file', help='Image file (optional if content provided)', location='files')
except AttributeError:
    # Fallback when parser is not available
    file_upload = None
