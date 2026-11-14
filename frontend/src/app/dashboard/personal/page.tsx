"use client"

import { useEffect, useState } from "react"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { PiggyBank, Target, TrendingUp, CreditCard, DollarSign, Plus } from "lucide-react"
import { formatMoney } from "@/lib/utils"

export default function PersonalFinancePage() {
  const { accessToken } = useAuth()
  const [loading, setLoading] = useState(true)
  const [netWorth, setNetWorth] = useState(0)
  const [monthlyIncome, setMonthlyIncome] = useState(0)
  const [monthlyExpenses, setMonthlyExpenses] = useState(0)
  const [savingsRate, setSavingsRate] = useState(0)
  const [goals, setGoals] = useState<any[]>([])
  const [budgets, setBudgets] = useState<any[]>([])
  const [accounts, setAccounts] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState("overview")

  useEffect(() => {
    if (!accessToken) return
    loadData()
  }, [accessToken])

  const loadData = async () => {
    // This would load from personal finance API endpoints
    // For now using mock data
    setNetWorth(125000)
    setMonthlyIncome(8500)
    setMonthlyExpenses(5200)
    setSavingsRate(38.8)
    setGoals([
      { id: 1, name: "Emergency Fund", target: 50000, current: 32000, deadline: "2024-12-31" },
      { id: 2, name: "House Down Payment", target: 100000, current: 45000, deadline: "2025-06-30" },
    ])
    setBudgets([
      { category: "Housing", budget: 2000, spent: 1800 },
      { category: "Food", budget: 800, spent: 650 },
      { category: "Transport", budget: 500, spent: 320 },
      { category: "Entertainment", budget: 300, spent: 180 },
    ])
    setAccounts([
      { name: "Main Checking", type: "checking", balance: 15000 },
      { name: "Savings Account", type: "savings", balance: 45000 },
      { name: "Investment Account", type: "investment", balance: 65000 },
    ])
    setLoading(false)
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

  const monthlySavings = 8500 - 5200

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Personal Finance</h1>
          <p className="text-muted-foreground">Manage your personal finances, budgets & goals</p>
        </div>

        {/* Key Metrics */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Net Worth</CardTitle>
              <PiggyBank className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatMoney(netWorth)}</div>
              <p className="text-xs text-muted-foreground">Total assets - liabilities</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Income</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{formatMoney(monthlyIncome)}</div>
              <p className="text-xs text-muted-foreground">After tax</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Expenses</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{formatMoney(5200)}</div>
              <p className="text-xs text-muted-foreground">Monthly spending</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Savings Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">38.8%</div>
              <p className="text-xs text-muted-foreground">Monthly savings: {formatMoney(monthlySavings)}</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="goals">Goals</TabsTrigger>
            <TabsTrigger value="budgets">Budgets</TabsTrigger>
            <TabsTrigger value="accounts">Accounts</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="grid gap-6 mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-4 md:grid-cols-3">
                  <Button variant="outline" className="h-24 flex flex-col items-center justify-center gap-2">
                    <DollarSign className="h-6 w-6" />
                    Add Income
                  </Button>
                  <Button variant="outline" className="h-24 flex flex-col items-center justify-center gap-2">
                    <CreditCard className="h-6 w-6" />
                    Add Expense
                  </Button>
                  <Button variant="outline" className="h-24 flex flex-col items-center justify-center gap-2">
                    <Target className="h-6 w-6" />
                    Set Goal
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="goals">
            <div className="space-y-4 mt-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Financial Goals</h2>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Goal
                </Button>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {[
                  { name: "Emergency Fund", target: 50000, current: 32000, deadline: "2024-12-31" },
                  { name: "House Down Payment", target: 100000, current: 45000, deadline: "2025-06-30" },
                ].map((goal) => {
                  const progress = (goal.current / goal.target) * 100
                  return (
                    <Card key={goal.name}>
                      <CardContent className="space-y-3">
                        <div className="flex justify-between">
                          <h3 className="font-semibold">{goal.name}</h3>
                          <span className="text-sm text-muted-foreground">Due: {goal.deadline}</span>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm">
                            <span>{formatMoney(goal.current)} / {formatMoney(goal.target)}</span>
                            <span>{progress.toFixed(1)}%</span>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${progress}%` }} />
                          </div>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {formatMoney(goal.target - goal.current)} remaining
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="budgets">
            <div className="space-y-4 mt-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Monthly Budgets</h2>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Budget
                </Button>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {[
                  { category: "Housing", budget: 2000, spent: 1800 },
                  { category: "Food", budget: 800, spent: 650 },
                  { category: "Transport", budget: 500, spent: 320 },
                  { category: "Entertainment", budget: 300, spent: 180 },
                ].map((b) => {
                  const pct = (b.spent / b.budget) * 100
                  return (
                    <Card key={b.category}>
                      <CardContent className="space-y-2">
                        <div className="flex justify-between">
                          <h3 className="font-semibold">{b.category}</h3>
                          <span className={pct > 100 ? "text-red-600" : "text-green-600"} font-medium>
                            {pct.toFixed(0)}%
                          </span>
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>{formatMoney(b.spent)} / {formatMoney(b.budget)}</span>
                            <span>{pct.toFixed(0)}%</span>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div className={`h-full rounded-full transition-all ${pct > 100 ? "bg-red-500" : pct > 80 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {formatMoney(b.budget - b.spent)} remaining
                        </p>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="accounts">
            <div className="space-y-4 mt-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Accounts</h2>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Account
                </Button>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                {[
                  { name: "Main Checking", type: "checking", balance: 15000 },
                  { name: "Savings Account", type: "savings", balance: 45000 },
                  { name: "Investment Account", type: "investment", balance: 65000 },
                ].map((acc) => (
                  <Card key={acc.name} className="text-center py-6">
                    <div className="text-3xl font-bold mb-1">{formatMoney(acc.balance)}</div>
                    <h3 className="font-semibold">{acc.name}</h3>
                    <span className="text-xs px-2 py-1 rounded-full bg-muted text-muted-foreground">
                      {acc.type}
                    </span>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  )
}