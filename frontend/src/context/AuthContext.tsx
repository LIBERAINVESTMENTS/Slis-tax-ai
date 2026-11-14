"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    const storedUser = localStorage.getItem("user")
    if (token && storedUser) {
      try {
        setAccessToken(token)
        setUser(JSON.parse(storedUser))
      } catch {
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        localStorage.removeItem("user")
      }
    }
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const data = await api.login(email, password)
    localStorage.setItem("access_token", data.access_token)
    localStorage.setItem("refresh_token", data.refresh_token)
    localStorage.setItem("user", JSON.stringify(data.user))
    setAccessToken(data.access_token)
    setUser(data.user)
  }

  const register = async (email: string, password: string, fullName?: string) => {
    const data = await api.register(email, password, fullName)
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