import { useEffect, useState } from 'react'
import { FolderOpen, Loader2, Plus, Search, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import PassportCard from '@/components/PassportCard'
import { fetchApi } from '@/lib/api'
import { getRegistryStats } from '@/lib/mockApi'
import type { Passport } from '@/types'

export function DashboardPage() {
  const [passports, setPassports] = useState<Passport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const stats = getRegistryStats()

  useEffect(() => {
    const loadPassports = async () => {
      try {
        const data = await fetchApi<{ passports: Passport[] }>('/v1/passports/mine')
        setPassports(data.passports ?? [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load passports')
      } finally {
        setLoading(false)
      }
    }

    void loadPassports()
  }, [])

  const filteredPassports = passports.filter(
    (passport) =>
      passport.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      passport.gaid.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const watchlist = passports.filter(
    (passport) => passport.verificationStatus !== 'verified',
  )

  const latestVerified = [...passports]
    .sort(
      (left, right) =>
        Date.parse(right.metadata.lastVerifiedAt) -
        Date.parse(left.metadata.lastVerifiedAt),
    )
    .slice(0, 3)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 w-full">
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-[#f1ebdf] tracking-tight">
            Forkit Core Dashboard
          </h1>
          <p className="text-dark-text-secondary mt-1">
            Monitor the mapped mock registry, verification posture, and active lineage branches.
          </p>
        </div>

        <Link
          to="/passports/create"
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-[#008190] to-[#2a1f55] text-[#f1ebdf] font-medium rounded-xl shadow-lg hover:from-[#008190]/90 hover:to-[#2a1f55]/90 transition-all transform hover:scale-[1.02]"
        >
          <Plus className="w-5 h-5" />
          Register New Passport
        </Link>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
          <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
            Total
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
            Models / Agents
          </div>
          <div className="mt-2 text-3xl font-bold text-[#f1ebdf]">
            {stats.models}/{stats.agents}
          </div>
        </div>
        <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
          <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
            Attention
          </div>
          <div className="mt-2 text-3xl font-bold text-amber-300">{stats.attention}</div>
        </div>
      </section>

      <div className="grid grid-cols-1 xl:grid-cols-[1.4fr_0.85fr] gap-6">
        <div className="space-y-6">
          <div className="relative max-w-xl">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-dark-text-secondary" />
            </div>
            <input
              type="text"
              placeholder="Search by name or GAID..."
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              className="block w-full pl-11 pr-4 py-3 border border-[#f1ebdf]/10 rounded-xl leading-5 bg-white/5 backdrop-blur-sm text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent sm:text-sm transition-all shadow-sm"
            />
          </div>

          {loading ? (
            <div className="waterdrop-glass rounded-[2rem] p-16 flex items-center justify-center border border-[#f1ebdf]/10">
              <Loader2 className="w-8 h-8 animate-spin text-[#6aa7ab]" />
            </div>
          ) : error ? (
            <div className="waterdrop-glass rounded-[2rem] p-8 border border-red-500/20 text-red-300">
              {error}
            </div>
          ) : filteredPassports.length === 0 ? (
            <div className="waterdrop-glass rounded-[2rem] p-16 text-center flex flex-col items-center justify-center border border-[#f1ebdf]/10">
              <div className="w-20 h-20 bg-[#2a1f55]/30 rounded-full flex items-center justify-center mb-6 shadow-inner">
                <FolderOpen className="w-10 h-10 text-[#6aa7ab]" />
              </div>
              <h3 className="text-2xl font-bold text-[#f1ebdf] mb-3">No passports found</h3>
              <p className="text-dark-text-secondary max-w-md mx-auto mb-8 leading-relaxed">
                Nothing matched the current dashboard search. Try another query or register a new passport.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredPassports.map((passport) => (
                <PassportCard key={passport.gaid} passport={passport} />
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="waterdrop-glass rounded-[2rem] p-6 border border-[#f1ebdf]/10">
            <div className="flex items-center gap-3 mb-5">
              <ShieldCheck className="w-5 h-5 text-[#6aa7ab]" />
              <h2 className="text-lg font-semibold text-[#f1ebdf]">Latest verification runs</h2>
            </div>
            <div className="space-y-4">
              {latestVerified.map((passport) => (
                <Link
                  key={passport.gaid}
                  to={`/verify?id=${passport.gaid}`}
                  className="block rounded-2xl border border-[#f1ebdf]/10 bg-[#0B0F19]/60 p-4 hover:border-[#6aa7ab]/30 transition-colors"
                >
                  <div className="text-sm font-semibold text-[#f1ebdf]">{passport.name}</div>
                  <div className="text-xs text-dark-text-secondary mt-1">
                    Verified {new Date(passport.metadata.lastVerifiedAt).toLocaleString()}
                  </div>
                </Link>
              ))}
            </div>
          </div>

          <div className="waterdrop-glass rounded-[2rem] p-6 border border-[#f1ebdf]/10">
            <div className="flex items-center gap-3 mb-5">
              <Search className="w-5 h-5 text-[#f49355]" />
              <h2 className="text-lg font-semibold text-[#f1ebdf]">Watchlist</h2>
            </div>
            <div className="space-y-4">
              {watchlist.map((passport) => (
                <Link
                  key={passport.gaid}
                  to={`/passports/${passport.gaid}`}
                  className="block rounded-2xl border border-[#f1ebdf]/10 bg-[#0B0F19]/60 p-4 hover:border-[#f49355]/30 transition-colors"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="text-sm font-semibold text-[#f1ebdf]">{passport.name}</div>
                      <div className="text-xs text-dark-text-secondary mt-1">
                        {passport.verificationChecks.find((check) => check.status !== 'pass')?.detail ??
                          'Requires operator review.'}
                      </div>
                    </div>
                    <span className="text-[10px] uppercase tracking-[0.2em] text-amber-300">
                      {passport.verificationStatus}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
