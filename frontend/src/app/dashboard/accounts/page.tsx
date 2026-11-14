"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { api, AccountOut } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { BookOpen, Plus, Search, Filter } from "lucide-react"

const ACCOUNT_TYPES = ["asset", "liability", "equity", "revenue", "expense"]

export default function AccountsPage() {
  const router = useRouter()
  const { accessToken } = useAuth()
  const [accounts, setAccounts] = useState<AccountOut[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [filter, setFilter] = useState("")
  const [filterType, setFilterType] = useState("")

  // Form state
  const [name, setName] = useState("")
  const [code, setCode] = useState("")
  const [type, setType] = useState("asset")
  const [subtype, setSubtype] = useState("")
  const [currency, setCurrency] = useState("SRD")
  const [description, setDescription] = useState("")
  const [formError, setFormError] = useState("")
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    if (!accessToken) {
      router.push("/login")
      return
    }
    loadAccounts()
  }, [accessToken, router])

  const loadAccounts = async () => {
    // Need a company selected - for now we'll need to handle this
    // This page requires a company context
    try {
      // We need a company ID - for demo, we'll try to get the first company
      const companies = await api.listCompanies()
      if (companies.length > 0) {
        const data = await api.listAccounts(companies[0].id)
        setAccounts(data)
      }
    } catch (err) {
      console.error("Failed to load accounts:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError("")
    setFormLoading(true)
    try {
      const companies = await api.listCompanies()
      if (companies.length === 0) throw new Error("No company found")
      await api.createAccount(companies[0].id, { code, name, type, subtype: subtype || undefined, currency })
      setShowCreate(false)
      setName("")
      setCode("")
      setType("asset")
      setSubtype("")
      setDescription("")
      loadAccounts()
    } catch (err: any) {
      setFormError(err.message || "Failed to create account")
    } finally {
      setFormLoading(false)
    }
  }

  const filteredAccounts = accounts.filter(acc => {
    const matchesFilter = acc.name.toLowerCase().includes(filter.toLowerCase()) ||
      acc.code.includes(filter)
    const matchesType = !filterType || acc.type === filterType
    return matchesFilter && matchesType
  })

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Chart of Accounts</h1>
            <p className="text-muted-foreground">Manage your company's accounts</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setShowCreate(!showCreate)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Account
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search accounts..."
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex gap-2">
                <Filter className="h-4 w-4 mt-1.5 text-muted-foreground" />
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="flex h-10 w-48 rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">All Types</option>
                  {ACCOUNT_TYPES.map(t => (
                    <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Create Account Form */}
        {showCreate && (
          <Card className="border-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Create New Account
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                {formError && <div className="text-sm text-destructive p-3 rounded-md bg-destructive/10">{formError}</div>}
                
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="code">Code *</Label>
                    <Input
                      id="code"
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      placeholder="1100"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="name">Name *</Label>
                    <Input
                      id="name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Bank Account"
                      required
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="type">Type *</Label>
                    <select
                      id="type"
                      value={type}
                      onChange={(e) => setType(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      {ACCOUNT_TYPES.map(t => (
                        <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="subtype">Subtype</Label>
                    <Input
                      id="subtype"
                      value={subtype}
                      onChange={(e) => setSubtype(e.target.value)}
                      placeholder="bank, cash, receivable..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="currency">Currency</Label>
                    <select
                      id="currency"
                      value={currency}
                      onChange={(e) => setCurrency(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="SRD">SRD</option>
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Optional description"
                  />
                </div>

                {formError && <div className="text-sm text-destructive">{formError}</div>}

                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => { setShowCreate(false); setFormError("") }}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={formLoading}>
                    {formLoading ? "Creating..." : "Create Account"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Accounts Table */}
        <Card>
          <CardHeader>
            <CardTitle>Accounts ({filteredAccounts.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {filteredAccounts.length === 0 ? (
              <div className="text-center py-12">
                <BookOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No accounts found</h3>
                <p className="text-muted-foreground mb-4">Create your first account to get started</p>
                <Button onClick={() => setShowCreate(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Account
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-muted-foreground border-b">
                      <th className="pb-3 font-medium">Code</th>
                      <th className="pb-3 font-medium">Name</th>
                      <th className="pb-3 font-medium">Type</th>
                      <th className="pb-3 font-medium">Subtype</th>
                      <th className="pb-3 font-medium">Currency</th>
                      <th className="pb-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAccounts.map((acc) => (
                      <tr key={acc.id} className="border-b last:border-b-0 hover:bg-muted/50">
                        <td className="py-3 font-mono text-sm">{acc.code}</td>
                        <td className="py-3 font-medium">{acc.name}</td>
                        <td className="py-3">
                          <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-muted">
                            {acc.type.charAt(0).toUpperCase() + acc.type.slice(1)}
                          </span>
                        </td>
                        <td className="py-3 text-sm text-muted-foreground">{acc.subtype || "-"}</td>
                        <td className="py-3">{acc.currency}</td>
                        <td className="py-3">
                          <span className={acc.is_active ? "text-green-600" : "text-red-600"}>
                            {acc.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}