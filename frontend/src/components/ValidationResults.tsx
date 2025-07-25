import React from 'react'
import { ValidationResult } from '../types/validation'

interface ValidationResultsProps {
  results: ValidationResult[]
}

const ValidationResults: React.FC<ValidationResultsProps> = ({ results }) => {
  if (results.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-12">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-6">
            <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No validations yet</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Submit a news article URL or paste content to see validation results and credibility analysis.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold text-gray-900">Validation Results</h3>
        <span className="text-sm text-gray-500">{results.length} validation{results.length !== 1 ? 's' : ''}</span>
      </div>
      
      {results.map((result) => (
        <div key={result.id} className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="text-xl font-semibold text-gray-900 mb-2">{result.article.title}</h4>
                <p className="text-sm text-gray-500 mb-2">{result.article.source}</p>
                {result.article.url && (
                  <a 
                    href={result.article.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View Article →
                  </a>
                )}
              </div>
              <div className="text-right">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  result.credibility_score >= 0.7 ? 'bg-green-100 text-green-800' :
                  result.credibility_score >= 0.4 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {Math.round(result.credibility_score * 100)}% Credible
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(result.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Claims Section */}
              <div>
                <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  Key Claims ({result.claims.length})
                </h5>
                {result.claims.length > 0 ? (
                  <ul className="space-y-2">
                    {result.claims.map((claim, index) => (
                      <li key={index} className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                        {claim}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 italic">No claims extracted</p>
                )}
              </div>

              {/* Sources Section */}
              <div>
                <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  Sources Verified ({result.sources_verified.length})
                </h5>
                {result.sources_verified.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.sources_verified.map((source, index) => (
                      <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-green-100 text-green-800">
                        {source}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 italic">No sources verified</p>
                )}
              </div>
            </div>

            {/* Contradictions Section */}
            {result.contradictions.length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h5 className="font-semibold text-red-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Contradictions Found ({result.contradictions.length})
                </h5>
                <ul className="space-y-2">
                  {result.contradictions.map((contradiction, index) => (
                    <li key={index} className="text-sm text-red-700 bg-red-50 p-3 rounded-lg border border-red-200">
                      {contradiction}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Detailed Analysis */}
            {result.details && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h5 className="font-semibold text-gray-900 mb-3">Detailed Analysis</h5>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-gray-500">Confidence</div>
                    <div className="font-semibold text-gray-900">
                      {result.details.confidence ? Math.round(result.details.confidence * 100) : 'N/A'}%
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-gray-500">Processing Time</div>
                    <div className="font-semibold text-gray-900">
                      {result.details.processing_time ? `${result.details.processing_time}s` : 'N/A'}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-gray-500">Sources Checked</div>
                    <div className="font-semibold text-gray-900">
                      {result.details.sources_checked || result.sources_verified.length}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-gray-500">Claims Extracted</div>
                    <div className="font-semibold text-gray-900">
                      {result.details.claims_extracted || result.claims.length}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ValidationResults 