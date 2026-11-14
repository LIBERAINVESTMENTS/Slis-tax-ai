"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { ArrowLeft, Building2 } from "lucide-react"

export default function NewCompanyPage() {
  const router = useRouter()
  const { accessToken } = useAuth()
  const [name, setName] = useState("")
  const [slug, setSlug] = useState("")
  const [country, setCountry] = useState("SR")
  const [currency, setCurrency] = useState("SRD")
  const [fiscalYearStartMonth, setFiscalYearStartMonth] = useState(1)
  const [taxRegime, setTaxRegime] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!accessToken) {
      router.push("/login")
    }
  }, [accessToken, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const company = await api.createCompany({ name, slug, country, currency, fiscal_year_start_month: fiscalYearStartMonth, tax_regime: taxRegime || undefined })
      router.push(`/dashboard/companies/${company.id}`)
      router.refresh()
    } catch (err: any) {
      setError(err.message || "Failed to create company")
    } finally {
      setLoading(false)
    }
  }

  const autoSlug = (value: string) => {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "")
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/companies">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Building2 className="h-6 w-6" />
              Create Company
            </h1>
            <p className="text-muted-foreground">Set up a new business entity</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Company Details</CardTitle>
            <CardDescription>Enter the basic information for your new company</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="text-sm text-destructive p-3 rounded-md bg-destructive/10">{error}</div>
              )}

              <div className="space-y-2">
                <Label htmlFor="name">Company Name *</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value)
                    if (!slug || slug === autoSlug(name)) {
                      setSlug(autoSlug(e.target.value))
                    }
                  }}
                  placeholder="My Company Inc."
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="slug">Slug *</Label>
                <Input
                  id="slug"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  placeholder="my-company-inc"
                  required
                  pattern="^[a-z0-9-]+$"
                />
                <p className="text-xs text-muted-foreground">URL-friendly identifier (lowercase, numbers, hyphens only)</p>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="country">Country *</Label>
                  <select
                    id="country"
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="SR">Suriname (SR)</option>
                    <option value="US">United States (US)</option>
                    <option value="NL">Netherlands (NL)</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="currency">Currency *</Label>
                  <select
                    id="currency"
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="SRD">SRD - Surinamese Dollar</option>
                    <option value="USD">USD - US Dollar</option>
                    <option value="EUR">EUR - Euro</option>
                  </select>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="fiscalYearStartMonth">Fiscal Year Start Month *</Label>
                  <select
                    id="fiscalYearStartMonth"
                    value={fiscalYearStartMonth}
                    onChange={(e) => setFiscalYearStartMonth(Number(e.target.value))}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    {[1,2,3,4,5,6,7,8,9,10,11,12].map(m => (
                      <option key={m} value={m}>
                        {new Date(2024, m-1).toLocaleString('default', { month: 'long' })}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="taxRegime">Tax Regime</Label>
                  <select
                    id="taxRegime"
                    value={taxRegime}
                    onChange={(e) => setTaxRegime(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="">Select tax regime...</option>
                    <option value="suriname_corporate">Suriname Corporate</option>
                    <option value="suriname_personal">Suriname Personal</option>
                  </select>
                </div>
              </div>
            </form>
          </CardContent>
          <CardFooter className="flex justify-end gap-2">
            <Link href="/dashboard/companies">
              <Button type="button" variant="outline">Cancel</Button>
            </Link>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Company"}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </Layout>
  )
}