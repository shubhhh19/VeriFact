import requests
import json

def test_validation_api():
    """Test the validation API endpoint with real news content"""
    
    url = "http://localhost:8000/api/v1/validation/validate"
    
    # Test data with real news content
    data = {
        "article_url": "https://example.com",
        "article_content": """
        Tech Giant Announces Major AI Breakthrough
        
        Silicon Valley's leading technology company has announced a revolutionary breakthrough in artificial intelligence that could transform how we interact with computers. According to company officials, the new AI system can understand and respond to natural language with unprecedented accuracy.
        
        The company reported that their new AI model achieved a 95% accuracy rate in language understanding tests, surpassing previous benchmarks by 15%. This development comes after three years of research and development involving over 500 engineers and scientists.
        
        Industry experts say this could lead to more advanced virtual assistants and improved machine translation services. The company plans to release the technology to developers next month, with consumer products expected by the end of the year.
        
        "This represents a significant step forward in AI capabilities," said Dr. Sarah Johnson, a leading AI researcher at Stanford University. "The implications for various industries are enormous."
        
        The announcement has already caused the company's stock price to rise by 8% in pre-market trading, with analysts predicting continued growth as the technology reaches the market.
        """,
        "validation_types": ["comprehensive"],
        "include_sources": True,
        "include_contradictions": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing validation API with real news content...")
        print(f"URL: {url}")
        print("Article content: Tech Giant Announces Major AI Breakthrough...")
        
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API test successful!")
            result = response.json()
            print(f"Validation ID: {result.get('validation_id')}")
            print(f"Status: {result.get('status')}")
            print(f"Score: {result.get('results', {}).get('score', 'N/A')}")
            print(f"Confidence: {result.get('results', {}).get('confidence', 'N/A')}")
            print(f"Claims found: {len(result.get('results', {}).get('claims', []))}")
            print(f"Sources found: {len(result.get('results', {}).get('sources', []))}")
            print(f"Contradictions found: {len(result.get('results', {}).get('contradictions', []))}")
            
            # Show first claim and source
            claims = result.get('results', {}).get('claims', [])
            sources = result.get('results', {}).get('sources', [])
            
            if claims:
                print(f"\nFirst claim: {claims[0].get('text', 'N/A')}")
            if sources:
                print(f"First source: {sources[0].get('name', 'N/A')} - {sources[0].get('title', 'N/A')}")
                
        else:
            print("❌ API test failed!")
            try:
                error_json = response.json()
                print(f"Error Response: {json.dumps(error_json, indent=2)}")
            except:
                print(f"Raw Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_validation_api() 