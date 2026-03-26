import { useEffect, useState } from 'react'
import {
  Activity,
  ArrowRight,
  ExternalLink,
  Fingerprint,
  GitBranch,
  Loader2,
  ShieldCheck,
  Wrench,
} from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { LineageGraph } from '@/components/LineageGraph'
import PassportCard from '@/components/PassportCard'
import { fetchApi } from '@/lib/api'
import type { Passport, PassportEdge } from '@/types'

export function PassportDetailPage() {
  const { passportSlug } = useParams()
  const [passport, setPassport] = useState<Passport | null>(null)
  const [family, setFamily] = useState<Passport[]>([])
  const [edges, setEdges] = useState<PassportEdge[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      if (!passportSlug) {
        setError('Missing passport identifier.')
        setLoading(false)
        return
      }

      try {
        const [passportData, lineageData] = await Promise.all([
          fetchApi<Passport>(`/v1/passports/${passportSlug}`),
          fetchApi<{ focus: Passport; family: Passport[]; edges: PassportEdge[] }>(
            `/v1/passports/${passportSlug}/lineage`,
          ),
        ])

        setPassport(passportData)
        setFamily(lineageData.family ?? [])
        setEdges(lineageData.edges ?? [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load passport.')
      } finally {
        setLoading(false)
      }
    }

    void load()
  }, [passportSlug])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-[#6aa7ab]" />
      </div>
    )
  }

  if (error || !passport) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
        <div className="waterdrop-glass rounded-[2rem] p-10 border border-[#f1ebdf]/10 text-center">
          <h1 className="text-3xl font-bold text-[#f1ebdf]">Passport not found</h1>
          <p className="text-dark-text-secondary mt-3">{error || 'No passport data returned.'}</p>
          <Link
            to="/passports"
            className="inline-flex items-center gap-2 mt-6 px-6 py-3 bg-gradient-to-r from-[#008190] to-[#2a1f55] text-[#f1ebdf] rounded-xl font-semibold"
          >
            Return to Passport List
          </Link>
        </div>
      </div>
    )
  }

  const relatedPassports = family.filter((candidate) => candidate.gaid !== passport.gaid)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 w-full">
      <section className="waterdrop-glass rounded-[2rem] border border-[#f1ebdf]/10 overflow-hidden">
        <div className="h-1.5 w-full bg-gradient-to-r from-[#008190] via-[#2a1f55] to-[#f49355]" />
        <div className="p-8 space-y-8">
          <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-6">
            <div className="space-y-5">
              <div className="flex flex-wrap items-center gap-3">
                <Badge variant="outline">{passport.passportType}</Badge>
                <Badge
                  variant={
                    passport.verificationStatus === 'verified'
                      ? 'success'
                      : passport.verificationStatus === 'monitoring'
                        ? 'warning'
                        : passport.verificationStatus === 'draft'
                          ? 'outline'
                          : 'danger'
                  }
                >
                  {passport.verificationStatus}
                </Badge>
              </div>
              <div>
                <h1 className="text-4xl font-bold text-[#f1ebdf] tracking-tight">
                  {passport.name}
                </h1>
                <p className="text-dark-text-secondary mt-3 max-w-3xl text-lg leading-relaxed">
                  {passport.description}
                </p>
              </div>
              <div className="flex flex-wrap gap-4">
                <Link
                  to={`/verify?id=${passport.gaid}`}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#008190] to-[#2a1f55] text-[#f1ebdf] rounded-xl font-semibold"
                >
                  Verify Passport
                  <ShieldCheck className="w-4 h-4" />
                </Link>
                <Link
                  to={`/lineage?id=${passport.gaid}`}
                  className="inline-flex items-center gap-2 px-6 py-3 border border-[#f1ebdf]/10 rounded-xl text-[#f1ebdf] hover:bg-[#f1ebdf]/5 transition-colors"
                >
                  Explore Lineage
                  <GitBranch className="w-4 h-4" />
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 min-w-full xl:min-w-[360px] xl:max-w-[420px]">
              <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
                  Governance
                </div>
                <div className="mt-2 text-3xl font-bold text-[#f1ebdf]">
                  {passport.metadata.governanceScore}
                </div>
              </div>
              <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
                  Integrity
                </div>
                <div className="mt-2 text-3xl font-bold text-[#f1ebdf]">
                  {passport.metadata.integrityScore}
                </div>
              </div>
              <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
                  Risk
                </div>
                <div className="mt-2 text-3xl font-bold text-amber-300">
                  {passport.metadata.riskLevel}
                </div>
              </div>
              <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
                  Last Verified
                </div>
                <div className="mt-2 text-sm font-semibold text-[#f1ebdf]">
                  {new Date(passport.metadata.lastVerifiedAt).toLocaleString()}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-6">
            <Card className="border border-[#f1ebdf]/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Fingerprint className="w-5 h-5 text-[#6aa7ab]" />
                  Identity Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary">
                    GAID
                  </div>
                  <div className="mt-2 font-mono text-sm text-[#f1ebdf] break-all">
                    {passport.gaid}
                  </div>
                </div>
                <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary">
                    Checksum
                  </div>
                  <div className="mt-2 font-mono text-sm text-[#f1ebdf] break-all">
                    {passport.checksumSha256 || 'Not sealed yet'}
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                    <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary">
                      Owner
                    </div>
                    <div className="mt-2 text-sm text-[#f1ebdf]">
                      {passport.ownerName} · {passport.organization}
                    </div>
                  </div>
                  <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                    <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary">
                      Architecture
                    </div>
                    <div className="mt-2 text-sm text-[#f1ebdf]">
                      {passport.architecture || 'Not specified'}
                    </div>
                  </div>
                </div>
                <div className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary">
                    Source
                  </div>
                  {passport.sourceUrl ? (
                    <a
                      href={passport.sourceUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-flex items-center gap-2 text-sm text-[#6aa7ab] hover:text-[#f1ebdf] transition-colors"
                    >
                      {passport.sourceUrl}
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  ) : (
                    <div className="mt-2 text-sm text-dark-text-secondary">No source URL attached.</div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="border border-[#f1ebdf]/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-[#6aa7ab]" />
                  Verification Checklist
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {passport.verificationChecks.map((check) => (
                  <div
                    key={check.label}
                    className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-semibold text-[#f1ebdf]">{check.label}</div>
                      <Badge
                        variant={
                          check.status === 'pass'
                            ? 'success'
                            : check.status === 'warn'
                              ? 'warning'
                              : 'outline'
                        }
                      >
                        {check.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-dark-text-secondary mt-2">
                      {check.detail}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-6">
        <Card className="border border-[#f1ebdf]/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#f49355]" />
              Capabilities, Tools, and Permissions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary mb-3">
                Use Cases
              </div>
              <div className="flex flex-wrap gap-2">
                {passport.metadata.useCases.map((useCase) => (
                  <Badge key={useCase} variant="outline">
                    {useCase}
                  </Badge>
                ))}
              </div>
            </div>

            <div>
              <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary mb-3">
                Permissions
              </div>
              <div className="flex flex-wrap gap-2">
                {passport.metadata.permissions.map((permission) => (
                  <Badge key={permission} variant="outline">
                    {permission}
                  </Badge>
                ))}
              </div>
            </div>

            {passport.trainingData?.length ? (
              <div>
                <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary mb-3">
                  Training Data
                </div>
                <div className="space-y-3">
                  {passport.trainingData.map((item) => (
                    <div
                      key={item}
                      className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4 text-sm text-[#f1ebdf]"
                    >
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            {passport.tools?.length ? (
              <div>
                <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary mb-3">
                  Toolchain
                </div>
                <div className="space-y-3">
                  {passport.tools.map((tool) => (
                    <div
                      key={tool.name}
                      className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4"
                    >
                      <div className="flex items-center gap-2 text-sm font-semibold text-[#f1ebdf]">
                        <Wrench className="w-4 h-4 text-[#6aa7ab]" />
                        {tool.name}
                      </div>
                      <div className="text-sm text-dark-text-secondary mt-2">
                        {tool.description}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card className="border border-[#f1ebdf]/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ArrowRight className="w-5 h-5 text-[#6aa7ab]" />
              Evidence Bundle
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {passport.metadata.evidence.map((item) => (
              <div
                key={item}
                className="rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10 p-4 text-sm text-dark-text-secondary"
              >
                {item}
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <Card className="border border-[#f1ebdf]/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-[#6aa7ab]" />
            Connected Lineage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <LineageGraph passports={family} edges={edges} focusGaid={passport.gaid} />
        </CardContent>
      </Card>

      {relatedPassports.length > 0 ? (
        <section className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-2xl font-bold text-[#f1ebdf]">Connected Passports</h2>
            <Link
              to={`/lineage?id=${passport.gaid}`}
              className="text-[#6aa7ab] font-semibold hover:text-[#f1ebdf] transition-colors"
            >
              Full lineage view
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {relatedPassports.slice(0, 3).map((related) => (
              <PassportCard key={related.gaid} passport={related} />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}
