import json
import urllib.request
import urllib.error
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api/documents"

def test_endpoint(endpoint, data, description):
    url = f"{BASE_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data).encode('utf-8')
    
    print(f"\n--- Testing {description} ---")
    
    try:
        req = urllib.request.Request(url, data=json_data, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("success"):
                output_key = "simplified_text" if endpoint == "simplify" else "summary"
                output = result.get(output_key)
                print(f"SUCCESS!")
                print(f"Original Length: {len(data['text'])}")
                print(f"Result Length: {len(output)}")
                print(f"Ratio: {len(output)/len(data['text']):.2f}")
                print(f"Output preview: {output[:100]}...")
                return output
            else:
                print(f"FAILED: {result}")
                return None
                
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    text = "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities. This chemical energy is stored in carbohydrate molecules, such as sugars and starches, which are synthesized from carbon dioxide and water."

    # 1. Test Simplification (should be similar length)
    simplified = test_endpoint("simplify", {
        "text": text,
        "language": "en",
        "dyslexia_type": "general"
    }, "English Simplification")

    # 2. Test Summarization (should be shorter)
    summarized = test_endpoint("summarize", {
        "text": text,
        "language": "en",
        "dyslexia_type": "general"
    }, "English Summarization")

if __name__ == "__main__":
    main()
