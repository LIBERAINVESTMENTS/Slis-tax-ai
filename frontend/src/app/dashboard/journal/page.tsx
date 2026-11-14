"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { api, JournalEntryOut } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { FileText, Plus, Search, ChevronDown, ChevronUp } from "lucide-react"

interface JournalLineForm {
  account_id: number
  account_code: string
  account_name: string
  debit: string
  credit: string
  memo: string
}

export default function JournalPage() {
  const router = useRouter()
  const { accessToken } = useAuth()
  const [entries, setEntries] = useState<JournalEntryOut[]>([])
  const [accounts, setAccounts] = useState<Array<{id: number, code: string, name: string}>>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [filter, setFilter] = useState("")

  // Form state
  const [entryNo, setEntryNo] = useState("")
  const [entryDate, setEntryDate] = useState(new Date().toISOString().split("T")[0])
  const [reference, setReference] = useState("")
  const [description, setDescription] = useState("")
  const [lines, setLines] = useState<JournalLineForm[]>([
    { account_id: 0, account_code: "", account_name: "", debit: "0", credit: "0", memo: "" },
    { account_id: 0, account_code: "", account_name: "", debit: "0", credit: "0", memo: "" },
  ])
  const [formError, setFormError] = useState("")
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    if (!accessToken) {
      router.push("/login")
      return
    }
    loadData()
  }, [accessToken, router])

  const loadData = async () => {
    try {
      const companies = await api.listCompanies()
      if (companies.length > 0) {
        const [entriesData, accountsData] = await Promise.all([
          api.listJournalEntries(companies[0].id),
          api.listAccounts(companies[0].id),
        ])
        setEntries(entriesData)
        setAccounts(accountsData.map(a => ({ id: a.id, code: a.code, name: a.name })))
      }
    } catch (err) {
      console.error("Failed to load data:", err)
    } finally {
      setLoading(false)
    }
  }

  const addLine = () => {
    setLines(prev => [...prev, { account_id: 0, account_code: "", account_name: "", debit: "0", credit: "0", memo: "" }])
  }

  const removeLine = (index: number) => {
    if (lines.length <= 2) return
    setLines(prev => prev.filter((_, i) => i !== index))
  }

  const updateLine = (index: number, field: keyof JournalLineForm, value: string) => {
    setLines(prev => prev.map((line, i) => i === index ? { ...line, [field]: value } : line))
  }

  const handleAccountChange = (index: number, accountId: number) => {
    const account = accounts.find(a => a.id === accountId)
    if (account) {
      setLines(prev => prev.map((line, i) => i === index ? { ...line, account_id: accountId, account_code: account.code, account_name: account.name } : line))
    }
  }

  const validateLines = () => {
    let totalDebit = 0
    let totalCredit = 0
    let hasValidLines = false

    for (const line of lines) {
      if (line.account_id === 0) return "All lines must have an account selected"
      const debit = parseFloat(line.debit) || 0
      const credit = parseFloat(line.credit) || 0
      if (debit > 0 && credit > 0) return "A line cannot have both debit and credit"
      if (debit > 0 || credit > 0) hasValidLines = true
      totalDebit += debit
      totalCredit += credit
    }

    if (!hasValidLines) return "At least one line must have an amount"
    if (totalDebit !== totalCredit) return `Entry is out of balance: debits=${totalDebit.toFixed(2)} credits=${totalCredit.toFixed(2)}`
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const validationError = validateLines()
    if (validationError) {
      setFormError(validationError)
      return
    }

    setFormError("")
    setFormLoading(true)

    try {
      const companies = await api.listCompanies()
      if (companies.length === 0) throw new Error("No company found")

      const journalLines = lines
        .filter(l => l.account_id !== 0 && (parseFloat(l.debit) > 0 || parseFloat(l.credit) > 0))
        .map(l => ({
          account_id: l.account_id,
          debit: l.debit,
          credit: l.credit,
          memo: l.memo,
        }))

      await api.createJournalEntry(companies[0].id, {
        entry_no: entryNo,
        entry_date: entryDate,
        reference: reference || undefined,
        description: description || undefined,
        lines: journalLines,
      })

      setShowCreate(false)
      setEntryNo("")
      setEntryDate(new Date().toISOString().split("T")[0])
      setReference("")
      setDescription("")
      setLines([
        { account_id: 0, account_code: "", account_name: "", debit: "0", credit: "0", memo: "" },
        { account_id: 0, account_code: "", account_name: "", debit: "0", credit: "0", memo: "" },
      ])
      setFormError("")
      loadData()
    } catch (err: any) {
      setFormError(err.message || "Failed to create journal entry")
    } finally {
      setFormLoading(false)
    }
  }

  const filteredEntries = entries.filter(e =>
    e.entry_no.toLowerCase().includes(filter.toLowerCase()) ||
    (e.reference?.toLowerCase().includes(filter.toLowerCase()) ?? false)
  )

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
            <h1 className="text-3xl font-bold tracking-tight">Journal Entries</h1>
            <p className="text-muted-foreground">Double-entry bookkeeping</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setShowCreate(!showCreate)}>
              <Plus className="h-4 w-4 mr-2" />
              New Entry
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
                  placeholder="Search entries..."
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Create Entry Form */}
        {showCreate && (
          <Card className="border-primary">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  New Journal Entry
                </CardTitle>
                <Button variant="ghost" size="icon" onClick={() => setShowCreate(false)}>
                  <ChevronUp className="h-5 w-5" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {formError && <div className="text-sm text-destructive p-3 rounded-md bg-destructive/10">{formError}</div>}

                <div className="grid gap-4 md:grid-cols-4">
                  <div className="space-y-2">
                    <Label htmlFor="entryNo">Entry No. *</Label>
                    <Input
                      id="entryNo"
                      value={entryNo}
                      onChange={(e) => setEntryNo(e.target.value)}
                      placeholder="JE-001"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="entryDate">Date *</Label>
                    <Input
                      id="entryDate"
                      type="date"
                      value={entryDate}
                      onChange={(e) => setEntryDate(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reference">Reference</Label>
                    <Input
                      id="reference"
                      value={reference}
                      onChange={(e) => setReference(e.target.value)}
                      placeholder="INV-001"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Monthly rent payment"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium">Lines (must balance: debits = credits)</h3>
                    <Button type="button" variant="outline" size="sm" onClick={addLine}>
                      <Plus className="h-4 w-4 mr-1" />
                      Add Line
                    </Button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="text-left text-sm text-muted-foreground border-b">
                          <th className="pb-2 font-medium w-40">Account</th>
                          <th className="pb-2 font-medium w-32">Debit</th>
                          <th className="pb-2 font-medium w-32">Credit</th>
                          <th className="pb-2 font-medium">Memo</th>
                          <th className="pb-2 font-medium w-10"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {lines.map((line, index) => (
                          <tr key={index} className="border-b last:border-b-0">
                            <td className="py-2">
                              <select
                                value={line.account_id}
                                onChange={(e) => handleAccountChange(index, Number(e.target.value))}
                                className="w-full rounded-md border border-input bg-background px-2 py-1 text-sm"
                              >
                                <option value={0}>Select account...</option>
                                {accounts.map(a => (
                                  <option key={a.id} value={a.id}>
                                    {a.code} - {a.name}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="py-2">
                              <Input
                                type="number"
                                step="0.01"
                                min="0"
                                value={line.debit}
                                onChange={(e) => updateLine(index, "debit", e.target.value)}
                                placeholder="0.00"
                                className="w-full text-right"
                              />
                            </td>
                            <td className="py-2">
                              <Input
                                type="number"
                                step="0.01"
                                min="0"
                                value={line.credit}
                                onChange={(e) => updateLine(index, "credit", e.target.value)}
                                placeholder="0.00"
                                className="w-full text-right"
                              />
                            </td>
                            <td className="py-2">
                              <Input
                                value={line.memo}
                                onChange={(e) => updateLine(index, "memo", e.target.value)}
                                placeholder="Memo"
                              />
                            </td>
                            <td className="py-2">
                              <Button
                                type="button"
                                variant="ghost"
                                size="icon"
                                onClick={() => removeLine(index)}
                                disabled={lines.length <= 2}
                              >
                                <ChevronDown className="h-4 w-4" />
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Balance Check */}
                  <div className="flex justify-end gap-4 pt-4 border-t">
                    <div className="font-medium">
                      Total Debit: <span className="font-mono ml-2">{(lines.reduce((sum, l) => sum + (parseFloat(l.debit) || 0), 0)).toFixed(2)}</span>
                    </div>
                    <div className="font-medium">
                      Total Credit: <span className="font-mono ml-2">{(lines.reduce((sum, l) => sum + (parseFloat(l.credit) || 0), 0)).toFixed(2)}</span>
                    </div>
                    <div className={`font-medium font-mono ${Math.abs(lines.reduce((sum, l) => sum + (parseFloat(l.debit) || 0), 0) - lines.reduce((sum, l) => sum + (parseFloat(l.credit) || 0), 0)) < 0.01 ? "text-green-600" : "text-red-600"}`}>
                      {Math.abs(lines.reduce((sum, l) => sum + (parseFloat(l.debit) || 0), 0) - lines.reduce((sum, l) => sum + (parseFloat(l.credit) || 0), 0)) < 0.01 ? "✓ Balanced" : "✗ Out of Balance"}
                    </div>
                  </div>
                </div>

                {formError && <div className="text-sm text-destructive p-3 rounded-md bg-destructive/10">{formError}</div>}

                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setShowCreate(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={formLoading}>
                    {formLoading ? "Creating..." : "Post Entry"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Entries List */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Journal Entries</CardTitle>
              <Input
                placeholder="Search..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-64 pl-10"
              />
            </div>
          </CardHeader>
          <CardContent>
            {entries.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No journal entries yet</h3>
                <p className="text-muted-foreground mb-4">Create your first double-entry journal entry</p>
                <Button onClick={() => setShowCreate(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  New Entry
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-muted-foreground border-b">
                      <th className="pb-3 font-medium">Entry No.</th>
                      <th className="pb-3 font-medium">Date</th>
                      <th className="pb-3 font-medium">Reference</th>
                      <th className="pb-3 font-medium">Description</th>
                      <th className="pb-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {entries
                      .filter(e => e.entry_no.toLowerCase().includes(filter.toLowerCase()) ||
                        (e.reference?.toLowerCase().includes(filter.toLowerCase()) ?? false))
                      .map((entry) => (
                        <tr key={entry.id} className="border-b last:border-b-0 hover:bg-muted/50">
                          <td className="py-3 font-mono">{entry.entry_no}</td>
                          <td className="py-3">{entry.entry_date}</td>
                          <td className="py-3 text-muted-foreground">{entry.reference || "-"}</td>
                          <td className="py-3 text-muted-foreground">{entry.description || "-"}</td>
                          <td className="py-3">
                            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${entry.posted ? "bg-green/10 text-green" : "bg-yellow/10 text-yellow"}`}>
                              {entry.posted ? "Posted" : "Draft"}
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