export interface ValidationResult {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'error' | 'in_progress' | 'failed'
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
  details?: any
}

export interface ValidationRequest {
  article_url?: string
  article_content?: string
  title?: string
  validation_types: string[]
  include_sources: boolean
  include_contradictions: boolean
}

export interface ValidationResponse {
  success: boolean
  validation_id?: string
  status?: string
  results?: ValidationResult
  message?: string
  error?: string
} 