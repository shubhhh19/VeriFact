# API Keys Setup for VeriFact

To enable real fact verification using Gemini AI and News API, you need to set up your API keys.

## 🔑 Required API Keys

### 1. Google Gemini API Key
- **Get it from**: https://makersuite.google.com/app/apikey
- **Cost**: Free tier available
- **Usage**: AI-powered claim extraction and contradiction detection

### 2. News API Key
- **Get it from**: https://newsapi.org/register
- **Cost**: Free tier available (1000 requests/day)
- **Usage**: Source verification and fact-checking

## 🚀 Setup Instructions

### Option 1: Environment Variables (Recommended)

Create a `.env` file in the project root with:

```bash
# Google Gemini API Key
GEMINI_API_KEY=your_actual_gemini_api_key_here

# News API Key
NEWS_API_KEY=your_actual_news_api_key_here

# Other settings
DEBUG=true
SECRET_KEY=your-super-secret-key-that-is-at-least-32-characters-long
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Option 2: System Environment Variables

Set these in your system environment:

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
$env:NEWS_API_KEY="your_actual_news_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_actual_gemini_api_key_here
set NEWS_API_KEY=your_actual_news_api_key_here
```

## 🧪 Testing

Once you've set up your API keys:

1. **Restart the backend server**:
   ```bash
   cd backend
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test the API**:
   ```bash
   python test_api.py
   ```

3. **Use the frontend**:
   - Open http://localhost:3000
   - Enter a news article URL or paste content
   - Click "Validate Article"

## 🔍 What You'll See

With real API keys, the system will:

- **Extract actual claims** from news articles using Gemini AI
- **Find real sources** from News API to verify claims
- **Detect contradictions** between claims and sources
- **Calculate credibility scores** based on source reliability
- **Provide detailed analysis** with real data

## ⚠️ Important Notes

- **Rate Limits**: News API has a free tier limit of 1000 requests/day
- **API Costs**: Check the pricing for both APIs if you exceed free tiers
- **Privacy**: Never commit your API keys to version control
- **Backup**: The system has fallback mechanisms if APIs are unavailable

## 🆘 Troubleshooting

If you see "Sample data" in results:
1. Check that your API keys are correctly set
2. Verify the keys are valid by testing them separately
3. Restart the backend server after setting environment variables
4. Check the server logs for API errors 