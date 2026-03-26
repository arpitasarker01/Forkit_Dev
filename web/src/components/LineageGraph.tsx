import { Activity, Cpu } from 'lucide-react'
import { useState } from 'react'
import type { Passport, PassportEdge } from '@/types'
import { cn } from '@/lib/utils'

type LineageGraphProps = {
  passports: Passport[]
  edges: PassportEdge[]
  focusGaid: string
}

function getPassportDepth(
  passport: Passport,
  passportsById: Map<string, Passport>,
  trail = new Set<string>(),
): number {
  if (trail.has(passport.gaid)) {
    return 0
  }

  const nextTrail = new Set(trail)
  nextTrail.add(passport.gaid)

  const parentDepth = passport.parentPassportGaid
    ? getPassportDepth(passportsById.get(passport.parentPassportGaid) ?? passport, passportsById, nextTrail) + 1
    : 0
  const modelDepth =
    passport.passportType === 'agent' && passport.modelPassportGaid
      ? getPassportDepth(passportsById.get(passport.modelPassportGaid) ?? passport, passportsById, nextTrail) + 1
      : passport.passportType === 'agent'
        ? 1
        : 0

  return Math.max(parentDepth, modelDepth)
}

export function LineageGraph({ passports, edges, focusGaid }: LineageGraphProps) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(focusGaid)
  const passportsById = new Map(passports.map((passport) => [passport.gaid, passport]))
  const grouped = passports.reduce<Record<number, Passport[]>>((accumulator, passport) => {
    const depth = getPassportDepth(passport, passportsById)

    if (!accumulator[depth]) {
      accumulator[depth] = []
    }

    accumulator[depth].push(passport)
    return accumulator
  }, {})

  const levels = Object.keys(grouped)
    .map(Number)
    .sort((left, right) => left - right)

  const positions = new Map<string, { x: number; y: number }>()
  levels.forEach((level, levelIndex) => {
    const column = grouped[level]
    const x =
      levels.length === 1 ? 50 : 12 + (76 / (levels.length - 1)) * levelIndex

    column.forEach((passport, rowIndex) => {
      const y = ((rowIndex + 1) / (column.length + 1)) * 78 + 11
      positions.set(passport.gaid, { x, y })
    })
  })

  const connectedNodes = new Set<string>()
  const connectedEdges = new Set<string>()

  if (hoveredNode) {
    const queue = [hoveredNode]

    while (queue.length > 0) {
      const current = queue.shift()

      if (!current || connectedNodes.has(current)) {
        continue
      }

      connectedNodes.add(current)

      edges.forEach((edge) => {
        if (edge.from === current || edge.to === current) {
          const key = `${edge.from}-${edge.to}-${edge.relation}`
          connectedEdges.add(key)

          if (!connectedNodes.has(edge.from)) {
            queue.push(edge.from)
          }

          if (!connectedNodes.has(edge.to)) {
            queue.push(edge.to)
          }
        }
      })
    }
  }

  return (
    <div className="w-full bg-[#0a0a0a] rounded-2xl border border-[#f1ebdf]/10 relative overflow-x-auto h-[500px] shadow-inner">
      <div className="min-w-[960px] h-full relative">
        <div className="absolute top-1/2 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#f1ebdf]/10 to-transparent blur-sm -translate-y-1/2 pointer-events-none" />
        <div className="absolute inset-0 bg-grid-pattern opacity-20" />

        <svg
          className="absolute inset-0 w-full h-full pointer-events-none"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
        >
          {edges.map((edge) => {
            const from = positions.get(edge.from)
            const to = positions.get(edge.to)

            if (!from || !to) {
              return null
            }

            const isHighlighted =
              connectedEdges.size === 0 ||
              connectedEdges.has(`${edge.from}-${edge.to}-${edge.relation}`)
            const dimmed = hoveredNode !== null && !isHighlighted
            const stroke =
              edge.relation === 'powered by' ? '#6aa7ab' : '#f49355'

            return (
              <path
                key={`${edge.from}-${edge.to}-${edge.relation}`}
                d={`M ${from.x} ${from.y} C ${(from.x + to.x) / 2} ${from.y}, ${(from.x + to.x) / 2} ${to.y}, ${to.x} ${to.y}`}
                stroke={stroke}
                strokeWidth={isHighlighted ? 0.75 : 0.4}
                strokeDasharray={edge.relation === 'powered by' ? '2 2' : 'none'}
                opacity={dimmed ? 0.18 : isHighlighted ? 0.95 : 0.4}
                fill="none"
                vectorEffect="non-scaling-stroke"
              />
            )
          })}
        </svg>

        {passports.map((passport) => {
          const position = positions.get(passport.gaid)

          if (!position) {
            return null
          }

          const highlighted =
            connectedNodes.size === 0 || connectedNodes.has(passport.gaid)
          const dimmed = hoveredNode !== null && !highlighted
          const isFocus = passport.gaid === focusGaid
          return (
            <div
              key={passport.gaid}
              className="absolute z-20"
              style={{
                left: `${position.x}%`,
                top: `${position.y}%`,
                transform: 'translate(-50%, -50%)',
              }}
              onMouseEnter={() => setHoveredNode(passport.gaid)}
              onMouseLeave={() => setHoveredNode(focusGaid)}
            >
              <div
                className={cn(
                  'w-52 rounded-2xl border p-4 backdrop-blur-md transition-all duration-300 cursor-pointer',
                  isFocus
                    ? 'border-emerald-400/60 bg-emerald-400/10 shadow-[0_0_24px_rgba(52,211,153,0.18)]'
                    : 'border-[#f1ebdf]/10 bg-[#151C2C]/80',
                  dimmed && 'opacity-35',
                  highlighted && !dimmed && 'shadow-lg',
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[#0B0F19] border border-[#f1ebdf]/10 flex items-center justify-center">
                    {passport.passportType === 'agent' ? (
                      <Activity className="w-5 h-5 text-[#6aa7ab]" />
                    ) : (
                      <Cpu className="w-5 h-5 text-[#f49355]" />
                    )}
                  </div>
                  <span className="text-[10px] uppercase tracking-[0.2em] text-dark-text-secondary">
                    {passport.passportType}
                  </span>
                </div>
                <div className="mt-3">
                  <div className="text-sm font-semibold text-[#f1ebdf]">{passport.name}</div>
                  <div className="text-[11px] text-dark-text-secondary mt-1">
                    {passport.gaid}
                  </div>
                  <div className="text-[11px] text-dark-text-secondary mt-2">
                    {passport.parentPassportGaid
                      ? 'Fork lineage attached'
                      : passport.modelPassportGaid
                        ? 'Backed by linked model'
                        : 'Root lineage'}
                  </div>
                </div>
                <div className="mt-3 flex items-center justify-between text-[10px] uppercase tracking-[0.2em]">
                  <span className="text-dark-text-secondary">
                    Governance {passport.metadata.governanceScore}
                  </span>
                  <span className="text-[#6aa7ab]">{passport.verificationStatus}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
