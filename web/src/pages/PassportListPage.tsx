import { useDeferredValue, useEffect, useState } from 'react'
import { Filter, Loader2, Search } from 'lucide-react'
import PassportCard from '@/components/PassportCard'
import { fetchApi } from '@/lib/api'
import type { Passport, PassportType, VerificationStatus } from '@/types'

export function PassportListPage() {
  const [passports, setPassports] = useState<Passport[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<'all' | PassportType>('all')
  const [statusFilter, setStatusFilter] = useState<'all' | VerificationStatus>('all')
  const deferredSearch = useDeferredValue(searchQuery.trim().toLowerCase())

  useEffect(() => {
    const load = async () => {
      const data = await fetchApi<{ passports: Passport[] }>('/v1/passports')
      setPassports(data.passports ?? [])
      setLoading(false)
    }

    void load()
  }, [])

  const filteredPassports = passports.filter((passport) => {
    const matchesSearch =
      deferredSearch.length === 0 ||
      [
        passport.name,
        passport.gaid,
        passport.description,
        passport.ownerName,
        passport.organization,
      ]
        .join(' ')
        .toLowerCase()
        .includes(deferredSearch)

    const matchesType = typeFilter === 'all' || passport.passportType === typeFilter
    const matchesStatus =
      statusFilter === 'all' || passport.verificationStatus === statusFilter

    return matchesSearch && matchesType && matchesStatus
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 w-full">
      <div>
        <h1 className="text-3xl font-bold text-[#f1ebdf] tracking-tight">Passport List</h1>
        <p className="text-dark-text-secondary mt-1">
          Filter the mapped registry by passport type, verification state, and search terms.
        </p>
      </div>

      <div className="waterdrop-glass rounded-[2rem] p-6 border border-[#f1ebdf]/10">
        <div className="grid grid-cols-1 lg:grid-cols-[1.5fr_0.8fr_0.8fr] gap-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-dark-text-secondary" />
            </div>
            <input
              type="text"
              placeholder="Search passports, owners, or GAIDs..."
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              className="block w-full pl-11 pr-4 py-3 border border-[#f1ebdf]/10 rounded-xl leading-5 bg-white/5 backdrop-blur-sm text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-2 focus:ring-[#008190] focus:border-transparent sm:text-sm transition-all shadow-sm"
            />
          </div>

          <select
            value={typeFilter}
            onChange={(event) => setTypeFilter(event.target.value as 'all' | PassportType)}
            className="px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] focus:outline-none focus:ring-2 focus:ring-[#008190]"
          >
            <option value="all">All types</option>
            <option value="model">Models</option>
            <option value="agent">Agents</option>
          </select>

          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value as 'all' | VerificationStatus)
            }
            className="px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] focus:outline-none focus:ring-2 focus:ring-[#008190]"
          >
            <option value="all">All statuses</option>
            <option value="verified">Verified</option>
            <option value="monitoring">Monitoring</option>
            <option value="draft">Draft</option>
            <option value="flagged">Flagged</option>
          </select>
        </div>

        <div className="flex items-center gap-2 mt-4 text-sm text-dark-text-secondary">
          <Filter className="w-4 h-4" />
          {filteredPassports.length} result{filteredPassports.length === 1 ? '' : 's'}
        </div>
      </div>

      {loading ? (
        <div className="waterdrop-glass rounded-[2rem] p-16 flex items-center justify-center border border-[#f1ebdf]/10">
          <Loader2 className="w-8 h-8 animate-spin text-[#6aa7ab]" />
        </div>
      ) : filteredPassports.length === 0 ? (
        <div className="waterdrop-glass rounded-[2rem] p-16 text-center border border-[#f1ebdf]/10">
          <div className="text-xl font-semibold text-[#f1ebdf]">No passports matched the current filters.</div>
          <div className="text-dark-text-secondary mt-2">
            Adjust the search or remove one of the filters to broaden the list.
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredPassports.map((passport) => (
            <PassportCard key={passport.gaid} passport={passport} />
          ))}
        </div>
      )}
    </div>
  )
}
