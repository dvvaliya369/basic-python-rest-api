# Python Flask REST API - Posts, Comments & Likes

A Flask REST API that provides endpoints for creating posts (text and/or images), adding comments to posts, and liking posts. This API demonstrates proper input validation, error handling, and structured responses with comprehensive Swagger documentation.

## 🚀 Features

### Posts API
- **Create posts** with text content, images, or both
- **File upload support** for images (PNG, JPG, JPEG, GIF, WebP)
- **Input validation** using Schematics models
- **Unique filename generation** for uploaded images
- **File size limits** (16MB maximum)

### Comments API  
- **Add comments** to specific posts
- **Optional author** field for comments
- **Content validation** (1-2000 characters)
- **CRUD operations** for comments (Create, Read, Delete)
- **JSON-based** request/response format

### Likes API
- **Like/Unlike posts** with toggle functionality
- **Track user likes** per post
- **Get like statistics** for posts
- **User like history** tracking
- **Check like status** for specific user-post combinations

### General Features
- **Swagger/OpenAPI documentation** available at `/api/v1/docs/`
- **Comprehensive error handling** with detailed error messages
- **Request logging** with rotating file logs
- **Input validation** using Schematics
- **Standardized JSON responses** for all endpoints
- **Test scripts** included for validation

## 📋 API Endpoints

### Posts Endpoints

#### Create Post
**POST** `/posts`

Create a new post with text content, image, or both.

**Request Format:** `multipart/form-data`

**Parameters:**
- `content` (optional, string): Text content up to 5000 characters
- `image` (optional, file): Image file (PNG, JPG, JPEG, GIF, WebP, max 16MB)

**Example Request:**
```bash
curl -X POST http://localhost:5000/posts \
  -F "content=This is my first post!" \
  -F "image=@/path/to/image.jpg"
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Post created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "This is my first post!",
    "image_filename": "550e8400-e29b-41d4-a716-446655440000.jpg",
    "created_at": "2023-10-16T15:30:45.123456"
  }
}
```

#### Get Post
**GET** `/posts/<post_id>`

Retrieve a specific post by ID (placeholder implementation).

#### Get All Posts  
**GET** `/posts`

Retrieve all posts (placeholder implementation).

### Comments Endpoints

#### Add Comment to Post
**POST** `/posts/<post_id>/comments`

Add a comment to a specific post.

**Request Format:** `application/json`

**Body Parameters:**
- `content` (required, string): Comment content (1-2000 characters)
- `author` (optional, string): Author name (max 100 characters)

**Example Request:**
```bash
curl -X POST http://localhost:5000/posts/my-post-id/comments \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great post! Thanks for sharing.",
    "author": "John Doe"
  }'
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Comment added successfully",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "post_id": "my-post-id",
    "content": "Great post! Thanks for sharing.",
    "author": "John Doe",
    "created_at": "2023-10-16T15:35:20.987654"
  }
}
```

#### Get Comments for Post
**GET** `/posts/<post_id>/comments`

Retrieve all comments for a specific post (placeholder implementation).

#### Get Specific Comment
**GET** `/comments/<comment_id>`

Retrieve a specific comment by ID (placeholder implementation).

#### Delete Comment
**DELETE** `/comments/<comment_id>`

Delete a specific comment by ID (placeholder implementation).

### Likes Endpoints

#### Like/Unlike Post
**POST** `/posts/<post_id>/like`

Toggle like status for a post by a user. If the user hasn't liked the post, it will be liked. If already liked, it will be unliked.

**Request Format:** `application/json`

**Body Parameters:**
- `user_id` (required, string): ID of the user performing the like action

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/posts/my-post-id/like \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Post liked successfully",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "post_id": "my-post-id",
    "user_id": "user123",
    "is_liked": true,
    "action": "liked",
    "created_at": "2023-10-16T15:40:15.123456",
    "updated_at": "2023-10-16T15:40:15.123456"
  }
}
```

#### Get Post Likes
**GET** `/posts/<post_id>/likes`

Get all likes for a specific post and total like count.

**Example Request:**
```bash
curl -X GET http://localhost:5000/api/v1/posts/my-post-id/likes
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Likes for post my-post-id",
  "data": {
    "post_id": "my-post-id",
    "total_likes": 3,
    "likes": [
      {
        "id": "like-id-1",
        "post_id": "my-post-id",
        "user_id": "user123",
        "is_liked": true,
        "created_at": "2023-10-16T15:40:15.123456",
        "updated_at": "2023-10-16T15:40:15.123456"
      }
    ]
  }
}
```

#### Check Like Status
**GET** `/posts/<post_id>/like/status?user_id=<user_id>`

Check if a specific user has liked a post.

**Query Parameters:**
- `user_id` (required): ID of the user to check like status for

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/v1/posts/my-post-id/like/status?user_id=user123"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Like status retrieved",
  "data": {
    "post_id": "my-post-id",
    "user_id": "user123",
    "is_liked": true
  }
}
```

#### Get User Likes
**GET** `/likes/users/<user_id>`

Get all posts liked by a specific user.

**Example Request:**
```bash
curl -X GET http://localhost:5000/api/v1/likes/users/user123
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Posts liked by user user123",
  "data": {
    "user_id": "user123",
    "total_likes": 5,
    "liked_posts": [
      {
        "id": "like-id-1",
        "post_id": "post-1",
        "user_id": "user123",
        "is_liked": true,
        "created_at": "2023-10-16T15:40:15.123456",
        "updated_at": "2023-10-16T15:40:15.123456"
      }
    ]
  }
}
```

