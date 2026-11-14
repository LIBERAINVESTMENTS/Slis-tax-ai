"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { formatMoney, formatDate } from "@/lib/utils"
import { api, CompanyOut, TaxReturnOut } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import {
  Building2,
  BookOpen,
  FileText,
  Calculator,
  Brain,
  PiggyBank,
  TrendingUp,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Users,
} from "lucide-react"

export default function DashboardPage() {
  const router = useRouter()
  const { user, accessToken } = useAuth()
  const [companies, setCompanies] = useState<CompanyOut[]>([])
  const [taxReturns, setTaxReturns] = useState<TaxReturnOut[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!accessToken) {
      router.push("/login")
      return
    }
    loadData()
  }, [accessToken, router])

  const loadData = async () => {
    try {
      const [companiesData, returnsData] = await Promise.all([
        api.listCompanies(),
        api.listTaxReturns(),
      ])
      setCompanies(companiesData)
      setTaxReturns(returnsData)
    } catch (err) {
      console.error("Failed to load dashboard data:", err)
    } finally {
      setLoading(false)
    }
  }

  const totalTaxOwed = taxReturns
    .filter((r) => r.status === "draft" || r.status === "approved")
    .reduce((sum, r) => sum + parseFloat(r.tax_owed), 0)

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
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back, {user?.full_name || user?.email?.split("@")[0]}
            </p>
          </div>
          <div className="flex gap-2">
            <Link href="/dashboard/companies/new" className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors">
              Add Company
            </Link>
            <Link href="/dashboard/tax/calculate" className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
              Calculate Tax
            </Link>
          </div>
        </div>

        {/* Stats cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Companies</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{companies.length}</div>
              <p className="text-xs text-muted-foreground">Business entities</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tax Returns</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{taxReturns.length}</div>
              <p className="text-xs text-muted-foreground">Total returns</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tax Owed (Draft)</CardTitle>
              <Calculator className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">
                {formatMoney(totalTaxOwed)}
              </div>
              <p className="text-xs text-muted-foreground">Pending payment</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI Agents</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">6</div>
              <p className="text-xs text-muted-foreground">Specialist agents ready</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick actions */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push("/dashboard/companies")}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-primary/10">
                  <Building2 className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">Manage Companies</h3>
                  <p className="text-sm text-muted-foreground">
                    {companies.length} companies • Add, edit, or select
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push("/dashboard/accounts")}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-green/10">
                  <BookOpen className="h-6 w-6 text-green" />
                </div>
                <div>
                  <h3 className="font-semibold">Chart of Accounts</h3>
                  <p className="text-sm text-muted-foreground">
                    Set up accounts per company
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push("/dashboard/journal")}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-blue/10">
                  <FileText className="h-6 w-6 text-blue" />
                </div>
                <div>
                  <h3 className="font-semibold">Journal Entries</h3>
                  <p className="text-sm text-muted-foreground">
                    Post balanced double-entry transactions
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push("/dashboard/tax")}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-orange/10">
                  <Calculator className="h-6 w-6 text-orange" />
                </div>
                <div>
                  <h3 className="font-semibold">Tax Center</h3>
                  <p className="text-sm text-muted-foreground">
                    Calculate, prepare & file returns
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push("/dashboard/ai")}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-purple/10">
                  <Brain className="h-6 w-6 text-purple" />
                </div>
                <div>
                  <h3 className="font-semibold">AI Assistant</h3>
                  <p className="text-sm text-muted-foreground">
                    Chat with Accountant, Tax, CFO agents
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push("/dashboard/personal")}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-pink/10">
                  <PiggyBank className="h-6 w-6 text-pink" />
                </div>
                <div>
                  <h3 className="font-semibold">Personal Finance</h3>
                  <p className="text-sm text-muted-foreground">
                    Budgets, net worth, goals
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent tax returns */}
        {taxReturns.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recent Tax Returns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-muted-foreground border-b">
                      <th className="pb-3 font-medium">Type</th>
                      <th className="pb-3 font-medium">Period</th>
                      <th className="pb-3 font-medium">Tax Owed</th>
                      <th className="pb-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {taxReturns.slice(0, 5).map((ret) => (
                      <tr key={ret.id} className="border-b last:border-b-0">
                        <td className="py-3">{ret.tax_type.replace("_", " ")}</td>
                        <td className="py-3">{formatDate(ret.period_end)}</td>
                        <td className="py-3 font-medium">{formatMoney(ret.tax_owed)}</td>
                        <td className="py-3">
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                              ret.status === "draft"
                                ? "bg-yellow/10 text-yellow"
                                : ret.status === "approved"
                                ? "bg-blue/10 text-blue"
                                : ret.status === "submitted"
                                ? "bg-green/10 text-green"
                                : "bg-gray/10 text-gray"
                            }`}
                          >
                            {ret.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  )
}