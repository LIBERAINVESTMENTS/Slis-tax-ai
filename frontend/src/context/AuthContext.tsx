"use client"

import { createContext, useContext, useState, ReactNode } from "react"
import { api } from "@/lib/api"
import { UserOut } from "./types"

interface AuthContextType {
  user: UserOut | null
  accessToken: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

function readStoredToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("access_token")
}

function readStoredUser(): UserOut | null {
  if (typeof window === "undefined") return null
  const raw = localStorage.getItem("user")
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserOut
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  // Initialize state synchronously from localStorage so protected pages see the
  // authenticated state on first render (no redirect race condition).
  const [user, setUser] = useState<UserOut | null>(readStoredUser)
  const [accessToken, setAccessToken] = useState<string | null>(readStoredToken)
  const [loading, setLoading] = useState(false)

  const login = async (email: string, password: string) => {
    const data = await api.login(email, password)
    localStorage.setItem("access_token", data.access_token)
    localStorage.setItem("refresh_token", data.refresh_token)
    localStorage.setItem("user", JSON.stringify(data.user))
    setAccessToken(data.access_token)
    setUser(data.user)
  }

  const register = async (email: string, password: string, fullName?: string) => {
    await api.register(email, password, fullName)
    // After registration, log in automatically
    const loginData = await api.login(email, password)
    localStorage.setItem("access_token", loginData.access_token)
    localStorage.setItem("refresh_token", loginData.refresh_token)
    localStorage.setItem("user", JSON.stringify(loginData.user))
    setAccessToken(loginData.access_token)
    setUser(loginData.user)
  }

  const logout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user")
    setAccessToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, accessToken, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth must be used within AuthProvider")
  return context
}