## 📖 API Documentation

### Swagger/OpenAPI Documentation

The API includes comprehensive Swagger documentation available at:
```
http://localhost:5000/api/v1/docs/
```

The Swagger UI provides:
- **Interactive API testing** - Test endpoints directly from the browser
- **Request/Response examples** - See expected data formats
- **Parameter documentation** - Detailed parameter descriptions
- **Error response examples** - Common error scenarios
- **Model schemas** - Data structure definitions

### API Versioning

All API endpoints are versioned under `/api/v1/` to ensure backward compatibility:
- **Swagger docs**: `/api/v1/docs/`
- **Posts**: `/api/v1/posts/`
- **Comments**: `/api/v1/comments/`  
- **Likes**: `/api/v1/likes/`

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.7+
- pip package manager

### Dependencies
```bash
pip install Flask schematics Werkzeug
```

### Quick Start

1. **Clone or download the project:**
```bash
# Navigate to your project directory
cd /path/to/your/project
```

2. **Install dependencies:**
```bash
pip install Flask schematics Werkzeug
```

3. **Run the server:**
```bash
python server.py
```

4. **Test the API:**
```bash
# Run the comment validation tests
python test_comments.py

# Or test manually with curl
curl -X POST http://localhost:5000/posts \
  -F "content=Hello World!"
```

The server will start on `http://localhost:5000` by default.

## 🧪 Testing

The project includes test scripts to validate the API functionality:

### Run Like Tests
```bash
python test_likes.py
```

### Run Comment Tests
```bash
python test_comments.py
```

### Run Comment Validation
```bash
python validate_comments.py
```

### Manual Testing Examples

**Create a text-only post:**
```bash
curl -X POST http://localhost:5000/api/v1/posts \
  -F "content=This is a text-only post"
```

**Create an image-only post:**
```bash
curl -X POST http://localhost:5000/api/v1/posts \
  -F "image=@image.jpg"
```

**Add a comment:**
```bash
curl -X POST http://localhost:5000/api/v1/posts/test-post-123/comments \
  -H "Content-Type: application/json" \
  -d '{"content": "Nice post!", "author": "Alice"}'
```

**Like a post:**
```bash
curl -X POST http://localhost:5000/api/v1/posts/test-post-123/like \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

**Check like status:**
```bash
curl -X GET "http://localhost:5000/api/v1/posts/test-post-123/like/status?user_id=user123"
```

## 📁 Project Structure

```
.
├── server.py                 # Main server startup script
├── api/
│   ├── __init__.py          # Flask app initialization and route imports
│   ├── config.py            # Configuration settings
│   ├── swagger_config.py    # Swagger/OpenAPI configuration
│   ├── swagger_routes.py    # Swagger-documented API routes
│   ├── posts/
│   │   ├── __init__.py
│   │   └── create_post.py   # Post creation and management routes
│   ├── comments/
│   │   ├── __init__.py
│   │   └── comment_routes.py # Comment CRUD operations
│   ├── likes/
│   │   ├── __init__.py
│   │   └── like_routes.py   # Like/unlike operations
│   └── examples/            # Example routes and utilities
├── test_comments.py         # Comment API validation tests
├── test_likes.py           # Like API validation tests
├── validate_comments.py     # Additional comment validation
└── uploads/                 # Directory for uploaded images (auto-created)
```

## 🔧 Configuration

### App Configuration (`api/config.py`)
- `DEBUG = True` - Enable debug mode
- `TESTING = False` - Testing mode flag
- `LOG_FILENAME = 'api-server.log'` - Log file location

### Upload Configuration
- **Allowed file types:** PNG, JPG, JPEG, GIF, WebP
- **Max file size:** 16MB
- **Upload directory:** `uploads/` (auto-created)

## 🛡️ Error Handling

The API provides comprehensive error handling with standardized error responses:

### Common Error Response Format
```json
{
  "success": false,
  "error": "Error description",
  "details": {
    "field_name": ["Detailed validation error"]
  }
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created successfully
- `400` - Bad request (validation errors, invalid data)
- `404` - Not found
- `500` - Internal server error

### Example Error Responses

**Missing required data (400):**
```json
{
  "success": false,
  "error": "Post must contain either text content or an image"
}
```

**Invalid file type (400):**
```json
{
  "success": false,
  "error": "Invalid file type. Allowed types: png, jpg, jpeg, gif, webp"
}
```

**Validation error (400):**
```json
{
  "success": false,
  "error": "Validation failed",
  "details": {
    "content": ["String value is too long."]
  }
}
```

## 📝 Logging

The application uses rotating file logging:
- **Log file:** `api-server.log`
- **Max size:** 10MB per file
- **Backup files:** 5 rotating backups
- **Includes:** Request logs, error logs, and application events

## 🚧 Database Integration

**Note:** The current implementation uses placeholder responses for data retrieval operations. For production use, you'll need to:

1. **Choose a database** (PostgreSQL, MySQL, MongoDB, etc.)
2. **Install database connector** (e.g., `psycopg2` for PostgreSQL)
3. **Create database schemas** for posts and comments
4. **Implement actual CRUD operations** in place of placeholder responses
5. **Add database configuration** to `config.py`

## 🤝 Contributing

This is a basic REST API implementation demonstrating:
- Input validation with Schematics
- File upload handling
- Error handling and logging
- Test-driven development
- RESTful API design principles

Feel free to extend this implementation with database integration, authentication, and additional features as needed.

## 📄 License

This project is provided as an educational example. See LICENSE file for details.
