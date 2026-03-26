import { useEffect, useState } from 'react'
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle,
  Clock,
  Database,
  Fingerprint,
  Search,
  Shield,
  User,
} from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { fetchApi } from '@/lib/api'
import { getPassports } from '@/lib/mockApi'
import type { Passport } from '@/types'

export function VerifyPassportPage() {
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const initialId = queryParams.get('id') || ''

  const [searchId, setSearchId] = useState(initialId)
  const [isSearching, setIsSearching] = useState(false)
  const [passport, setPassport] = useState<Passport | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!initialId) {
      return
    }

    void performSearch(initialId)
  }, [initialId])

  async function performSearch(idToSearch: string) {
    if (!idToSearch.trim()) {
      return
    }

    setIsSearching(true)
    setError('')
    setPassport(null)

    try {
      const data = (await fetchApi(`/v1/passports/${idToSearch.trim()}`)) as Passport
      setPassport(data)
    } catch {
      setError('No passport found with that ID.')
    } finally {
      setIsSearching(false)
    }
  }

  const handleSearch = async (event: React.FormEvent) => {
    event.preventDefault()
    await performSearch(searchId)
  }

  const quickPicks = getPassports().slice(0, 4)

  return (
    <div className="min-h-screen text-[#f1ebdf] flex flex-col items-center py-16 px-4 relative">
      <Link
        to="/"
        className="absolute top-8 left-8 text-dark-text-secondary hover:text-[#f1ebdf] flex items-center gap-2 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Home
      </Link>

      <div className="w-full max-w-5xl space-y-8 mt-8">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-dark-accent-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Shield className="w-8 h-8 text-dark-accent-primary" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight">Passport Verification</h1>
          <p className="text-dark-text-secondary text-lg max-w-2xl mx-auto">
            Enter a Forkit Core passport GAID to inspect its cryptographic seal,
            linked lineage, and operational release posture.
          </p>
        </div>

        <Card className="bg-dark-bg-secondary/50 border-[#f1ebdf]/10 backdrop-blur-sm">
          <CardContent className="pt-6">
            <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-text-secondary" />
                <Input
                  value={searchId}
                  onChange={(event) => setSearchId(event.target.value)}
                  placeholder="Enter Passport ID (e.g., gaid-policy-intake-copilot)"
                  className="w-full pl-10 bg-dark-bg border-[#f1ebdf]/10 h-12 text-lg focus:ring-dark-accent-primary"
                />
              </div>
              <Button
                type="submit"
                disabled={isSearching || !searchId.trim()}
                className="h-12 px-8 bg-dark-accent-primary hover:bg-dark-accent-primary/90 text-dark-bg font-medium text-lg"
              >
                {isSearching ? 'Verifying...' : 'Verify'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-6">
          <div className="space-y-6">
            {error ? (
              <div className="bg-semantic-danger/10 border border-semantic-danger/20 rounded-xl p-6 text-center">
                <AlertTriangle className="w-8 h-8 text-semantic-danger mx-auto mb-3" />
                <h3 className="text-lg font-medium text-semantic-danger mb-1">
                  Verification Failed
                </h3>
                <p className="text-semantic-danger/80">{error}</p>
              </div>
            ) : null}

            {passport ? (
              <Card className="bg-dark-bg border-[#f1ebdf]/10 overflow-hidden relative">
                <div className="absolute top-0 right-0 w-64 h-64 bg-dark-accent-primary/5 blur-[100px] rounded-full pointer-events-none" />
                <CardHeader className="border-b border-[#f1ebdf]/5 pb-6">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <CardTitle className="text-2xl">{passport.name}</CardTitle>
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
                      <p className="text-dark-text-secondary">{passport.description}</p>
                    </div>
                    <div className="w-12 h-12 rounded-xl bg-dark-bg-secondary flex items-center justify-center shrink-0 border border-[#f1ebdf]/5">
                      <Fingerprint className="w-6 h-6 text-dark-accent-primary" />
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-6 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="text-sm font-medium text-[#f1ebdf]/80 uppercase tracking-wider">
                        Identity Details
                      </h4>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-dark-bg-secondary/50 rounded-lg border border-[#f1ebdf]/5">
                          <span className="text-sm text-dark-text-secondary flex items-center gap-2">
                            <Fingerprint className="w-4 h-4" /> Passport ID
                          </span>
                          <span className="text-sm font-mono text-[#f1ebdf]">
                            {passport.gaid}
                          </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-dark-bg-secondary/50 rounded-lg border border-[#f1ebdf]/5">
                          <span className="text-sm text-dark-text-secondary flex items-center gap-2">
                            <Database className="w-4 h-4" /> Region
                          </span>
                          <span className="text-sm text-[#f1ebdf] capitalize">
                            {passport.metadata.region}
                          </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-dark-bg-secondary/50 rounded-lg border border-[#f1ebdf]/5">
                          <span className="text-sm text-dark-text-secondary flex items-center gap-2">
                            <User className="w-4 h-4" /> Owner
                          </span>
                          <span className="text-sm text-[#f1ebdf]">
                            {passport.ownerName}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="text-sm font-medium text-[#f1ebdf]/80 uppercase tracking-wider">
                        Status & Compliance
                      </h4>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-dark-bg-secondary/50 rounded-lg border border-[#f1ebdf]/5">
                          <span className="text-sm text-dark-text-secondary flex items-center gap-2">
                            <Shield className="w-4 h-4" /> Risk Level
                          </span>
                          <Badge
                            variant={
                              passport.metadata.riskLevel === 'High'
                                ? 'danger'
                                : passport.metadata.riskLevel === 'Medium'
                                  ? 'warning'
                                  : 'success'
                            }
                          >
                            {passport.metadata.riskLevel}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-dark-bg-secondary/50 rounded-lg border border-[#f1ebdf]/5">
                          <span className="text-sm text-dark-text-secondary flex items-center gap-2">
                            <CheckCircle className="w-4 h-4" /> Governance
                          </span>
                          <span className="text-sm text-[#f1ebdf]">
                            {passport.metadata.governanceScore}
                          </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-dark-bg-secondary/50 rounded-lg border border-[#f1ebdf]/5">
                          <span className="text-sm text-dark-text-secondary flex items-center gap-2">
                            <Clock className="w-4 h-4" /> Last Updated
                          </span>
                          <span className="text-sm text-[#f1ebdf]">
                            {new Date(passport.updatedAt).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-sm font-medium text-[#f1ebdf]/80 uppercase tracking-wider">
                      Verification Checks
                    </h4>
                    {passport.verificationChecks.map((check) => (
                      <div
                        key={check.label}
                        className="p-3 bg-dark-bg-secondary/50 rounded-lg border border-[#f1ebdf]/5"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div className="text-sm font-semibold text-[#f1ebdf]">
                            {check.label}
                          </div>
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
                  </div>
                </CardContent>
              </Card>
            ) : null}
          </div>

          <div className="space-y-6">
            <Card className="bg-dark-bg-secondary/50 border-[#f1ebdf]/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Quick Picks</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {quickPicks.map((item) => (
                  <button
                    key={item.gaid}
                    type="button"
                    onClick={() => {
                      setSearchId(item.gaid)
                      void performSearch(item.gaid)
                    }}
                    className="w-full text-left p-3 rounded-xl border border-[#f1ebdf]/10 hover:border-[#6aa7ab]/30 bg-dark-bg-secondary/50 transition-colors"
                  >
                    <div className="text-sm font-semibold text-[#f1ebdf]">{item.name}</div>
                    <div className="text-xs text-dark-text-secondary mt-1">{item.gaid}</div>
                  </button>
                ))}
              </CardContent>
            </Card>

            {passport ? (
              <Card className="bg-dark-bg-secondary/50 border-[#f1ebdf]/10 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle>Evidence Bundle</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {passport.metadata.evidence.map((item) => (
                    <div
                      key={item}
                      className="p-3 rounded-xl border border-[#f1ebdf]/10 bg-dark-bg-secondary/50 text-sm text-dark-text-secondary"
                    >
                      {item}
                    </div>
                  ))}
                </CardContent>
              </Card>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
