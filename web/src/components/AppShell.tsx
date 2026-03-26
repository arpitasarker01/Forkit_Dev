import { Shield } from 'lucide-react'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { cn } from '@/lib/utils'

const navItems = [
  { label: 'Landing', path: '/' },
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Passport List', path: '/passports' },
  { label: 'Verify', path: '/verify' },
  { label: 'Lineage', path: '/lineage' },
]

export function AppShell() {
  return (
    <div className="min-h-screen bg-[#0B0F19] flex flex-col relative overflow-hidden transition-colors duration-300">
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute inset-0 bg-grid-pattern opacity-40" />
        <div className="absolute top-[-10%] left-[-10%] w-[800px] h-[800px] bg-[#008190]/20 rounded-full mix-blend-screen blur-[120px] animate-heartbeat" />
        <div className="absolute top-[20%] right-[-10%] w-[600px] h-[600px] bg-[#f49355]/10 rounded-full mix-blend-screen blur-[120px] animate-heartbeat animation-delay-2000" />
        <div className="absolute bottom-[-20%] left-[20%] w-[700px] h-[700px] bg-[#2a1f55]/30 rounded-full mix-blend-screen blur-[120px] animate-heartbeat animation-delay-4000" />
      </div>

      <header className="sticky top-0 z-50 waterdrop-glass">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 py-4 lg:flex-row lg:items-center lg:justify-between">
            <Link to="/" className="flex items-center gap-4 group">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#008190] to-[#2a1f55] flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
                <Shield className="w-6 h-6 text-[#f1ebdf]" strokeWidth={2} />
              </div>
              <div>
                <div className="font-extrabold text-3xl text-[#f1ebdf] tracking-tight">
                  Forkit Core
                </div>
                <div className="text-xs uppercase tracking-[0.25em] text-dark-text-secondary">
                  Passport Console Prototype
                </div>
              </div>
            </Link>

            <nav className="flex flex-wrap items-center gap-2">
              {navItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/'}
                  className={({ isActive }) =>
                    cn(
                      'px-4 py-2 rounded-full text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-dark-accent-primary/20 text-dark-accent-primary'
                        : 'text-dark-text-secondary hover:bg-[#f1ebdf]/5 hover:text-[#f1ebdf]',
                    )
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>

            <div className="flex items-center gap-3">
              <Link
                to="/passports/create"
                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-[#008190] to-[#2a1f55] text-[#f1ebdf] font-medium rounded-xl shadow-lg hover:from-[#008190]/90 hover:to-[#2a1f55]/90 transition-all transform hover:scale-[1.02]"
              >
                Create Passport
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 w-full flex flex-col relative z-10">
        <Outlet />
      </main>
    </div>
  )
}
