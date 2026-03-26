import type { Passport, PassportEdge } from '../types'

type CreatePassportPayload = {
  passportType: 'model' | 'agent'
  name: string
  org: string
  description?: string
  sourceUrl?: string
  checksumSha256?: string
  parentPassportGaid?: string
  modelPassportGaid?: string
  deploymentEnvironment?: string
  heartbeatConfig?: Passport['heartbeatConfig']
}

const now = Date.now()

const seedPassports: Passport[] = [
  {
    id: 1,
    gaid: 'gaid-aurora-foundation-13b',
    passportType: 'model',
    name: 'Aurora Foundation 13B',
    description:
      'Root Forkit Core model passport used as the anchor for downstream governance, lineage, and compliance derivatives.',
    ownerName: 'Arpita Sarker',
    organization: 'Forkit',
    verificationStatus: 'verified',
    checksumSha256: '90ea6657ed2db16e6ba0830654dc4b38a497c7ea73b211217f12e8afc3c04ab4',
    artifactHash: '1c4a6c72f51b4ad903688d1b9127d8c05a23e34f9e88af6d7611d47c51f3a2aa',
    parentHash: null,
    parentPassportGaid: null,
    sourceUrl: 'https://github.com/arpitasarker01/Forkit_Dev',
    architecture: 'transformer',
    taskType: 'text-generation',
    trainingData: ['Public procurement directives', 'Corporate registry extracts', 'Synthetic decision traces'],
    capabilities: {
      modalities: ['text'],
      contextLength: 32768,
      domains: ['governance', 'audit', 'registry'],
    },
    quantisation: { method: 'AWQ', bits: 4 },
    fineTuningMethod: null,
    parameterCount: 13000000000,
    sealedAt: new Date(now - 12 * 24 * 60 * 60 * 1000).toISOString(),
    systemPromptHash: null,
    modelPassportGaid: null,
    tools: null,
    memoryType: null,
    temperature: null,
    maxTokens: null,
    deploymentEnvironment: 'registry://eu/foundation',
    heartbeatConfig: null,
    liveness: null,
    verificationChecks: [
      {
        label: 'Artifact checksum',
        status: 'pass',
        detail: 'Weight bundle digest matches the sealed artifact.',
      },
      {
        label: 'Creator signature',
        status: 'pass',
        detail: 'Signature envelope validated against the local keyring.',
      },
      {
        label: 'Root anchor',
        status: 'pass',
        detail: 'No parent expected. Root lineage is sealed.',
      },
    ],
    metadata: {
      license: 'Apache-2.0',
      region: 'EU-West',
      useCases: ['Model identity', 'Registry provenance', 'Compliance copilots'],
      permissions: ['Read registry records', 'Generate provenance manifests'],
      evidence: [
        'Artifact hash matched cold-storage bundle AUR-13B-BASE.',
        'Capability manifest refreshed for the March policy release.',
      ],
      integrityScore: 99,
      governanceScore: 98,
      lastVerifiedAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
      riskLevel: 'Low',
    },
    createdAt: new Date(now - 42 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    gaid: 'gaid-aurora-compliance-13b',
    passportType: 'model',
    name: 'Aurora Compliance 13B',
    description:
      'Fine-tuned compliance branch for policy analysis, exception handling, and release-readiness reviews.',
    ownerName: 'Arpita Sarker',
    organization: 'Forkit',
    verificationStatus: 'monitoring',
    checksumSha256: 'ec8d4e6932db715c47ffdd419abcefae6b45a7df5dfd0c66017c5e51dbb11fe6',
    artifactHash: 'a8f9eaab52bd944320af4d402ca0c2ce9b1ca0a7fd0cb81f48fa338d2f36db08',
    parentHash: '1c4a6c72f51b4ad903688d1b9127d8c05a23e34f9e88af6d7611d47c51f3a2aa',
    parentPassportGaid: 'gaid-aurora-foundation-13b',
    sourceUrl: 'https://github.com/arpitasarker01/Forkit_Dev/tree/main/examples',
    architecture: 'transformer',
    taskType: 'compliance-review',
    trainingData: ['EU AI Act annotations', 'Internal policy playbooks'],
    capabilities: {
      modalities: ['text'],
      contextLength: 32768,
      domains: ['compliance', 'policy', 'risk'],
    },
    quantisation: null,
    fineTuningMethod: 'LoRA',
    parameterCount: 13000000000,
    sealedAt: new Date(now - 8 * 24 * 60 * 60 * 1000).toISOString(),
    systemPromptHash: null,
    modelPassportGaid: null,
    tools: null,
    memoryType: null,
    temperature: null,
    maxTokens: null,
    deploymentEnvironment: 'registry://eu/compliance',
    heartbeatConfig: null,
    liveness: null,
    verificationChecks: [
      {
        label: 'Parent lineage',
        status: 'pass',
        detail: 'Parent model anchor matches Aurora Foundation 13B.',
      },
      {
        label: 'Artifact checksum',
        status: 'pass',
        detail: 'Weights match the sealed fine-tune release bundle.',
      },
      {
        label: 'Dataset integrity',
        status: 'warn',
        detail: 'One supplemental policy dataset needs checksum resealing.',
      },
    ],
    metadata: {
      license: 'Apache-2.0',
      region: 'EU-Central',
      useCases: ['Policy review', 'Regulatory gap detection', 'Escalation drafting'],
      permissions: ['Draft compliance memos', 'Escalate exception cases'],
      evidence: [
        'Parent lineage and artifact hash both resolve correctly.',
        'Dataset checksum drift was recorded after the latest enrichment cycle.',
      ],
      integrityScore: 94,
      governanceScore: 91,
      lastVerifiedAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
      riskLevel: 'Medium',
    },
    createdAt: new Date(now - 31 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 3,
    gaid: 'gaid-atlas-vision-risk-6b',
    passportType: 'model',
    name: 'Atlas Vision Risk 6B',
    description:
      'Multimodal risk model for supplier packet inspection, document anomaly screening, and vendor intake.',
    ownerName: 'Arpita Sarker',
    organization: 'Forkit',
    verificationStatus: 'verified',
    checksumSha256: 'c5c6e68e995462e327b1c044edfb0e2ac9d5d8445ddca6a82160b1d4f4c7931f',
    artifactHash: '723630f23206a6e1ba95b73e5fbf4be50163582f1513cfbc9165bf2359ff0e19',
    parentHash: '1c4a6c72f51b4ad903688d1b9127d8c05a23e34f9e88af6d7611d47c51f3a2aa',
    parentPassportGaid: 'gaid-aurora-foundation-13b',
    sourceUrl: 'https://github.com/arpitasarker01/Forkit_Dev/tree/main/docs',
    architecture: 'vision-transformer',
    taskType: 'document-risk-analysis',
    trainingData: ['Invoice image corpus', 'Vendor onboarding samples'],
    capabilities: {
      modalities: ['vision', 'text'],
      contextLength: 16384,
      domains: ['supplier-risk', 'document-intake'],
    },
    quantisation: { method: 'GPTQ', bits: 4 },
    fineTuningMethod: 'Adapter Tuning',
    parameterCount: 6000000000,
    sealedAt: new Date(now - 15 * 24 * 60 * 60 * 1000).toISOString(),
    systemPromptHash: null,
    modelPassportGaid: null,
    tools: null,
    memoryType: null,
    temperature: null,
    maxTokens: null,
    deploymentEnvironment: 'registry://us/vision-risk',
    heartbeatConfig: null,
    liveness: null,
    verificationChecks: [
      {
        label: 'Vision adapter checksum',
        status: 'pass',
        detail: 'Visual adapter package matches the passport record.',
      },
      {
        label: 'Parent lineage',
        status: 'pass',
        detail: 'Model traces back to Aurora Foundation 13B.',
      },
      {
        label: 'Capability manifest',
        status: 'pass',
        detail: 'Declared modalities are present in the runtime bundle.',
      },
    ],
    metadata: {
      license: 'Apache-2.0',
      region: 'US-East',
      useCases: ['Vendor screening', 'Visual anomaly scoring', 'Packet triage'],
      permissions: ['Inspect vendor attachments', 'Score submission anomalies'],
      evidence: [
        'Vision adapter hash matches the sealed deployment artifact.',
        'Latest deployment artifact sealed with no detected anomalies.',
      ],
      integrityScore: 97,
      governanceScore: 95,
      lastVerifiedAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
      riskLevel: 'Low',
    },
    createdAt: new Date(now - 35 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 4,
    gaid: 'gaid-policy-intake-copilot',
    passportType: 'agent',
    name: 'Policy Intake Copilot',
    description:
      'Agent passport for intake triage, policy diffing, and escalation workflows on top of Aurora Compliance.',
    ownerName: 'Arpita Sarker',
    organization: 'Forkit',
    verificationStatus: 'verified',
    checksumSha256: 'c2931ef28c9eb571556180b83fa4556d2df87c95dd0fd50ae6df9467548a674d',
    artifactHash: null,
    parentHash: null,
    parentPassportGaid: null,
    sourceUrl: 'https://github.com/arpitasarker01/Forkit_Dev/tree/main/forkit',
    architecture: 'react-agent',
    taskType: 'policy-intake',
    trainingData: ['Current policy release notes'],
    capabilities: {
      modalities: ['text', 'tools'],
      contextLength: 128000,
      domains: ['workflow', 'intake', 'routing'],
    },
    quantisation: null,
    fineTuningMethod: null,
    parameterCount: null,
    sealedAt: new Date(now - 6 * 24 * 60 * 60 * 1000).toISOString(),
    systemPromptHash: '9f2db8258b452004fbbd6d2241d1c099',
    modelPassportGaid: 'gaid-aurora-compliance-13b',
    tools: [
      {
        name: 'policy-diff-engine',
        description: 'Compares revisions and highlights policy drift.',
        endpointUrl: 'https://policy-intake.mock.forkit.dev/tools/diff',
      },
      {
        name: 'case-routing-webhook',
        description: 'Dispatches reviewed items to the right queue.',
        endpointUrl: 'https://policy-intake.mock.forkit.dev/tools/router',
      },
    ],
    memoryType: 'receipt-log',
    temperature: 0.2,
    maxTokens: 4000,
    deploymentEnvironment: 'production',
    heartbeatConfig: {
      intervalDays: 7,
      statusUrl: 'https://policy-intake.mock.forkit.dev/status',
    },
    liveness: {
      checkinStatus: 'active',
      lastCheckinAt: new Date(now - 2 * 60 * 60 * 1000).toISOString(),
      missedAttempts: 0,
      nextCheckinDue: new Date(now + 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    verificationChecks: [
      {
        label: 'Tool manifest',
        status: 'pass',
        detail: 'Attached tools and versions match the sealed record.',
      },
      {
        label: 'Endpoint pinning',
        status: 'pass',
        detail: 'Runtime endpoint hash still matches the approved release.',
      },
      {
        label: 'Underlying model link',
        status: 'pass',
        detail: 'Agent references Aurora Compliance 13B without mismatch.',
      },
    ],
    metadata: {
      license: 'Apache-2.0',
      region: 'EU-West',
      useCases: ['Case triage', 'Policy diffing', 'Escalation routing'],
      permissions: ['Open intake cases', 'Draft escalation packets'],
      evidence: [
        'Tool manifest hash matches the deployed orchestration bundle.',
        'Morning verification passed with no drift across tools or endpoints.',
      ],
      integrityScore: 96,
      governanceScore: 93,
      lastVerifiedAt: new Date(now - 10 * 60 * 60 * 1000).toISOString(),
      riskLevel: 'Low',
    },
    createdAt: new Date(now - 20 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(now - 10 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 5,
    gaid: 'gaid-supplier-guardian',
    passportType: 'agent',
    name: 'Supplier Guardian',
    description:
      'Vendor risk screening agent that combines visual packet checks with supplier metadata enrichment.',
    ownerName: 'Arpita Sarker',
    organization: 'Forkit',
    verificationStatus: 'flagged',
    checksumSha256: '77f2d62d09502a4fa9ac7367fe0f143b3119a1ff1f67d3e2a54ac8f6fcf7bb83',
    artifactHash: null,
    parentHash: null,
    parentPassportGaid: null,
    sourceUrl: 'https://github.com/arpitasarker01/Forkit_Dev/tree/main/tests',
    architecture: 'react-agent',
    taskType: 'supplier-risk',
    trainingData: ['Vendor onboarding samples', 'Risk watchlist feed'],
    capabilities: {
      modalities: ['vision', 'text', 'tools'],
      contextLength: 64000,
      domains: ['supplier-risk', 'triage'],
    },
    quantisation: null,
    fineTuningMethod: null,
    parameterCount: null,
    sealedAt: new Date(now - 4 * 24 * 60 * 60 * 1000).toISOString(),
    systemPromptHash: 'af78d0fb826f7ef4fd23395176c3ca71',
    modelPassportGaid: 'gaid-atlas-vision-risk-6b',
    tools: [
      {
        name: 'invoice-classifier',
        description: 'Screens attachments for invoice anomalies.',
        endpointUrl: 'https://supplier-guardian.mock.forkit.dev/tools/classifier',
      },
      {
        name: 'vendor-graph-enrich',
        description: 'Expands linked vendor entities and watchlist edges.',
        endpointUrl: 'https://supplier-guardian.mock.forkit.dev/tools/graph',
      },
    ],
    memoryType: 'vector-store',
    temperature: 0.3,
    maxTokens: 3000,
    deploymentEnvironment: 'staging',
    heartbeatConfig: {
      intervalDays: 7,
      statusUrl: 'https://supplier-guardian.mock.forkit.dev/status',
    },
    liveness: {
      checkinStatus: 'silent',
      lastCheckinAt: new Date(now - 28 * 60 * 60 * 1000).toISOString(),
      missedAttempts: 2,
      nextCheckinDue: new Date(now + 24 * 60 * 60 * 1000).toISOString(),
    },
    verificationChecks: [
      {
        label: 'Underlying model link',
        status: 'pass',
        detail: 'Atlas Vision Risk 6B link remains intact.',
      },
      {
        label: 'Endpoint pinning',
        status: 'warn',
        detail: 'Runtime endpoint no longer matches the sealed configuration.',
      },
      {
        label: 'Watchlist feed seal',
        status: 'warn',
        detail: 'Risk watchlist data requires resealing after nightly sync.',
      },
    ],
    metadata: {
      license: 'Apache-2.0',
      region: 'US-East',
      useCases: ['Vendor dossier triage', 'Packet anomaly scoring', 'Review queueing'],
      permissions: ['Flag supplier records', 'Trigger manual review queues'],
      evidence: [
        'Underlying model hash remains valid.',
        'Endpoint hash diverged after an unsealed configuration patch.',
      ],
      integrityScore: 82,
      governanceScore: 76,
      lastVerifiedAt: new Date(now - 14 * 60 * 60 * 1000).toISOString(),
      riskLevel: 'High',
    },
    createdAt: new Date(now - 17 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(now - 14 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 6,
    gaid: 'gaid-provenance-auditor',
    passportType: 'agent',
    name: 'Provenance Auditor',
    description:
      'Draft agent that packages lineage receipts, evidence bundles, and audit narratives for downstream review.',
    ownerName: 'Arpita Sarker',
    organization: 'Forkit',
    verificationStatus: 'draft',
    checksumSha256: '6a34ba51d33bc7fdb3f83b4ad54778791da44e7196d4f1bf1ae7ae4a9c00b5b0',
    artifactHash: null,
    parentHash: null,
    parentPassportGaid: 'gaid-policy-intake-copilot',
    sourceUrl: 'https://github.com/arpitasarker01/Forkit_Dev/tree/main/examples',
    architecture: 'react-agent',
    taskType: 'audit-export',
    trainingData: ['Registry snapshots', 'Verification run history'],
    capabilities: {
      modalities: ['text', 'tools'],
      contextLength: 96000,
      domains: ['audit', 'lineage', 'evidence'],
    },
    quantisation: null,
    fineTuningMethod: null,
    parameterCount: null,
    sealedAt: null,
    systemPromptHash: '1f4d8fb11c22c0fb11a5c9c0e948c25a',
    modelPassportGaid: 'gaid-aurora-compliance-13b',
    tools: [
      {
        name: 'lineage-graph-explorer',
        description: 'Builds ancestry graphs for a selected passport.',
        endpointUrl: 'staging://provenance-auditor/tools/graph',
      },
      {
        name: 'receipt-bundler',
        description: 'Packages audit receipts and supporting artifacts.',
        endpointUrl: 'staging://provenance-auditor/tools/receipts',
      },
    ],
    memoryType: 'receipt-ledger',
    temperature: 0.1,
    maxTokens: 5000,
    deploymentEnvironment: 'staging',
    heartbeatConfig: {
      intervalDays: 15,
      statusUrl: 'https://staging.forkit.dev/provenance-auditor/status',
    },
    liveness: {
      checkinStatus: 'offline',
      lastCheckinAt: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(),
      missedAttempts: 4,
      nextCheckinDue: new Date(now + 2 * 24 * 60 * 60 * 1000).toISOString(),
    },
    verificationChecks: [
      {
        label: 'Parent agent lineage',
        status: 'pass',
        detail: 'Fork link to Policy Intake Copilot is valid.',
      },
      {
        label: 'Staging endpoint seal',
        status: 'pending',
        detail: 'Endpoint configuration has not been sealed for production.',
      },
      {
        label: 'Red-team review',
        status: 'pending',
        detail: 'Pre-release verification scenario run has not started yet.',
      },
    ],
    metadata: {
      license: 'Apache-2.0',
      region: 'EU-Central',
      useCases: ['Lineage export', 'Audit receipt bundling', 'Review narrative drafting'],
      permissions: ['Read lineage graphs', 'Export evidence packages'],
      evidence: [
        'Draft build references the correct parent agent and model lineage.',
        'Red-team review and staging endpoint seal are still pending.',
      ],
      integrityScore: 90,
      governanceScore: 88,
      lastVerifiedAt: new Date(now - 8 * 60 * 60 * 1000).toISOString(),
      riskLevel: 'Medium',
    },
    createdAt: new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(now - 8 * 60 * 60 * 1000).toISOString(),
  },
]

let passportStore = [...seedPassports]

function slugify(value: string) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export function getPassports() {
  return [...passportStore]
}

export function getPassportByGaid(gaid: string) {
  return passportStore.find((passport) => passport.gaid === gaid)
}

export function getRegistryStats() {
  const passports = getPassports()

  return {
    total: passports.length,
    models: passports.filter((passport) => passport.passportType === 'model').length,
    agents: passports.filter((passport) => passport.passportType === 'agent').length,
    verified: passports.filter((passport) => passport.verificationStatus === 'verified').length,
    attention: passports.filter(
      (passport) =>
        passport.verificationStatus === 'flagged' ||
        passport.verificationStatus === 'draft' ||
        passport.verificationStatus === 'monitoring',
    ).length,
  }
}

export function getPassportEdges(passports = getPassports()) {
  return passports.flatMap<PassportEdge>((passport) => {
    const edges: PassportEdge[] = []

    if (passport.parentPassportGaid) {
      edges.push({
        from: passport.parentPassportGaid,
        to: passport.gaid,
        relation: 'forked from',
      })
    }

    if (passport.passportType === 'agent' && passport.modelPassportGaid) {
      edges.push({
        from: passport.modelPassportGaid,
        to: passport.gaid,
        relation: 'powered by',
      })
    }

    return edges
  })
}

export function getPassportFamily(seedGaid: string) {
  const queue = [seedGaid]
  const visited = new Set<string>()

  while (queue.length > 0) {
    const current = queue.shift()

    if (!current || visited.has(current)) {
      continue
    }

    visited.add(current)
    const focus = getPassportByGaid(current)

    passportStore.forEach((passport) => {
      const related =
        passport.gaid === current ||
        passport.parentPassportGaid === current ||
        passport.modelPassportGaid === current ||
        passport.gaid === focus?.parentPassportGaid ||
        passport.gaid === focus?.modelPassportGaid

      if (related && !visited.has(passport.gaid)) {
        queue.push(passport.gaid)
      }
    })
  }

  return passportStore.filter((passport) => visited.has(passport.gaid))
}

export function getRelatedPassports(gaid: string) {
  return getPassportFamily(gaid).filter((passport) => passport.gaid !== gaid)
}

function buildPassportFromPayload(payload: CreatePassportPayload) {
  const suffix = Date.now().toString(36)
  const gaid = `gaid-${slugify(payload.name)}-${suffix}`
  const isAgent = payload.passportType === 'agent'

  const newPassport: Passport = {
    id: passportStore.length + 1,
    gaid,
    passportType: payload.passportType,
    name: payload.name,
    description:
      payload.description ||
      'Draft passport created from the Forkit Core frontend prototype.',
    ownerName: 'Arpita Sarker',
    organization: payload.org,
    verificationStatus: 'draft',
    checksumSha256: payload.checksumSha256 || null,
    artifactHash: payload.checksumSha256 || null,
    parentHash: null,
    parentPassportGaid: payload.parentPassportGaid || null,
    sourceUrl: payload.sourceUrl || null,
    architecture: isAgent ? 'react-agent' : 'transformer',
    taskType: isAgent ? 'agent-orchestration' : 'model-registration',
    trainingData: isAgent ? ['Operational prompts', 'Release notes'] : ['Curated registry training bundle'],
    capabilities: {
      modalities: isAgent ? ['text', 'tools'] : ['text'],
      contextLength: isAgent ? 64000 : 32768,
      domains: ['governance', 'provenance'],
    },
    quantisation: isAgent ? null : { method: 'AWQ', bits: 4 },
    fineTuningMethod: isAgent ? null : 'LoRA',
    parameterCount: isAgent ? null : 7000000000,
    sealedAt: null,
    systemPromptHash: isAgent ? `draft-${suffix}` : null,
    modelPassportGaid: payload.modelPassportGaid || null,
    tools: isAgent
      ? [
          {
            name: 'registry-sync',
            description: 'Synchronises the draft with registry metadata.',
            endpointUrl: payload.heartbeatConfig?.statusUrl || 'staging://registry-sync',
          },
        ]
      : null,
    memoryType: isAgent ? 'receipt-ledger' : null,
    temperature: isAgent ? 0.2 : null,
    maxTokens: isAgent ? 4000 : null,
    deploymentEnvironment: payload.deploymentEnvironment || 'staging',
    heartbeatConfig: isAgent ? payload.heartbeatConfig ?? { intervalDays: 15 } : null,
    liveness: isAgent
      ? {
          checkinStatus: 'offline',
          lastCheckinAt: new Date().toISOString(),
          missedAttempts: 0,
          nextCheckinDue: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString(),
        }
      : null,
    verificationChecks: [
      {
        label: 'Artifact seal',
        status: payload.checksumSha256 ? 'pass' : 'pending',
        detail: payload.checksumSha256
          ? 'Draft includes a checksum ready for sealing.'
          : 'Add an artifact checksum before promotion.',
      },
      {
        label: 'Lineage link',
        status:
          payload.parentPassportGaid || payload.modelPassportGaid ? 'pass' : 'pending',
        detail:
          payload.parentPassportGaid || payload.modelPassportGaid
            ? 'Draft includes at least one lineage reference.'
            : 'No lineage reference selected yet.',
      },
      {
        label: 'Release review',
        status: 'pending',
        detail: 'Manual release approval has not been completed.',
      },
    ],
    metadata: {
      license: 'Apache-2.0',
      region: 'Prototype',
      useCases: ['Draft registration', 'Preview flow'],
      permissions: ['Register draft passports'],
      evidence: [
        'Draft generated by the Forkit Core frontend prototype.',
        'Promote only after checksum, lineage, and release approval are sealed.',
      ],
      integrityScore: payload.checksumSha256 ? 88 : 72,
      governanceScore: 78,
      lastVerifiedAt: new Date().toISOString(),
      riskLevel: 'Medium',
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }

  passportStore = [newPassport, ...passportStore]
  return newPassport
}

export async function mockFetchApi(endpoint: string, options: RequestInit = {}) {
  await new Promise((resolve) => setTimeout(resolve, 180))

  const method = options.method || 'GET'

  if (endpoint === '/v1/passports' || endpoint === '/v1/passports/mine') {
    if (method === 'POST') {
      const payload = JSON.parse((options.body as string) || '{}') as CreatePassportPayload
      return buildPassportFromPayload(payload)
    }

    return { passports: getPassports() }
  }

  if (endpoint.startsWith('/v1/passports/')) {
    const parts = endpoint.split('/')
    const gaid = parts[3]
    const passport = getPassportByGaid(gaid)

    if (!passport) {
      throw new Error('Passport not found')
    }

    if (endpoint.endsWith('/lineage')) {
      const family = getPassportFamily(gaid)
      return {
        focus: passport,
        family,
        edges: getPassportEdges(family),
      }
    }

    if (endpoint.endsWith('/summary')) {
      const family = getPassportFamily(gaid)
      return {
        familyCount: family.length,
        descendantCount: family.filter(
          (candidate) =>
            candidate.parentPassportGaid === gaid ||
            candidate.modelPassportGaid === gaid,
        ).length,
        lastVerifiedAt: passport.metadata.lastVerifiedAt,
      }
    }

    return passport
  }

  if (endpoint === '/v1/registry/stats') {
    return getRegistryStats()
  }

  throw new Error(`Unknown mock endpoint: ${endpoint}`)
}
