import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import PassportCard from '@/components/PassportCard'
import { cn } from '@/lib/utils'
import { fetchApi } from '@/lib/api'
import { usePageTitle } from '@/hooks/usePageTitle'
import type { Passport, PassportType, VerificationStatus } from '@/types'

export function PassportListPage() {
  usePageTitle('Registry')
  const [passports, setPassports] = useState<Passport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [typeFilter, setTypeFilter] = useState<'all' | PassportType>('all')
  const [statusFilter, setStatusFilter] = useState<'all' | VerificationStatus>('all')

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchApi<{ passports: Passport[] }>('/v1/passports')
        setPassports(data.passports ?? [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load the registry')
      } finally {
        setLoading(false)
      }
    }

    void load()
  }, [])
  const modelCount = passports.filter((passport) => passport.passportType === 'model').length
  const agentCount = passports.filter((passport) => passport.passportType === 'agent').length
  const verifiedCount = passports.filter(
    (passport) => passport.verificationStatus === 'verified',
  ).length
  const filteredPassports = passports.filter((passport) => {
    const matchesType = typeFilter === 'all' || passport.passportType === typeFilter
    const matchesStatus =
      statusFilter === 'all' || passport.verificationStatus === statusFilter

    return matchesType && matchesStatus
  })

  return (
    <div className="mx-auto w-full max-w-7xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold tracking-tight text-text">Registry</h1>
          <p className="mt-1 text-muted">
            Browse every current passport, then narrow the registry by record type or verification state before you inspect a record.
          </p>
        </div>
        <div className="flex flex-wrap gap-4 text-sm font-semibold">
          <Link to="/search" className="section-link">
            Search and filter registry
          </Link>
          <Link to="/registry/stats" className="section-link">
            Open registry stats
          </Link>
        </div>
      </div>

      <div className="rounded-[2rem] border border-border/80 p-6 waterdrop-glass">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <div className="rounded-[1.5rem] border border-border bg-surface-soft px-5 py-4">
            <div className="eyebrow">Total</div>
            <div className="mt-2 text-3xl font-bold text-text">{passports.length}</div>
          </div>
          <div className="rounded-[1.5rem] border border-border bg-surface-soft px-5 py-4">
            <div className="eyebrow">Models</div>
            <div className="mt-2 text-3xl font-bold text-primary">{modelCount}</div>
          </div>
          <div className="rounded-[1.5rem] border border-border bg-surface-soft px-5 py-4">
            <div className="eyebrow">Agents</div>
            <div className="mt-2 text-3xl font-bold text-text">{agentCount}</div>
          </div>
          <div className="rounded-[1.5rem] border border-border bg-surface-soft px-5 py-4">
            <div className="eyebrow">Verified</div>
            <div className="mt-2 text-3xl font-bold text-accent">{verifiedCount}</div>
          </div>
        </div>

        <div className="mt-5 grid gap-5 border-t border-border/70 pt-5 lg:grid-cols-[1.05fr_1.05fr_0.9fr]">
          <div>
            <div className="eyebrow mb-3">Browse by type</div>
            <div className="flex flex-wrap gap-2">
              {[
                { label: 'All passports', value: 'all' },
                { label: 'ModelPassport', value: 'model' },
                { label: 'AgentPassport', value: 'agent' },
              ].map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setTypeFilter(option.value as 'all' | PassportType)}
                  className={cn(
                    'rounded-full border px-4 py-2 text-sm font-semibold transition-all',
                    typeFilter === option.value
                      ? 'border-primary/25 bg-primary text-[#f1ebdf] shadow-[0_10px_20px_rgba(42,31,85,0.18)]'
                      : 'border-border bg-surface-soft text-text hover:border-primary/25 hover:bg-primary/5',
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="eyebrow mb-3">Verification state</div>
            <div className="flex flex-wrap gap-2">
              {[
                { label: 'All states', value: 'all' },
                { label: 'Verified', value: 'verified' },
                { label: 'Warning', value: 'warning' },
                { label: 'Pending', value: 'pending' },
              ].map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() =>
                    setStatusFilter(option.value as 'all' | VerificationStatus)
                  }
                  className={cn(
                    'rounded-full border px-4 py-2 text-sm font-semibold transition-all',
                    statusFilter === option.value
                      ? 'border-accent/25 bg-accent text-[#f1ebdf] shadow-[0_10px_20px_rgba(0,129,144,0.18)]'
                      : 'border-border bg-surface-soft text-text hover:border-accent/25 hover:bg-accent/5',
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col justify-between rounded-[1.5rem] border border-border bg-surface-soft px-5 py-4">
            <div>
              <div className="eyebrow">Browse results</div>
              <div className="mt-2 text-2xl font-bold text-text">{filteredPassports.length}</div>
              <div className="mt-1 text-sm text-muted">
                Registry keeps the full browse view. Use Search for direct text lookup.
              </div>
            </div>
            <Link to="/search" className="mt-4 section-link text-sm font-semibold">
              Open Search
            </Link>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center rounded-[2rem] border border-border/80 p-16 waterdrop-glass">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : error ? (
        <div className="rounded-[2rem] border border-semantic-danger/20 bg-semantic-danger/8 p-8 text-semantic-danger">
          {error}
        </div>
      ) : filteredPassports.length === 0 ? (
        <div className="rounded-[2rem] border border-border/80 p-16 text-center waterdrop-glass">
          <div className="text-xl font-semibold text-text">No passports match the current browse filters.</div>
          <div className="mt-2 text-muted">
            Adjust the registry filters or use Search for a direct text query.
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredPassports.map((passport) => (
            <PassportCard key={passport.id} passport={passport} />
          ))}
        </div>
      )}
    </div>
  )
}
