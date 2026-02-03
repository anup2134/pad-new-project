import json
import urllib.request
import urllib.error
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/documents"

def test_endpoint(endpoint, data, description):
    url = f"{BASE_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data).encode('utf-8')
    
    print(f"\n--- Testing {description} ---")
    print(f"Input: {data['text'][:50]}...")
    
    try:
        req = urllib.request.Request(url, data=json_data, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("success"):
                output_key = "simplified_text" if endpoint == "simplify" else "summary"
                print(f"SUCCESS!")
                print(f"Output ({output_key}):")
                print("-" * 20)
                print(result.get(output_key))
                print("-" * 20)
                return True
            else:
                print(f"FAILED: API returned success=False")
                print(result)
                return False
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    # Test Data
    hindi_text = "डिस्लेक्सिया एक सीखने की अक्षमता है जो पढ़ने, लिखने और वर्तनी में कठिनाई पैदा करती है। यह बुद्धि से संबंधित नहीं है। डिस्लेक्सिया वाले लोग अक्सर अक्षरों और शब्दों को पहचानने में संघर्ष करते हैं। सही समर्थन और रणनीतियों के साथ, डिस्लेक्सिया वाले लोग स्कूल और जीवन में सफल हो सकते हैं।"
    
    english_text = "Dyslexia is a specific learning disability that is neurobiological in origin. It is characterized by difficulties with accurate and/or fluent word recognition and by poor spelling and decoding abilities."

    # 1. Test Hindi Simplification
    test_endpoint("simplify", {
        "text": hindi_text,
        "language": "hi",
        "dyslexia_type": "phonological"
    }, "Hindi Simplification (Phonological)")

    # 2. Test Hindi Summarization
    test_endpoint("summarize", {
        "text": hindi_text,
        "language": "hi",
        "dyslexia_type": "visual"
    }, "Hindi Summarization (Visual)")

    # 3. Test English Simplification
    test_endpoint("simplify", {
        "text": english_text,
        "language": "en",
        "dyslexia_type": "general"
    }, "English Simplification (General)")

if __name__ == "__main__":
    main()
