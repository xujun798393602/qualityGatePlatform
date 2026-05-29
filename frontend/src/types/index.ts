// Auth types
export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface TokenRefresh {
  refresh_token: string
}

// User types
export interface User {
  id: string
  username: string
  email: string
  name: string
  is_active: boolean
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface UserUpdate {
  username?: string
  email?: string
  is_active?: boolean
}

// Role types
export interface Role {
  id: string
  name: string
  description?: string
  permissions?: string[]
}

// Team types
export interface Team {
  id: string
  name: string
  description?: string
}

// System config types
export interface SystemConfig {
  [key: string]: any
}

// API response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
