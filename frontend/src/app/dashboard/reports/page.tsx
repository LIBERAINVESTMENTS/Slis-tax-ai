"use client"

import { useEffect, useState } from "react"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { api, CompanyOut } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs"
import { formatMoney } from "@/lib/utils"
import { TrendingUp, Scale, ArrowUpDown, BarChart3 } from "lucide-react"

export default function ReportsPage() {
  const { accessToken } = useAuth()
  const [companies, setCompanies] = useState<CompanyOut[]>([])
  const [selectedCompany, setSelectedCompany] = useState<CompanyOut | null>(null)
  const [statements, setStatements] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("income")

  useEffect(() => {
    if (!accessToken) return
    loadCompanies()
  }, [accessToken])

  const loadCompanies = async () => {
    try {
      const data = await api.listCompanies()
      setCompanies(data)
      if (data.length > 0) {
        setSelectedCompany(data[0])
        loadStatements(data[0].id)
      }
    } catch (err) {
      console.error("Failed to load companies:", err)
    } finally {
      setLoading(false)
    }
  }

  const loadStatements = async (companyId: number) => {
    setLoading(true)
    try {
      const data = await api.getFinancialStatements(companyId)
      setStatements(data)
    } catch (err) {
      console.error("Failed to load statements:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleCompanyChange = (companyId: string) => {
    const company = companies.find(c => c.id === Number(companyId))
    setSelectedCompany(company || null)
    if (company) loadStatements(company.id)
  }

  const currency = selectedCompany?.currency || "SRD"

  const income = statements?.income_statement
  const balance = statements?.balance_sheet
  const cashflow = statements?.cash_flow

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <BarChart3 className="h-6 w-6" />
              Financial Reports
            </h1>
            <p className="text-muted-foreground">Profit & Loss, Balance Sheet, and Cash Flow statements</p>
          </div>
          <div>
            <select
              value={selectedCompany?.id || ""}
              onChange={(e) => handleCompanyChange(e.target.value)}
              className="flex h-10 w-64 rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              {companies.map(c => (
                <option key={c.id} value={c.id}>{c.name} ({c.currency})</option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : !statements ? (
          <Card>
            <CardContent className="py-12 text-center">
              <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No financial data yet</h3>
              <p className="text-muted-foreground">Post journal entries to generate financial statements</p>
            </CardContent>
          </Card>
        ) : (
          <Tabs defaultValue="income" onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="income">
                <TrendingUp className="h-4 w-4 mr-2" />
                Income Statement
              </TabsTrigger>
              <TabsTrigger value="balance">
                <Scale className="h-4 w-4 mr-2" />
                Balance Sheet
              </TabsTrigger>
              <TabsTrigger value="cashflow">
                <ArrowUpDown className="h-4 w-4 mr-2" />
                Cash Flow
              </TabsTrigger>
            </TabsList>

            {/* Income Statement */}
            <TabsContent value="income">
              <Card>
                <CardHeader>
                  <CardTitle>Profit & Loss Statement</CardTitle>
                  <CardDescription>{selectedCompany?.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold mb-2 text-green-600">Revenue</h3>
                      {Object.entries(income?.revenue_detail || {}).map(([name, amount]) => (
                        <div key={name} className="flex justify-between py-1 text-sm">
                          <span>{name}</span>
                          <span>{formatMoney(amount as string, currency)}</span>
                        </div>
                      ))}
                      <div className="flex justify-between font-semibold border-t pt-2 mt-2">
                        <span>Total Revenue</span>
                        <span>{formatMoney(income?.revenue, currency)}</span>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2 text-red-600">Expenses</h3>
                      {Object.entries(income?.expense_detail || {}).map(([name, amount]) => (
                        <div key={name} className="flex justify-between py-1 text-sm">
                          <span>{name}</span>
                          <span>({formatMoney(amount as string, currency)})</span>
                        </div>
                      ))}
                      <div className="flex justify-between font-semibold border-t pt-2 mt-2">
                        <span>Total Expenses</span>
                        <span>({formatMoney(income?.expenses, currency)})</span>
                      </div>
                    </div>

                    <div className="flex justify-between font-bold text-lg border-t-2 pt-4">
                      <span>Net Income</span>
                      <span className={parseFloat(income?.net_income || "0") >= 0 ? "text-green-600" : "text-red-600"}>
                        {formatMoney(income?.net_income, currency)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Balance Sheet */}
            <TabsContent value="balance">
              <Card>
                <CardHeader>
                  <CardTitle>Balance Sheet</CardTitle>
                  <CardDescription>{selectedCompany?.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between py-2">
                      <span className="font-medium">Assets</span>
                      <span>{formatMoney(balance?.assets, currency)}</span>
                    </div>
                    <div className="flex justify-between py-2">
                      <span className="font-medium">Liabilities</span>
                      <span>{formatMoney(balance?.liabilities, currency)}</span>
                    </div>
                    <div className="flex justify-between py-2">
                      <span className="font-medium">Equity</span>
                      <span>{formatMoney(balance?.equity, currency)}</span>
                    </div>
                    <div className="flex justify-between font-semibold border-t pt-3">
                      <span>Liabilities + Equity</span>
                      <span>{formatMoney(balance?.liabilities_plus_equity, currency)}</span>
                    </div>
                    <div className={`flex items-center gap-2 text-sm ${balance?.balanced ? "text-green-600" : "text-red-600"}`}>
                      {balance?.balanced ? "✓ Balanced" : "⚠ Out of balance"}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Cash Flow */}
            <TabsContent value="cashflow">
              <Card>
                <CardHeader>
                  <CardTitle>Cash Flow Statement</CardTitle>
                  <CardDescription>{selectedCompany?.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between py-2">
                      <span className="font-medium">Cash Inflow</span>
                      <span className="text-green-600">{formatMoney(cashflow?.cash_in, currency)}</span>
                    </div>
                    <div className="flex justify-between py-2">
                      <span className="font-medium">Cash Outflow</span>
                      <span className="text-red-600">({formatMoney(cashflow?.cash_out, currency)})</span>
                    </div>
                    <div className="flex justify-between font-semibold border-t pt-3">
                      <span>Net Cash Flow</span>
                      <span>{formatMoney(cashflow?.net_cash_flow, currency)}</span>
                    </div>
                    <div className="flex justify-between py-2">
                      <span className="font-medium">Cash Balance</span>
                      <span>{formatMoney(cashflow?.cash_balance, currency)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </Layout>
  )
}
