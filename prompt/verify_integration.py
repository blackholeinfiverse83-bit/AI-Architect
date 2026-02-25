import requests
import json
import time

VIDEO_API_BASE_URL = 'http://127.0.0.1:9000'
USERNAME = 'test_user_integration'
PASSWORD = 'password123'

def test_health():
    print("Checking Video API Health...")
    try:
        response = requests.get(f"{VIDEO_API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def get_auth_token():
    print("\nRegistering/Logging in...")
    # Try login first
    login_url = f"{VIDEO_API_BASE_URL}/users/login"
    try:
        response = requests.post(login_url, data={'username': USERNAME, 'password': PASSWORD})
        if response.status_code == 200:
            print("Login successful")
            return response.json().get('access_token')
        
        # If login fails, try register
        print("Login failed, attempting registration...")
        register_url = f"{VIDEO_API_BASE_URL}/users/register"
        response = requests.post(register_url, json={
            'username': USERNAME,
            'password': PASSWORD,
            'email': f"{USERNAME}@example.com"
        })
        if response.status_code == 201:
            print("Registration successful")
            return response.json().get('access_token')
        else:
            print(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def test_generate_video(token):
    print("\nTesting Video Generation...")
    url = f"{VIDEO_API_BASE_URL}/generate-video"
    script_content = "AI Integration Test\nFast and Reliable\nDone by Antigravity"
    
    files = {
        'file': ('script.txt', script_content, 'text/plain')
    }
    data = {
        'title': 'Integration Test Video'
    }
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200, result.get('content_id')
    except Exception as e:
        print(f"Video generation failed: {e}")
        return False, None

def test_list_contents(token):
    print("\nTesting List Contents...")
    url = f"{VIDEO_API_BASE_URL}/contents"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        items = result.get('items', [])
        print(f"Found {len(items)} items")
        for item in items:
            print(f"- {item.get('title')} ({item.get('content_id')})")
        return response.status_code == 200, items
    except Exception as e:
        print(f"Listing contents failed: {e}")
        return False, []

def test_recommendations(token, content_id):
    if not content_id:
        print("\nSkipping recommendations test (no content_id)")
        return False
    
    print(f"\nTesting AI Recommendations for {content_id}...")
    url = f"{VIDEO_API_BASE_URL}/recommend-tags/{content_id}"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Recommended Tags: {result.get('recommended_tags')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Recommendations failed: {e}")
        return False

if __name__ == "__main__":
    if test_health():
        token = get_auth_token()
        if token:
            success, content_id = test_generate_video(token)
            test_list_contents(token)
            if success:
                test_recommendations(token, content_id)
        else:
            print("Failed to obtain auth token")
    else:
        print("Video API is not reachable. Skipping further tests.")
