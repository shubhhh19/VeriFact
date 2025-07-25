import React, { useState } from 'react'
import ValidationForm from './ValidationForm'
import ValidationResults from './ValidationResults'

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

const NewsValidator: React.FC = () => {
  const [validationResults, setValidationResults] = useState<ValidationResult[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleValidation = async (articleUrl: string) => {
    setIsLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      const mockResult: ValidationResult = {
        id: Date.now().toString(),
        status: 'completed',
        article: {
          title: 'Sample News Article',
          url: articleUrl,
          source: 'Example News'
        },
        claims: [
          'Claim 1: This is a sample claim from the article',
          'Claim 2: Another important claim to verify'
        ],
        credibility_score: 0.75,
        contradictions: [
          'Contradiction found with source X',
          'Inconsistent information with source Y'
        ],
        sources_verified: [
          'Reuters',
          'Associated Press',
          'BBC News'
        ],
        timestamp: new Date().toISOString()
      }
      
      setValidationResults(prev => [mockResult, ...prev])
      setIsLoading(false)
    }, 2000)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Validate News Articles with AI
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Enter a news article URL to analyze its credibility, extract claims, 
          and check for contradictions across multiple sources.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <ValidationForm onSubmit={handleValidation} isLoading={isLoading} />
        </div>
        
        <div className="lg:col-span-2">
          <ValidationResults results={validationResults} />
        </div>
      </div>
    </div>
  )
}

export default NewsValidator 