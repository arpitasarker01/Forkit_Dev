import { Activity, AlertTriangle, Box, Clock3, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import type { Passport } from '@/types'

interface PassportCardProps {
  passport: Passport
}

export default function PassportCard({ passport }: PassportCardProps) {
  const isAgent = passport.passportType === 'agent'

  const StatusIcon =
    passport.verificationStatus === 'verified'
      ? ShieldCheck
      : passport.verificationStatus === 'monitoring'
        ? Clock3
        : AlertTriangle

  const statusColor =
    passport.verificationStatus === 'verified'
      ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30 border-emerald-200 dark:border-emerald-800/50'
      : passport.verificationStatus === 'monitoring'
        ? 'text-amber-600 dark:text-amber-300 bg-amber-100 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800/50'
        : passport.verificationStatus === 'draft'
          ? 'text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700/50'
          : 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30 border-red-200 dark:border-red-800/50'

  return (
    <div className="group relative waterdrop-glass border border-[#f1ebdf]/10 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden flex flex-col h-full transform hover:-translate-y-1">
      <div className="h-1.5 w-full bg-gradient-to-r from-[#008190] via-[#2a1f55] to-[#f49355] opacity-90" />

      <div className="p-6 flex-1 flex flex-col">
        <div className="flex justify-between items-start mb-5">
          <div className="flex items-start gap-3">
            <div className="p-2.5 bg-white/5 rounded-xl border border-[#f1ebdf]/10 shadow-sm">
              {isAgent ? (
                <Activity className="w-6 h-6 text-[#6aa7ab]" />
              ) : (
                <Box className="w-6 h-6 text-[#6aa7ab]" />
              )}
            </div>
            <div>
              <h3 className="font-bold text-[#f1ebdf] text-lg leading-tight line-clamp-1 mb-1">
                {passport.name}
              </h3>
              <p className="text-xs text-dark-text-secondary font-mono truncate max-w-[210px] bg-[#f1ebdf]/5 px-2 py-0.5 rounded-md">
                {passport.gaid}
              </p>
            </div>
          </div>

          <div
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-bold capitalize shadow-sm',
              statusColor,
            )}
          >
            <StatusIcon className="w-3.5 h-3.5" />
            {passport.verificationStatus}
          </div>
        </div>

        <p className="text-sm text-dark-text-secondary line-clamp-3 mb-6 flex-1 leading-relaxed">
          {passport.description}
        </p>

        <div className="grid grid-cols-2 gap-4 pt-5 border-t border-[#f1ebdf]/10 mt-auto">
          <div>
            <p className="text-[10px] text-dark-text-secondary mb-1 uppercase tracking-widest font-bold">
              Type
            </p>
            <span className="text-sm font-semibold text-[#f1ebdf] capitalize truncate">
              {isAgent ? 'Autonomous Agent' : 'Language Model'}
            </span>
          </div>

          <div>
            <p className="text-[10px] text-dark-text-secondary mb-1 uppercase tracking-widest font-bold">
              Owner
            </p>
            <p className="text-sm font-semibold text-[#f1ebdf] truncate">
              {passport.ownerName}
            </p>
          </div>
        </div>
      </div>

      <div className="px-6 py-4 bg-white/5 border-t border-[#f1ebdf]/10 flex justify-between items-center group-hover:bg-[#008190]/5 transition-colors">
        <div className="flex items-center gap-3">
          {isAgent ? (
            <div
              className="flex items-center gap-2"
              title={`Last check-in: ${
                passport.liveness?.lastCheckinAt
                  ? new Date(passport.liveness.lastCheckinAt).toLocaleString()
                  : 'Never'
              }`}
            >
              <div className="relative flex h-2 w-2">
                {passport.liveness?.checkinStatus === 'active' ? (
                  <>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500" />
                  </>
                ) : (
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
                )}
              </div>
              <span
                className={cn(
                  'text-[11px] font-medium uppercase tracking-wider',
                  passport.liveness?.checkinStatus === 'active'
                    ? 'text-teal-400'
                    : passport.liveness?.checkinStatus === 'silent'
                      ? 'text-amber-300'
                      : 'text-red-400',
                )}
              >
                Agent: {passport.liveness?.checkinStatus || 'offline'}
              </span>
            </div>
          ) : (
            <span className="text-[11px] font-medium text-dark-text-secondary uppercase tracking-wider">
              Governance {passport.metadata.governanceScore}
            </span>
          )}
        </div>
        <Link
          to={`/passports/${passport.gaid}`}
          className="text-sm font-bold text-[#6aa7ab] flex items-center gap-1.5 hover:text-[#f1ebdf] transition-colors"
        >
          View Details
        </Link>
      </div>
    </div>
  )
}
