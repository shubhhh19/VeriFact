import React, { useState } from 'react'
import ValidationForm from './ValidationForm'
import ValidationResults from './ValidationResults'
import { ValidationResult } from '../types/validation'

const NewsValidator: React.FC = () => {
  const [validationResults, setValidationResults] = useState<ValidationResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleValidation = async (articleUrl: string, articleContent?: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/v1/validation/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          article_url: articleUrl || undefined,
          article_content: articleContent || undefined,
          validation_types: ['comprehensive'],
          include_sources: true,
          include_contradictions: true,
        }),
      })

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.success && data.results) {
        const newResult: ValidationResult = {
          id: data.validation_id,
          status: data.results.status,
          article: {
            title: 'Validated Article',
            url: articleUrl,
            source: 'User Input'
          },
          claims: data.results.claims?.map((claim: any) => claim.text) || [],
          credibility_score: data.results.score || 0,
          contradictions: data.results.contradictions?.map((cont: any) => cont.claim) || [],
          sources_verified: data.results.sources?.map((source: any) => source.name) || [],
          timestamp: data.results.completed_at || new Date().toISOString(),
          details: data.results
        }
        
        setValidationResults(prev => [newResult, ...prev])
      } else {
        throw new Error(data.error || 'Validation failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-6">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Verify News with AI
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Submit a news article URL or paste content to analyze its credibility, 
          extract claims, and detect contradictions across multiple sources.
        </p>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex">
            <svg className="w-5 h-5 text-red-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <ValidationForm onSubmit={handleValidation} isLoading={isLoading} />
        </div>
        
        <div className="lg:col-span-2">
          <ValidationResults results={validationResults} />
        </div>
      </div>

      {/* Features Section */}
      <div className="mt-16 grid md:grid-cols-3 gap-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Claim Extraction</h3>
          <p className="text-gray-600">AI automatically identifies and extracts key claims from news articles</p>
        </div>
        
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-4">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9m0-9H3" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Source Verification</h3>
          <p className="text-gray-600">Cross-reference information with multiple trusted news sources</p>
        </div>
        
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-red-100 rounded-lg mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Contradiction Detection</h3>
          <p className="text-gray-600">Identify conflicting information and inconsistencies across sources</p>
        </div>
      </div>
    </div>
  )
}

export default NewsValidator 