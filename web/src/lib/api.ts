import { mockFetchApi } from './mockApi'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}) {
  return (await mockFetchApi(endpoint, options)) as T
}
