import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Activity,
  Box,
  Info,
  Loader2,
  ShieldCheck,
} from 'lucide-react'
import { fetchApi } from '@/lib/api'
import { getPassports } from '@/lib/mockApi'
import { cn } from '@/lib/utils'
import type { Passport } from '@/types'

export function CreatePassportPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [passportType, setPassportType] = useState<'model' | 'agent'>('model')
  const [name, setName] = useState('')
  const [org, setOrg] = useState('Forkit')
  const [description, setDescription] = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  const [checksumSha256, setChecksumSha256] = useState('')
  const [parentPassportGaid, setParentPassportGaid] = useState('')
  const [modelPassportGaid, setModelPassportGaid] = useState('')
  const [deploymentEnvironment, setDeploymentEnvironment] = useState('staging')
  const [intervalDays, setIntervalDays] = useState<7 | 15 | 30 | 90>(15)
  const [statusUrl, setStatusUrl] = useState('')

  const passports = getPassports()
  const modelOptions = passports.filter((passport) => passport.passportType === 'model')
  const parentOptions = passports.filter((passport) =>
    passportType === 'model'
      ? passport.passportType === 'model'
      : passport.passportType === 'agent',
  )

  const gaidPreview = `gaid-${(name || 'new-passport')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'draft'}-preview`

  const linkedModel = modelOptions.find((passport) => passport.gaid === modelPassportGaid)
  const linkedParent = parentOptions.find(
    (passport) => passport.gaid === parentPassportGaid,
  )

  const checklist = [
    {
      label: 'Checksum attached',
      ready: checksumSha256.length === 64,
    },
    {
      label: 'Lineage reference selected',
      ready: Boolean(parentPassportGaid || modelPassportGaid),
    },
    {
      label: 'Source URL provided',
      ready: sourceUrl.startsWith('http'),
    },
  ]

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetchApi('/v1/passports', {
        method: 'POST',
        body: JSON.stringify({
          passportType,
          name,
          org,
          description,
          sourceUrl,
          checksumSha256,
          parentPassportGaid: parentPassportGaid || undefined,
          modelPassportGaid: modelPassportGaid || undefined,
          deploymentEnvironment,
          heartbeatConfig:
            passportType === 'agent'
              ? {
                  intervalDays,
                  statusUrl: statusUrl || undefined,
                }
              : undefined,
        }),
      })

      navigate(`/passports/${(response as Passport).gaid}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to register passport')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      <div className="max-w-6xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-[#f1ebdf] tracking-tight">
            Create Passport
          </h1>
          <p className="text-dark-text-secondary mt-1">
            Reuse the provided frontend’s registration flow, but point it at Forkit Core’s registry shape.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <form
              onSubmit={handleSubmit}
              className="waterdrop-glass border border-[#f1ebdf]/10 rounded-2xl shadow-lg overflow-hidden"
            >
              <div className="p-8 border-b border-[#f1ebdf]/10 bg-white/5 backdrop-blur-md">
                <label className="block text-xs font-bold text-dark-text-secondary mb-4 uppercase tracking-widest">
                  Asset Type
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setPassportType('model')}
                    className={cn(
                      'flex flex-col items-center justify-center p-6 rounded-xl border-2 transition-all duration-200',
                      passportType === 'model'
                        ? 'border-[#008190] bg-[#008190]/10 text-[#6aa7ab] shadow-sm transform scale-[1.02]'
                        : 'border-[#f1ebdf]/10 bg-white/5 text-dark-text-secondary hover:border-[#008190]/50',
                    )}
                  >
                    <Box className="w-8 h-8 mb-3" />
                    <span className="font-bold text-lg text-[#f1ebdf]">Model Passport</span>
                    <span className="text-xs opacity-80 mt-1 font-medium">
                      Foundation or derived model
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPassportType('agent')}
                    className={cn(
                      'flex flex-col items-center justify-center p-6 rounded-xl border-2 transition-all duration-200',
                      passportType === 'agent'
                        ? 'border-[#008190] bg-[#008190]/10 text-[#6aa7ab] shadow-sm transform scale-[1.02]'
                        : 'border-[#f1ebdf]/10 bg-white/5 text-dark-text-secondary hover:border-[#008190]/50',
                    )}
                  >
                    <Activity className="w-8 h-8 mb-3" />
                    <span className="font-bold text-lg text-[#f1ebdf]">Agent Passport</span>
                    <span className="text-xs opacity-80 mt-1 font-medium">
                      Runtime with heartbeat tracking
                    </span>
                  </button>
                </div>
              </div>

              <div className="p-8 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                      Asset Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(event) => setName(event.target.value)}
                      placeholder="e.g., Forkit Provenance Exporter"
                      className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                      Organization *
                    </label>
                    <input
                      type="text"
                      required
                      value={org}
                      onChange={(event) => setOrg(event.target.value)}
                      placeholder="Forkit"
                      className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                    Description
                  </label>
                  <textarea
                    value={description}
                    onChange={(event) => setDescription(event.target.value)}
                    rows={4}
                    placeholder="Summarise what this passport represents and how it will be used."
                    className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all resize-none"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                      Source URL
                    </label>
                    <input
                      type="url"
                      value={sourceUrl}
                      onChange={(event) => setSourceUrl(event.target.value)}
                      placeholder="https://github.com/..."
                      className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                      Checksum (SHA-256)
                    </label>
                    <input
                      type="text"
                      value={checksumSha256}
                      onChange={(event) => setChecksumSha256(event.target.value)}
                      placeholder="64-character lowercase hex"
                      maxLength={64}
                      className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] font-mono text-sm placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {passportType === 'agent' ? (
                    <div>
                      <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                        Linked Model
                      </label>
                      <select
                        value={modelPassportGaid}
                        onChange={(event) => setModelPassportGaid(event.target.value)}
                        className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                      >
                        <option value="">No linked model</option>
                        {modelOptions.map((passport) => (
                          <option key={passport.gaid} value={passport.gaid}>
                            {passport.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  ) : null}

                  <div>
                    <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                      {passportType === 'model' ? 'Parent Model' : 'Parent Agent'}
                    </label>
                    <select
                      value={parentPassportGaid}
                      onChange={(event) => setParentPassportGaid(event.target.value)}
                      className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                    >
                      <option value="">No parent link</option>
                      {parentOptions.map((passport) => (
                        <option key={passport.gaid} value={passport.gaid}>
                          {passport.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                      Deployment Environment
                    </label>
                    <input
                      type="text"
                      value={deploymentEnvironment}
                      onChange={(event) => setDeploymentEnvironment(event.target.value)}
                      placeholder="staging"
                      className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                    />
                  </div>

                  {passportType === 'agent' ? (
                    <div>
                      <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                        Heartbeat Interval
                      </label>
                      <select
                        value={intervalDays}
                        onChange={(event) =>
                          setIntervalDays(Number(event.target.value) as 7 | 15 | 30 | 90)
                        }
                        className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                      >
                        <option value={7}>7 days</option>
                        <option value={15}>15 days</option>
                        <option value={30}>30 days</option>
                        <option value={90}>90 days</option>
                      </select>
                    </div>
                  ) : null}
                </div>

                {passportType === 'agent' ? (
                  <div>
                    <label className="block text-sm font-bold text-[#f1ebdf] mb-2">
                      Status URL
                    </label>
                    <input
                      type="url"
                      value={statusUrl}
                      onChange={(event) => setStatusUrl(event.target.value)}
                      placeholder="https://status.forkit.dev/agent"
                      className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent transition-all"
                    />
                  </div>
                ) : null}
              </div>

              <div className="p-8 border-t border-[#f1ebdf]/10 bg-white/5 backdrop-blur-md flex flex-col sm:flex-row items-center justify-between gap-4">
                {error ? (
                  <p className="text-sm font-medium text-red-300 bg-red-500/10 px-4 py-2 rounded-lg border border-red-500/20">
                    {error}
                  </p>
                ) : (
                  <p className="text-sm font-medium text-dark-text-secondary">
                    Draft passports are created in-memory and routed straight to the detail screen.
                  </p>
                )}

                <button
                  type="submit"
                  disabled={loading || !name || !org}
                  className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3.5 bg-gradient-to-r from-[#008190] to-[#2a1f55] text-[#f1ebdf] font-bold rounded-xl shadow-lg hover:from-[#008190]/90 hover:to-[#2a1f55]/90 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <ShieldCheck className="w-5 h-5" />
                  )}
                  Mint Passport
                </button>
              </div>
            </form>
          </div>

          <div className="space-y-6">
            <div className="waterdrop-glass border border-[#f1ebdf]/10 rounded-2xl p-6 shadow-lg">
              <h3 className="text-[11px] font-bold text-dark-text-secondary uppercase tracking-widest mb-4">
                GAID Preview
              </h3>
              <div className="p-4 bg-[#0B0F19]/60 border border-[#f1ebdf]/10 rounded-xl font-mono text-sm text-[#f1ebdf] break-all">
                {gaidPreview}
              </div>
            </div>

            <div className="waterdrop-glass border border-[#f1ebdf]/10 rounded-2xl shadow-lg overflow-hidden">
              <div className="p-6 border-b border-[#f1ebdf]/10 bg-white/5 flex justify-between items-center">
                <h3 className="text-[11px] font-bold text-dark-text-secondary uppercase tracking-widest">
                  Validation Checklist
                </h3>
              </div>

              <div className="p-6 space-y-5">
                {checklist.map((item) => (
                  <div key={item.label} className="flex items-start gap-4">
                    <div
                      className={cn(
                        'mt-0.5 w-6 h-6 rounded-full flex items-center justify-center shrink-0 border shadow-sm',
                        item.ready
                          ? 'bg-emerald-900/30 border-emerald-700/50 text-emerald-400'
                          : 'bg-white/5 border-[#f1ebdf]/10 text-dark-text-secondary',
                      )}
                    >
                      {item.ready ? '✓' : ''}
                    </div>
                    <div>
                      <p
                        className={cn(
                          'text-sm font-bold',
                          item.ready ? 'text-[#f1ebdf]' : 'text-dark-text-secondary',
                        )}
                      >
                        {item.label}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="waterdrop-glass border border-[#f1ebdf]/10 rounded-2xl p-6 shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <Info className="w-4 h-4 text-[#f49355]" />
                <h3 className="text-[11px] font-bold text-dark-text-secondary uppercase tracking-widest">
                  Lineage Mapping
                </h3>
              </div>
              <div className="space-y-4 text-sm">
                <div className="rounded-xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                  <div className="text-dark-text-secondary">Linked model</div>
                  <div className="mt-2 text-[#f1ebdf]">
                    {linkedModel?.name || 'No model selected'}
                  </div>
                </div>
                <div className="rounded-xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                  <div className="text-dark-text-secondary">Parent lineage</div>
                  <div className="mt-2 text-[#f1ebdf]">
                    {linkedParent?.name || 'No parent link selected'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
