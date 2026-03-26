import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 w-full">
      <div className="waterdrop-glass rounded-[2rem] p-12 border border-[#f1ebdf]/10 text-center">
        <h1 className="text-4xl font-bold text-[#f1ebdf]">Route not found</h1>
        <p className="text-dark-text-secondary mt-4">
          This screen is not part of the mapped Forkit Core console.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 mt-8 px-6 py-3 bg-gradient-to-r from-[#008190] to-[#2a1f55] text-[#f1ebdf] rounded-xl font-semibold"
        >
          Return to Landing
        </Link>
      </div>
    </div>
  )
}
