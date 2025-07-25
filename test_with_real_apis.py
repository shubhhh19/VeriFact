#!/usr/bin/env python3
"""
Test script to demonstrate VeriFact with real API keys
"""

import os
import requests
import json

def check_api_keys():
    """Check if API keys are configured"""
    gemini_key = os.getenv("GEMINI_API_KEY")
    news_key = os.getenv("NEWS_API_KEY")
    
    print("🔑 API Key Status:")
    print(f"   Gemini API Key: {'✅ Configured' if gemini_key and gemini_key != 'your_gemini_api_key_here' else '❌ Not configured'}")
    print(f"   News API Key: {'✅ Configured' if news_key and news_key != 'your_news_api_key_here' else '❌ Not configured'}")
    
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("\n📝 To get your Gemini API key:")
        print("   1. Go to: https://makersuite.google.com/app/apikey")
        print("   2. Create a new API key")
        print("   3. Set it as: $env:GEMINI_API_KEY='your_key_here'")
    
    if not news_key or news_key == 'your_news_api_key_here':
        print("\n📝 To get your News API key:")
        print("   1. Go to: https://newsapi.org/register")
        print("   2. Register for a free account")
        print("   3. Set it as: $env:NEWS_API_KEY='your_key_here'")
    
    return bool(gemini_key and news_key and 
                gemini_key != 'your_gemini_api_key_here' and 
                news_key != 'your_news_api_key_here')

def test_validation_with_real_apis():
    """Test the validation API with real news content"""
    
    if not check_api_keys():
        print("\n❌ Please configure your API keys first!")
        print("   See API_KEYS_SETUP.md for detailed instructions")
        return
    
    url = "http://localhost:8000/api/v1/validation/validate"
    
    # Real news article content for testing
    test_article = """
    NASA Announces Discovery of New Exoplanet
    
    NASA scientists have announced the discovery of a potentially habitable exoplanet located 40 light-years from Earth. The planet, named TOI-700 d, is approximately 1.2 times the size of Earth and orbits within the habitable zone of its star.
    
    According to NASA's Transiting Exoplanet Survey Satellite (TESS), the planet receives about 86% of the energy that Earth receives from the Sun. This makes it one of the most promising candidates for potentially habitable worlds discovered to date.
    
    "This is an exciting discovery," said Dr. Emily Gilbert, a researcher at NASA's Jet Propulsion Laboratory. "The planet's size and location suggest it could have liquid water on its surface, which is essential for life as we know it."
    
    The discovery was made using data from TESS, which has been scanning the sky for planets since 2018. The mission has already identified over 2,000 candidate exoplanets, with TOI-700 d being one of the most significant finds.
    
    Scientists estimate that the planet's surface temperature could range from -3 to 30 degrees Celsius, making it potentially suitable for life. However, further observations with more powerful telescopes will be needed to determine if the planet has an atmosphere and what gases it contains.
    """
    
    data = {
        "article_url": "https://example.com/nasa-exoplanet-discovery",
        "article_content": test_article,
        "validation_types": ["comprehensive"],
        "include_sources": True,
        "include_contradictions": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("\n🧪 Testing VeriFact with real APIs...")
        print("   This will use Gemini AI to extract claims and News API to verify sources")
        
        response = requests.post(url, json=data, headers=headers, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Validation completed successfully!")
            print(f"   Validation ID: {result.get('validation_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Credibility Score: {result.get('results', {}).get('score', 'N/A'):.2f}")
            print(f"   Confidence: {result.get('results', {}).get('confidence', 'N/A'):.2f}")
            
            # Show extracted claims
            claims = result.get('results', {}).get('claims', [])
            print(f"\n📋 Extracted Claims ({len(claims)}):")
            for i, claim in enumerate(claims[:3], 1):
                print(f"   {i}. {claim.get('text', 'N/A')[:100]}...")
                print(f"      Confidence: {claim.get('confidence', 'N/A'):.2f}")
            
            # Show verified sources
            sources = result.get('results', {}).get('sources', [])
            print(f"\n🔍 Verified Sources ({len(sources)}):")
            for i, source in enumerate(sources[:3], 1):
                print(f"   {i}. {source.get('name', 'N/A')}")
                print(f"      Title: {source.get('title', 'N/A')[:80]}...")
                print(f"      Reliability: {source.get('reliability', 'N/A'):.2f}")
            
            # Show contradictions
            contradictions = result.get('results', {}).get('contradictions', [])
            if contradictions:
                print(f"\n⚠️  Contradictions Found ({len(contradictions)}):")
                for i, contradiction in enumerate(contradictions, 1):
                    print(f"   {i}. {contradiction.get('description', 'N/A')[:80]}...")
            else:
                print(f"\n✅ No contradictions detected")
            
            print(f"\n🎯 Analysis Summary:")
            if result.get('results', {}).get('score', 0) > 0.7:
                print("   This article appears to be highly credible")
            elif result.get('results', {}).get('score', 0) > 0.5:
                print("   This article appears to be moderately credible")
            else:
                print("   This article has low credibility - verify claims independently")
                
        else:
            print(f"\n❌ API test failed with status {response.status_code}")
            try:
                error_json = response.json()
                print(f"   Error: {json.dumps(error_json, indent=2)}")
            except:
                print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error testing API: {e}")

def main():
    """Main function"""
    print("🚀 VeriFact - AI-Powered News Validation System")
    print("=" * 50)
    
    # Check if backend is running
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server is not responding properly")
            return
    except:
        print("❌ Backend server is not running")
        print("   Please start it with: cd backend && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    test_validation_with_real_apis()
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print("\n📖 Next steps:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Enter a real news article URL or paste content")
    print("   3. Click 'Validate Article' to see real-time analysis")
    print("   4. Check the detailed results with claims, sources, and credibility scores")

if __name__ == "__main__":
    main() 