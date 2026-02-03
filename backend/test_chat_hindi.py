import json
import urllib.request
import urllib.error
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api/chat"

def test_chat(endpoint, data, description):
    url = f"{BASE_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data).encode('utf-8')
    
    print(f"\n--- Testing {description} ---")
    
    try:
        req = urllib.request.Request(url, data=json_data, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("success"):
                print(f"SUCCESS!")
                print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return result
            else:
                print(f"FAILED: API returned success=False")
                print(result)
                return None
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # 1. New Session
    print("\n--- Creating New Session ---")
    url = f"{BASE_URL}/new-session"
    print(f"Requesting URL: {url}")
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            session_id = result['session_id']
            print(f"Session ID: {session_id}")
    except Exception as e:
        print(f"Failed to create session: {e}")
        return

    # 2. Set Context (Hindi)
    hindi_doc = "डिस्लेक्सिया एक सीखने की अक्षमता है जो पढ़ने, लिखने और वर्तनी में कठिनाई पैदा करती है।"
    test_chat("set-context", {
        "session_id": session_id,
        "document_text": hindi_doc
    }, "Set Hindi Context")

    # 3. Ask Question (Hindi)
    test_chat("ask", {
        "session_id": session_id,
        "question": "डिस्लेक्सिया क्या है?",
        "language": "hi",
        "dyslexia_type": "general"
    }, "Ask Hindi Question")

if __name__ == "__main__":
    main()
