import React, { useState } from 'react'

interface ValidationFormProps {
  onSubmit: (articleUrl: string) => void
  isLoading: boolean
}

const ValidationForm: React.FC<ValidationFormProps> = ({ onSubmit, isLoading }) => {
  const [articleUrl, setArticleUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (articleUrl.trim()) {
      onSubmit(articleUrl.trim())
      setArticleUrl('')
    }
  }

  return (
    <div className="card">
      <h3 className="text-xl font-semibold text-gray-900 mb-4">
        Validate Article
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
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
            className="input-field"
            required
            disabled={isLoading}
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading || !articleUrl.trim()}
          className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
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
      
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">How it works:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Extracts key claims from the article</li>
          <li>• Cross-references with multiple news sources</li>
          <li>• Detects contradictions and inconsistencies</li>
          <li>• Provides credibility scoring</li>
        </ul>
      </div>
    </div>
  )
}

export default ValidationForm 