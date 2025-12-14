import urllib.request
import urllib.parse
import json
import http.cookiejar

BASE_URL = "http://localhost:5000"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def register():
    print("Registering...")
    data = urllib.parse.urlencode({
        "username": "api_test_user_3",
        "password": "password"
    }).encode()
    
    try:
        req = urllib.request.Request(f"{BASE_URL}/register", data=data)
        with opener.open(req) as response:
            print(f"Register URL: {response.geturl()}") # Should be /discover
    except Exception as e:
        print(f"Register Failed: {e}")

def get_food_id():
    print("Searching for food...")
    try:
        with opener.open(f"{BASE_URL}/api/search?mood=happy") as response:
            data = json.loads(response.read().decode())
            if not data:
                print("No foods found!")
                return None
            food = data[0]
            print(f"Found: {food['name']} (ID: {food['id']})")
            return food['id']
    except Exception as e:
        print(f"Search Failed: {e}")
        return None

def toggle_favorite(food_id):
    print(f"Toggling favorite {food_id}...")
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/favorite/{food_id}", method='POST')
        with opener.open(req) as response:
            print(f"Response: {response.read().decode()}")
    except Exception as e:
        print(f"Toggle Failed: {e}")

def check_favorites(expected_id=None):
    print("Checking favorites...")
    try:
        with opener.open(f"{BASE_URL}/api/favorites") as response:
            data = json.loads(response.read().decode())
            ids = [f['id'] for f in data]
            print(f"Favorites: {ids}")
            
            if expected_id:
                if expected_id in ids:
                    print("SUCCESS: Food found.")
                else:
                    print("FAILURE: Food missing.")
            else:
                if not ids:
                    print("SUCCESS: Empty.")
                else:
                    print("FAILURE: Not empty.")
    except Exception as e:
        print(f"Check Failed: {e}")

if __name__ == '__main__':
    register()
    fid = get_food_id()
    if fid:
        toggle_favorite(fid)
        check_favorites(expected_id=fid)
        toggle_favorite(fid)
        check_favorites(expected_id=None)
