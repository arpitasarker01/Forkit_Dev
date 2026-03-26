export type PassportType = 'model' | 'agent'
export type VerificationStatus = 'verified' | 'monitoring' | 'draft' | 'flagged'
export type VerificationCheckStatus = 'pass' | 'warn' | 'pending'
export type RiskLevel = 'Low' | 'Medium' | 'High'

export interface VerificationCheck {
  label: string
  status: VerificationCheckStatus
  detail: string
}

export interface PassportTool {
  name: string
  description: string
  endpointUrl: string
}

export interface PassportMetadata {
  license: string
  region: string
  useCases: string[]
  permissions: string[]
  evidence: string[]
  integrityScore: number
  governanceScore: number
  lastVerifiedAt: string
  riskLevel: RiskLevel
}

export interface Passport {
  id: number
  gaid: string
  passportType: PassportType
  name: string
  description: string
  ownerName: string
  organization: string
  verificationStatus: VerificationStatus
  checksumSha256?: string | null
  artifactHash?: string | null
  parentHash?: string | null
  parentPassportGaid?: string | null
  sourceUrl?: string | null
  architecture?: string | null
  taskType?: string | null
  trainingData?: string[] | null
  capabilities?: {
    modalities: string[]
    contextLength: number
    domains: string[]
  } | null
  quantisation?: {
    method: string
    bits: number
  } | null
  fineTuningMethod?: string | null
  parameterCount?: number | null
  sealedAt?: string | null
  systemPromptHash?: string | null
  modelPassportGaid?: string | null
  tools?: PassportTool[] | null
  memoryType?: string | null
  temperature?: number | null
  maxTokens?: number | null
  deploymentEnvironment?: string | null
  heartbeatConfig?: {
    intervalDays: 7 | 15 | 30 | 90
    statusUrl?: string
  } | null
  liveness?: {
    checkinStatus: 'active' | 'silent' | 'offline'
    lastCheckinAt: string
    missedAttempts: number
    nextCheckinDue: string
  } | null
  verificationChecks: VerificationCheck[]
  metadata: PassportMetadata
  createdAt: string
  updatedAt: string
}

export interface PassportEdge {
  from: string
  to: string
  relation: 'forked from' | 'powered by'
}
