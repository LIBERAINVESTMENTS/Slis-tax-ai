"use client"

import { useEffect, useState } from "react"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { Calculator, FileText, Download, AlertCircle, CheckCircle, Clock } from "lucide-react"
import { formatMoney, formatDate } from "@/lib/utils"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs"

const TAX_TYPES = [
  { value: "corporate_income_tax", label: "Corporate Income Tax (36%)" },
  { value: "personal_income_tax", label: "Personal Income Tax (Progressive)" },
  { value: "vat", label: "VAT / BTW (10% standard)" },
  { value: "wage_tax", label: "Wage / Payroll Tax" },
  { value: "withholding_tax", label: "Withholding Tax" },
]

const VAT_RATES = [
  { value: "standard", label: "Standard (10%)" },
  { value: "reduced", label: "Reduced (5%)" },
  { value: "luxury", label: "Luxury (25%)" },
  { value: "zero", label: "Zero / Exports (0%)" },
]

export default function TaxPage() {
  const { accessToken } = useAuth()
  const [returns, setReturns] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("returns")

  // Calculator state
  const [calcType, setCalcType] = useState("corporate_income_tax")
  const [calcAmount, setCalcAmount] = useState("")
  const [vatRate, setVatRate] = useState("standard")
  const [calcResult, setCalcResult] = useState<any>(null)
  const [calcError, setCalcError] = useState("")
  const [calcLoading, setCalcLoading] = useState(false)

  // Create return state
  const [showCreateReturn, setShowCreateReturn] = useState(false)
  const [returnType, setReturnType] = useState("corporate_income_tax")
  const [periodStart, setPeriodStart] = useState(new Date().toISOString().split("T")[0])
  const [periodEnd, setPeriodEnd] = useState(new Date().toISOString().split("T")[0])
  const [filingDeadline, setFilingDeadline] = useState("")

  useEffect(() => {
    if (!accessToken) return
    loadReturns()
  }, [accessToken])

  const loadReturns = async () => {
    try {
      const data = await api.listTaxReturns()
      setReturns(data)
    } catch (err) {
      console.error("Failed to load returns:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleCalculate = async () => {
    if (!calcAmount) return
    setCalcError("")
    setCalcLoading(true)
    try {
      let result
      if (calcType === "vat") {
        result = await api.calculateTax({ tax_type: "vat", amount: calcAmount, rate_category: vatRate })
      } else {
        result = await api.calculateTax({ tax_type: calcType, amount: calcAmount })
      }
      setCalcResult(result)
    } catch (err: any) {
      setCalcError(err.message || "Calculation failed")
    } finally {
      setCalcLoading(false)
    }
  }

  const handleCreateReturn = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const ret = await api.createTaxReturn({
        company_id: null, // personal return for demo
        country: "SR",
        tax_type: returnType,
        period_start: periodStart,
        period_end: periodEnd,
        filing_deadline: filingDeadline || undefined,
      })
      setShowCreateReturn(false)
      loadReturns()
    } catch (err: any) {
      alert(err.message || "Failed to create return")
    }
  }

  const handleApprove = async (id: number) => {
    if (!confirm("Approve this tax return for filing?")) return
    try {
      await api.approveTaxReturn(id)
      loadReturns()
    } catch (err: any) {
      alert(err.message || "Failed to approve")
    }
  }

  const handleSubmit = async (id: number) => {
    if (!confirm("Submit this tax return? This action cannot be undone.")) return
    try {
      await api.submitTaxReturn(id)
      loadReturns()
    } catch (err: any) {
      alert(err.message || "Failed to submit")
    }
  }

  const handleDownload = async (id: number) => {
    try {
      const result = await api.downloadTaxReturn(id)
      alert(`Download ready: ${result.download_url}`)
    } catch (err: any) {
      alert(err.message || "Download failed")
    }
  }

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
            <h1 className="text-3xl font-bold tracking-tight">Tax Center</h1>
            <p className="text-muted-foreground">Suriname tax calculations, returns & filings</p>
          </div>
        </div>

        <Tabs defaultValue={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="calculator">Calculator</TabsTrigger>
            <TabsTrigger value="returns">Tax Returns</TabsTrigger>
            <TabsTrigger value="create">Create Return</TabsTrigger>
          </TabsList>

          {/* Calculator Tab */}
          <TabsContent value="calculator">
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calculator className="h-5 w-5" />
                    Tax Calculator
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Tax Type</Label>
                    <select
                      value={calcType}
                      onChange={(e) => { setCalcType(e.target.value); setCalcResult(null); }}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      {TAX_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                  </div>

                  {calcType === "vat" && (
                    <div className="space-y-2">
                      <Label>VAT Rate Category</Label>
                      <select
                        value={vatRate}
                        onChange={(e) => setVatRate(e.target.value)}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      >
                        {VAT_RATES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                      </select>
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label>Amount (SRD)</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      value={calcAmount}
                      onChange={(e) => setCalcAmount(e.target.value)}
                      placeholder="10000.00"
                    />
                  </div>

                  <Button onClick={handleCalculate} disabled={calcLoading || !calcAmount} className="w-full">
                    {calcLoading ? "Calculating..." : "Calculate"}
                  </Button>

                  {calcError && <div className="text-sm text-destructive p-3 rounded-md bg-destructive/10">{calcError}</div>}

                  {calcResult && (
                    <div className="p-4 rounded-md bg-green/10 border border-green/20 space-y-2">
                      <h4 className="font-medium">Calculation Result</h4>
                      <div className="grid gap-2 text-sm">
                        <div className="flex justify-between">
                          <span>Tax Type:</span>
                          <span className="font-medium">{TAX_TYPES.find(t => t.value === calcType)?.label}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Taxable Amount:</span>
                          <span className="font-medium">{formatMoney(calcResult.taxable_amount || calcResult.amount)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Rate:</span>
                          <span className="font-medium">{calcResult.rate}%</span>
                        </div>
                        <div className="flex justify-between font-medium text-lg">
                          <span>Tax Owed:</span>
                          <span>{formatMoney(calcResult.tax_owed || calcResult.vat || calcResult.tax)}</span>
                        </div>
                        {calcResult.total && (
                          <div className="flex justify-between font-medium">
                            <span>Total (incl. tax):</span>
                            <span>{formatMoney(calcResult.total)}</span>
                          </div>
                        )}
                        {calcResult.breakdown && (
                          <details className="mt-2">
                            <summary className="cursor-pointer text-sm text-muted-foreground">Show bracket breakdown</summary>
                            <div className="mt-2 space-y-1 text-xs">
                              {calcResult.breakdown.map((b: any, i: number) => (
                                <div key={i} className="flex justify-between p-2 bg-muted/50 rounded">
                                  <span>{b.from} - {b.to || "∞"} @ {b.rate}%</span>
                                  <span>{formatMoney(b.tax)}</span>
                                </div>
                              ))}
                            </div>
                          </details>
                        )}
                        {calcResult.note && (
                          <p className="text-xs text-muted-foreground mt-2">{calcResult.note}</p>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-orange-500" />
                    Important Notes
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>• All calculations use <strong>verified Suriname tax rules</strong> with official sources</p>
                  <p>• Personal income tax brackets above SRD 192,000 are <strong>unverified</strong> — not used for live calculation</p>
                  <p>• Wage tax brackets above SRD 150,000 annual taxable are <strong>unverified</strong></p>
                  <p>• Dividend withholding treaty rate (7.5%) is <strong>unverified</strong></p>
                  <p>• Filing deadlines and employer social rates require official confirmation</p>
                  <p>• <strong>Never rely on this for official filings without verification</strong></p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Returns Tab */}
          <TabsContent value="returns">
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Your Tax Returns</CardTitle>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
                    </div>
                  ) : returns.length === 0 ? (
                    <div className="text-center py-12">
                      <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <h3 className="text-lg font-medium mb-2">No tax returns yet</h3>
                      <p className="text-muted-foreground mb-4">Create your first tax return</p>
                      <Button onClick={() => setActiveTab("create")}>
                        Create Return
                      </Button>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="text-left text-sm text-muted-foreground border-b">
                            <th className="pb-3 font-medium">Type</th>
                            <th className="pb-3 font-medium">Period</th>
                            <th className="pb-3 font-medium">Tax Owed</th>
                            <th className="pb-3 font-medium">Status</th>
                            <th className="pb-3 font-medium">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {returns.map((ret) => (
                            <tr key={ret.id} className="border-b last:border-b-0">
                              <td className="py-3">{ret.tax_type.replace("_", " ")}</td>
                              <td className="py-3">{formatDate(ret.period_start)} – {formatDate(ret.period_end)}</td>
                              <td className="py-3 font-medium">{formatMoney(ret.tax_owed)}</td>
                              <td className="py-3">
                                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                                  ret.status === "draft" ? "bg-yellow/10 text-yellow" :
                                  ret.status === "approved" ? "bg-blue/10 text-blue" :
                                  ret.status === "submitted" ? "bg-green/10 text-green" :
                                  "bg-gray/10 text-gray"
                                }`}>
                                  {ret.status}
                                </span>
                              </td>
                              <td className="py-3">
                                <div className="flex items-center gap-2">
                                  {ret.status === "draft" && (
                                    <Button variant="outline" size="sm" onClick={() => handleApprove(ret.id)}>
                                      <CheckCircle className="h-3 w-3 mr-1" />
                                      Approve
                                    </Button>
                                  )}
                                  {ret.status === "approved" && (
                                    <Button variant="destructive" size="sm" onClick={() => handleSubmit(ret.id)}>
                                      <FileText className="h-3 w-3 mr-1" />
                                      Submit
                                    </Button>
                                  )}
                                  {ret.status !== "draft" && (
                                    <Button variant="outline" size="sm" onClick={() => handleDownload(ret.id)}>
                                      <Download className="h-3 w-3 mr-1" />
                                      Download
                                    </Button>
                                  )}
                                </div>
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
          </TabsContent>

          {/* Create Return Tab */}
          <TabsContent value="create">
            <Card>
              <CardHeader>
                <CardTitle>Create New Tax Return</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={(e) => { e.preventDefault(); handleCreateReturn(e) }} className="space-y-4 max-w-md">
                  <div className="space-y-2">
                    <Label>Tax Type</Label>
                    <select
                      value={returnType}
                      onChange={(e) => setReturnType(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      {TAX_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Period Start</Label>
                      <Input type="date" value={periodStart} onChange={(e) => setPeriodStart(e.target.value)} required />
                    </div>
                    <div className="space-y-2">
                      <Label>Period End</Label>
                      <Input type="date" value={periodEnd} onChange={(e) => setPeriodEnd(e.target.value)} required />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Filing Deadline (optional)</Label>
                    <Input type="date" value={filingDeadline} onChange={(e) => setFilingDeadline(e.target.value)} />
                  </div>

                  <div className="flex justify-end gap-2 pt-4">
                    <Button type="button" variant="outline" onClick={() => setActiveTab("returns")}>Cancel</Button>
                    <Button type="submit">Create Return</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  )
}