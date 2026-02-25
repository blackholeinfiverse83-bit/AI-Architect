import json
import sys

def analyze_openapi(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        paths = data.get('paths', {})
        print(f"Total paths: {len(paths)}")
        
        auth_paths = []
        for path, methods in paths.items():
            if 'auth' in path.lower() or 'login' in path.lower() or 'signup' in path.lower():
                auth_paths.append(path)
                print(f"\nPath: {path}")
                for method, details in methods.items():
                    tags = details.get('tags', [])
                    print(f"  {method.upper()}: tags={tags}")
        
        if not auth_paths:
            print("\nNo authentication-related paths found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_openapi('live_openapi.json')
