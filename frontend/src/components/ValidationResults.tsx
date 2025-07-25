import React from 'react'

interface ValidationResult {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  article: {
    title: string
    url: string
    source: string
  }
  claims: string[]
  credibility_score: number
  contradictions: string[]
  sources_verified: string[]
  timestamp: string
}

interface ValidationResultsProps {
  results: ValidationResult[]
}

const ValidationResults: React.FC<ValidationResultsProps> = ({ results }) => {
  if (results.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No validations yet</h3>
          <p className="mt-1 text-sm text-gray-500">Submit a news article URL to see validation results.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-gray-900">Validation Results</h3>
      
      {results.map((result) => (
        <div key={result.id} className="card">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h4 className="text-lg font-medium text-gray-900">{result.article.title}</h4>
              <p className="text-sm text-gray-500">{result.article.source}</p>
              <a href={result.article.url} target="_blank" rel="noopener noreferrer" className="text-sm text-primary-600 hover:text-primary-700">
                View Article →
              </a>
            </div>
            <div className="text-right">
              <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                result.credibility_score >= 0.7 ? 'bg-green-100 text-green-800' :
                result.credibility_score >= 0.4 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {Math.round(result.credibility_score * 100)}% Credible
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h5 className="font-medium text-gray-900 mb-2">Key Claims</h5>
              <ul className="space-y-1">
                {result.claims.map((claim, index) => (
                  <li key={index} className="text-sm text-gray-600">• {claim}</li>
                ))}
              </ul>
            </div>

            <div>
              <h5 className="font-medium text-gray-900 mb-2">Sources Verified</h5>
              <div className="flex flex-wrap gap-1">
                {result.sources_verified.map((source, index) => (
                  <span key={index} className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                    {source}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {result.contradictions.length > 0 && (
            <div className="mt-4">
              <h5 className="font-medium text-red-900 mb-2">Contradictions Found</h5>
              <ul className="space-y-1">
                {result.contradictions.map((contradiction, index) => (
                  <li key={index} className="text-sm text-red-600">• {contradiction}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Validated on {new Date(result.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ValidationResults 