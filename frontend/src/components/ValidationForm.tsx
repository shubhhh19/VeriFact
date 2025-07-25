import React, { useState } from 'react'

interface ValidationFormProps {
  onSubmit: (articleUrl: string, articleContent?: string) => void
  isLoading: boolean
}

const ValidationForm: React.FC<ValidationFormProps> = ({ onSubmit, isLoading }) => {
  const [articleUrl, setArticleUrl] = useState('')
  const [articleContent, setArticleContent] = useState('')
  const [inputType, setInputType] = useState<'url' | 'content'>('url')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputType === 'url' && articleUrl.trim()) {
      onSubmit(articleUrl.trim())
    } else if (inputType === 'content' && articleContent.trim()) {
      onSubmit('', articleContent.trim())
    }
  }

  const isValid = () => {
    if (inputType === 'url') {
      return articleUrl.trim().length > 0
    } else {
      return articleContent.trim().length > 0
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-4">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h3 className="text-2xl font-bold text-gray-900">Validate Article</h3>
          <p className="text-gray-600">Submit URL or paste content</p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Input Type Toggle */}
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            type="button"
            onClick={() => setInputType('url')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              inputType === 'url'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Article URL
          </button>
          <button
            type="button"
            onClick={() => setInputType('content')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              inputType === 'content'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Paste Content
          </button>
        </div>
        
        {/* URL Input */}
        {inputType === 'url' && (
          <div>
            <label htmlFor="article-url" className="block text-sm font-medium text-gray-700 mb-2">
              News Article URL
            </label>
            <input
              type="url"
              id="article-url"
              value={articleUrl}
              onChange={(e) => setArticleUrl(e.target.value)}
              placeholder="https://example.com/news-article"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              required
              disabled={isLoading}
            />
          </div>
        )}
        
        {/* Content Input */}
        {inputType === 'content' && (
          <div>
            <label htmlFor="article-content" className="block text-sm font-medium text-gray-700 mb-2">
              Article Content
            </label>
            <textarea
              id="article-content"
              value={articleContent}
              onChange={(e) => setArticleContent(e.target.value)}
              placeholder="Paste the article content here..."
              rows={8}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors resize-none"
              required
              disabled={isLoading}
            />
          </div>
        )}
        
        <button
          type="submit"
          disabled={isLoading || !isValid()}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Validating...
            </div>
          ) : (
            'Validate Article'
          )}
        </button>
      </form>
      
      <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          How it works
        </h4>
        <ul className="text-sm text-blue-800 space-y-2">
          <li className="flex items-start">
            <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
            <span>AI extracts key claims from the article</span>
          </li>
          <li className="flex items-start">
            <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
            <span>Cross-references with multiple news sources</span>
          </li>
          <li className="flex items-start">
            <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
            <span>Detects contradictions and inconsistencies</span>
          </li>
          <li className="flex items-start">
            <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
            <span>Provides credibility scoring and analysis</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default ValidationForm 