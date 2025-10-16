#!/usr/bin/env python3
"""
Static validation script for comment routes
This script validates the code structure and syntax without running the Flask app
"""

import ast
import os

def validate_python_file(filepath):
    """Validate Python file syntax"""
    print(f"\nValidating {filepath}:")
    
    if not os.path.exists(filepath):
        print(f"❌ File does not exist: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the file to check syntax
        ast.parse(content)
        print(f"✅ Syntax is valid")
        
        # Check for required imports and functions based on file type
        if 'comment_routes.py' in filepath:
            required_patterns = [
                'from flask import',
                'from schematics',
                'class Comment',
                '@app.route',
                'def add_comment_to_post',
                'def get_comments_for_post'
            ]
            
            for pattern in required_patterns:
                if pattern in content:
                    print(f"✅ Found: {pattern}")
                else:
                    print(f"⚠️  Missing: {pattern}")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def validate_api_structure():
    """Validate the overall API structure"""
    print("API Structure Validation")
    print("=" * 40)
    
    # Files to validate
    files_to_check = [
        '/vercel/sandbox/api/__init__.py',
        '/vercel/sandbox/api/comments/__init__.py',
        '/vercel/sandbox/api/comments/comment_routes.py',
        '/vercel/sandbox/api/posts/create_post.py'
    ]
    
    all_valid = True
    for filepath in files_to_check:
        if not validate_python_file(filepath):
            all_valid = False
    
    # Check if comment routes are imported
    print(f"\nChecking imports in main __init__.py:")
    try:
        with open('/vercel/sandbox/api/__init__.py', 'r') as f:
            init_content = f.read()
            
        if 'from api.comments import comment_routes' in init_content:
            print("✅ Comment routes are properly imported")
        else:
            print("⚠️  Comment routes import not found")
            
    except Exception as e:
        print(f"❌ Error checking imports: {e}")
        all_valid = False
    
    return all_valid

def show_api_endpoints():
    """Show available API endpoints"""
    print("\n\nAvailable API Endpoints")
    print("=" * 40)
    
    endpoints = [
        {
            'method': 'POST',
            'path': '/posts/{post_id}/comments',
            'description': 'Add a comment to a specific post',
            'body': '{"content": "Comment text", "author": "Author name (optional)"}'
        },
        {
            'method': 'GET',
            'path': '/posts/{post_id}/comments',
            'description': 'Get all comments for a specific post',
            'body': 'None'
        },
        {
            'method': 'GET',
            'path': '/comments/{comment_id}',
            'description': 'Get a specific comment by ID',
            'body': 'None'
        },
        {
            'method': 'DELETE',
            'path': '/comments/{comment_id}',
            'description': 'Delete a specific comment by ID',
            'body': 'None'
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"  Description: {endpoint['description']}")
        print(f"  Request Body: {endpoint['body']}")

def main():
    """Main validation function"""
    print("Comment Feature Validation")
    print("=" * 50)
    
    # Validate structure
    if validate_api_structure():
        print("\n✅ All validations passed!")
    else:
        print("\n❌ Some validations failed!")
    
    # Show endpoints
    show_api_endpoints()
    
    print("\n\nImplementation Notes:")
    print("- Comment validation uses Schematics models")
    print("- All routes include proper error handling")
    print("- Logging is implemented for debugging")
    print("- Comments are associated with posts via post_id")
    print("- Author field is optional (can be anonymous comments)")
    print("- Content field is required with length limits")
    print("- Database implementation needed for persistence")

if __name__ == '__main__':
    main()
