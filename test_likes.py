#!/usr/bin/env python
"""
Test script for the post like routes
"""

import requests
import json
import uuid

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_like_routes():
    """Test all like-related routes"""
    
    print("Testing Post Like Routes")
    print("=" * 50)
    
    # Generate test data
    post_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    print(f"Using test post_id: {post_id}")
    print(f"Using test user_id: {user_id}")
    print()
    
    # Test 1: Toggle Like (should like the post)
    print("Test 1: Like a post")
    print("-" * 30)
    
    like_data = {"user_id": user_id}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/posts/{post_id}/like",
            json=like_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 2: Check Like Status
    print("Test 2: Check like status")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/posts/{post_id}/like/status?user_id={user_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 3: Get Post Likes
    print("Test 3: Get all likes for post")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/posts/{post_id}/likes")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 4: Toggle Like Again (should unlike the post)
    print("Test 4: Unlike a post (toggle again)")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/posts/{post_id}/like",
            json=like_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 5: Get User Likes
    print("Test 5: Get all posts liked by user")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/likes/users/{user_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 6: Error Cases
    print("Test 6: Error cases")
    print("-" * 30)
    
    # Missing user_id
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/posts/{post_id}/like",
            json={},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Missing user_id - Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Missing user_id in query param
    try:
        response = requests.get(f"{BASE_URL}/api/v1/posts/{post_id}/like/status")
        print(f"Missing query user_id - Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_like_routes()
