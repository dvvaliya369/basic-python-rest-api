#!/usr/bin/env python3
"""
Test script to validate the comment routes
This script tests the API endpoints without starting a server
"""

import json
from api import app

def test_comment_routes():
    """Test the comment API routes"""
    
    with app.test_client() as client:
        print("Testing Comment Routes")
        print("=" * 40)
        
        # Test 1: Add a comment to a post
        print("\n1. Testing POST /posts/test-post-123/comments")
        comment_data = {
            "content": "This is a test comment for the post",
            "author": "Test User"
        }
        
        response = client.post(
            '/posts/test-post-123/comments',
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")
        
        # Test 2: Add a comment without author
        print("\n2. Testing POST /posts/test-post-123/comments (no author)")
        comment_data_no_author = {
            "content": "This is an anonymous comment"
        }
        
        response = client.post(
            '/posts/test-post-123/comments',
            data=json.dumps(comment_data_no_author),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")
        
        # Test 3: Try to add empty comment (should fail)
        print("\n3. Testing POST /posts/test-post-123/comments (empty content - should fail)")
        empty_comment = {
            "content": "",
            "author": "Test User"
        }
        
        response = client.post(
            '/posts/test-post-123/comments',
            data=json.dumps(empty_comment),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")
        
        # Test 4: Get comments for a post
        print("\n4. Testing GET /posts/test-post-123/comments")
        response = client.get('/posts/test-post-123/comments')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")
        
        # Test 5: Get a specific comment
        print("\n5. Testing GET /comments/test-comment-123")
        response = client.get('/comments/test-comment-123')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")
        
        # Test 6: Delete a comment
        print("\n6. Testing DELETE /comments/test-comment-123")
        response = client.delete('/comments/test-comment-123')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")
        
        # Test 7: Try to add comment with wrong content type (should fail)
        print("\n7. Testing POST /posts/test-post-123/comments (wrong content type - should fail)")
        response = client.post(
            '/posts/test-post-123/comments',
            data="content=test&author=user",
            content_type='application/x-www-form-urlencoded'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")

if __name__ == '__main__':
    test_comment_routes()
