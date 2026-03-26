import { GitBranch, Layers } from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { LineageGraph } from '@/components/LineageGraph'
import {
  getPassportByGaid,
  getPassportEdges,
  getPassportFamily,
  getPassports,
} from '@/lib/mockApi'

export function LineagePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const passports = getPassports()
  const selectedId =
    searchParams.get('id') || 'gaid-policy-intake-copilot'
  const focusPassport = getPassportByGaid(selectedId) ?? passports[0]
  const family = getPassportFamily(focusPassport.gaid)
  const edges = getPassportEdges(family)
  const descendants = family.filter(
    (passport) =>
      passport.parentPassportGaid === focusPassport.gaid ||
      passport.modelPassportGaid === focusPassport.gaid,
  )

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 w-full">
      <div>
        <h1 className="text-3xl font-bold text-[#f1ebdf] tracking-tight">Lineage</h1>
        <p className="text-dark-text-secondary mt-1">
          Explore how the mapped Forkit Core passports inherit from root models, derived branches, and linked agents.
        </p>
      </div>

      <Card className="border border-[#f1ebdf]/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-[#6aa7ab]" />
            Focus Passport
          </CardTitle>
        </CardHeader>
        <CardContent>
          <select
            value={focusPassport.gaid}
            onChange={(event) => setSearchParams({ id: event.target.value })}
            className="w-full px-4 py-3 border border-[#f1ebdf]/10 rounded-xl bg-white/5 text-[#f1ebdf] focus:outline-none focus:ring-2 focus:ring-[#008190]"
          >
            {passports.map((passport) => (
              <option key={passport.gaid} value={passport.gaid}>
                {passport.name}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
          <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
            Family Nodes
          </div>
          <div className="mt-2 text-3xl font-bold text-[#f1ebdf]">{family.length}</div>
        </div>
        <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
          <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
            Descendants
          </div>
          <div className="mt-2 text-3xl font-bold text-[#f1ebdf]">{descendants.length}</div>
        </div>
        <div className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10">
          <div className="text-xs uppercase tracking-[0.2em] text-dark-text-secondary">
            Last Verified
          </div>
          <div className="mt-2 text-sm font-semibold text-[#f1ebdf]">
            {new Date(focusPassport.metadata.lastVerifiedAt).toLocaleString()}
          </div>
        </div>
      </section>

      <Card className="border border-[#f1ebdf]/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-[#6aa7ab]" />
            Lineage Graph
          </CardTitle>
        </CardHeader>
        <CardContent>
          <LineageGraph passports={family} edges={edges} focusGaid={focusPassport.gaid} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {family.map((passport) => (
          <Link
            key={passport.gaid}
            to={`/passports/${passport.gaid}`}
            className="waterdrop-glass rounded-2xl p-5 border border-[#f1ebdf]/10 hover:border-[#6aa7ab]/30 transition-colors"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-lg font-semibold text-[#f1ebdf]">{passport.name}</div>
                <div className="text-sm text-dark-text-secondary mt-1">{passport.gaid}</div>
              </div>
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
          </Link>
        ))}
      </div>
    </div>
  )
}
