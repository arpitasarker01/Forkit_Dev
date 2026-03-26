import {
  ArrowRight,
  Fingerprint,
  GitBranch,
  Search,
  Shield,
  Upload,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { LineageGraph } from '@/components/LineageGraph'
import PassportCard from '@/components/PassportCard'
import {
  getPassportByGaid,
  getPassportEdges,
  getPassportFamily,
  getPassports,
  getRegistryStats,
} from '@/lib/mockApi'

const featureCards = [
  {
    icon: Shield,
    title: 'Identity you can verify',
    description:
      'Every model or agent carries a deterministic passport with checksums, ownership, and release evidence.',
  },
  {
    icon: Search,
    title: 'Operational verification',
    description:
      'Review checksum drift, runtime mismatch, and release gates before anything moves into production.',
  },
  {
    icon: GitBranch,
    title: 'Lineage with receipts',
    description:
      'Trace from a root model into every derivative model and downstream agent without losing provenance.',
  },
]

export function LandingPage() {
  const stats = getRegistryStats()
  const featuredPassports = getPassports().slice(0, 3)
  const focusPassport = getPassportByGaid('gaid-policy-intake-copilot') ?? featuredPassports[0]
  const family = getPassportFamily(focusPassport.gaid)
  const edges = getPassportEdges(family)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12 lg:pt-24 space-y-14 w-full">
      <section className="grid grid-cols-1 xl:grid-cols-[1.25fr_0.9fr] gap-8 items-center">
        <div className="space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#2a1f55]/30 backdrop-blur-md border border-[#f1ebdf]/10 shadow-sm">
            <span className="flex h-2 w-2 rounded-full bg-[#008190] animate-pulse" />
            <span className="text-sm font-medium text-[#f1ebdf]">
              Mapping Forkit Core to the provided frontend system
            </span>
          </div>

          <div className="space-y-6">
            <h1 className="text-5xl md:text-7xl font-extrabold text-[#f1ebdf] tracking-tight leading-[1.05]">
              Give Forkit Core a{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#008190] via-[#6aa7ab] to-[#f49355]">
                production-grade passport console.
              </span>
            </h1>
            <p className="text-xl text-dark-text-secondary max-w-3xl leading-relaxed">
              This `/web` app now follows the visual language of the provided
              `forkit_dev_open_source` frontend while focusing it on the Forkit Core
              registry: landing, dashboard, passport list, detail, create, verify,
              and lineage.
            </p>
          </div>

          <div className="flex flex-wrap gap-4">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-[#008190] to-[#2a1f55] text-[#f1ebdf] font-bold rounded-xl shadow-lg hover:from-[#008190]/90 hover:to-[#2a1f55]/90 transition-all transform hover:scale-[1.02]"
            >
              Open Dashboard
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/passports/create"
              className="inline-flex items-center gap-2 px-6 py-3.5 border border-[#f1ebdf]/10 rounded-xl text-[#f1ebdf] hover:bg-[#f1ebdf]/5 transition-colors"
            >
              <Upload className="w-4 h-4" />
              Create Passport
            </Link>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
              <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
                Passports
              </div>
              <div className="mt-2 text-3xl font-bold text-[#f1ebdf]">{stats.total}</div>
            </div>
            <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
              <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
                Verified
              </div>
              <div className="mt-2 text-3xl font-bold text-emerald-400">{stats.verified}</div>
            </div>
            <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
              <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
                Models
              </div>
              <div className="mt-2 text-3xl font-bold text-[#f1ebdf]">{stats.models}</div>
            </div>
            <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
              <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
                Attention
              </div>
              <div className="mt-2 text-3xl font-bold text-amber-300">{stats.attention}</div>
            </div>
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-4 bg-gradient-to-r from-[#008190]/20 via-[#2a1f55]/30 to-[#f49355]/20 rounded-[2rem] blur-2xl" />
          <div className="relative waterdrop-glass rounded-[2rem] p-8 border border-[#f1ebdf]/10 overflow-hidden">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#008190] to-[#2a1f55] flex items-center justify-center shadow-sm">
                <Fingerprint className="w-6 h-6 text-[#f1ebdf]" />
              </div>
              <div>
                <div className="text-lg font-semibold text-[#f1ebdf]">Registry Snapshot</div>
                <div className="text-sm text-dark-text-secondary">
                  Current focus: {focusPassport.name}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {[
                {
                  label: 'Focus Passport',
                  value: focusPassport.gaid,
                },
                {
                  label: 'Lineage Nodes',
                  value: `${family.length} connected passports`,
                },
                {
                  label: 'Latest Evidence',
                  value: focusPassport.metadata.evidence[0],
                },
              ].map((item) => (
                <div
                  key={item.label}
                  className="p-4 rounded-2xl bg-[#0B0F19]/60 border border-[#f1ebdf]/10"
                >
                  <div className="text-[11px] uppercase tracking-[0.2em] text-dark-text-secondary">
                    {item.label}
                  </div>
                  <div className="mt-2 text-sm text-[#f1ebdf] break-words">{item.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {featureCards.map((feature) => (
          <div
            key={feature.title}
            className="waterdrop-glass rounded-[2rem] p-6 border border-[#f1ebdf]/10"
          >
            <div className="w-12 h-12 rounded-2xl bg-[#f1ebdf]/5 border border-[#f1ebdf]/10 flex items-center justify-center mb-5">
              <feature.icon className="w-6 h-6 text-[#6aa7ab]" />
            </div>
            <h2 className="text-xl font-semibold text-[#f1ebdf] mb-3">{feature.title}</h2>
            <p className="text-dark-text-secondary leading-relaxed">{feature.description}</p>
          </div>
        ))}
      </section>

      <section className="waterdrop-glass rounded-[2rem] p-6 md:p-8 border border-[#f1ebdf]/10">
        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 mb-8">
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
              Lineage Preview
            </div>
            <h2 className="text-3xl font-bold text-[#f1ebdf] mt-2">
              Forkit Core lineage mapped into the provided UI system
            </h2>
            <p className="text-dark-text-secondary mt-3 max-w-3xl">
              The graph below uses the mock Forkit Core passports but presents them in
              the same glass-panel, dark-console language as the provided reference app.
            </p>
          </div>
          <Link
            to={`/lineage?id=${focusPassport.gaid}`}
            className="text-[#6aa7ab] font-semibold hover:text-[#f1ebdf] transition-colors"
          >
            Open full lineage
          </Link>
        </div>
        <LineageGraph passports={family} edges={edges} focusGaid={focusPassport.gaid} />
      </section>

      <section className="space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
              Featured Passports
            </div>
            <h2 className="text-3xl font-bold text-[#f1ebdf] mt-2">
              Core registry entries ready for review
            </h2>
          </div>
          <Link
            to="/passports"
            className="text-[#6aa7ab] font-semibold hover:text-[#f1ebdf] transition-colors"
          >
            Browse all passports
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {featuredPassports.map((passport) => (
            <PassportCard key={passport.gaid} passport={passport} />
          ))}
        </div>
      </section>
    </div>
  )
}
