"use client"

import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { AIChat } from "@/components/AIChat"
import { useAuth } from "@/context/AuthContext"
import { Brain, Bot, Shield, FileText, TrendingUp, User, Calculator } from "lucide-react"

const agents = [
  { id: "master", name: "Master Agent", role: "Central coordinator", icon: Brain, desc: "Routes your questions to the right specialist" },
  { id: "accountant", name: "Accountant Agent", role: "Bookkeeping & Reconciliation", icon: Calculator, desc: "Journal entries, duplicates, bank reconciliation" },
  { id: "tax", name: "Tax Agent", role: "Tax Legislation & Preparation", icon: FileText, desc: "Suriname corporate, personal, VAT, wage tax" },
  { id: "cfo", name: "CFO Agent", role: "Business Analysis & Forecasting", icon: TrendingUp, desc: "Cash flow, break-even, margins, scenarios" },
  { id: "personal_finance", name: "Personal Finance Agent", role: "Personal Financial Management", icon: User, desc: "Budgets, net worth, goals, recurring expenses" },
  { id: "document", name: "Document Agent", role: "OCR & Document Extraction", icon: Shield, desc: "Receipts, invoices, bank statements (needs OCR setup)" },
  { id: "audit", name: "Audit Agent", role: "Verification & Compliance", icon: Shield, desc: "Tamper detection, period locks, compliance checks" },
]

export default function AIPage() {
  const { user } = useAuth()

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Assistant</h1>
          <p className="text-muted-foreground">Your team of specialist AI agents for accounting, tax & finance</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <Card key={agent.id} className="hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <agent.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <p className="text-sm text-muted-foreground">{agent.role}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">{agent.desc}</p>
                <AIChat user={user} />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </Layout>
  )
}