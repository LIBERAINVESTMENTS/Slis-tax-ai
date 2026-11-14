"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { api, CompanyOut } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { Building2, Plus, Edit, Trash2 } from "lucide-react"

export default function CompaniesPage() {
  const router = useRouter()
  const { accessToken } = useAuth()
  const [companies, setCompanies] = useState<CompanyOut[]>([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<number | null>(null)

  useEffect(() => {
    if (!accessToken) {
      router.push("/login")
      return
    }
    loadCompanies()
  }, [accessToken, router])

  const loadCompanies = async () => {
    try {
      const data = await api.listCompanies()
      setCompanies(data)
    } catch (err) {
      console.error("Failed to load companies:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this company?")) return
    setDeleting(id)
    try {
      // Note: DELETE endpoint not implemented in backend yet
      alert("Delete not yet implemented in backend")
    } catch (err) {
      console.error("Failed to delete company:", err)
    } finally {
      setDeleting(null)
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
            <h1 className="text-3xl font-bold tracking-tight">Companies</h1>
            <p className="text-muted-foreground">Manage your business entities</p>
          </div>
          <Link href="/dashboard/companies/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Company
            </Button>
          </Link>
        </div>

        {companies.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Building2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No companies yet</h3>
              <p className="text-muted-foreground mb-4">Create your first business entity to get started</p>
              <Link href="/dashboard/companies/new">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Company
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {companies.map((company) => (
              <Card key={company.id} className="hover:border-primary/50 transition-colors">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{company.name}</CardTitle>
                    <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary">
                      {company.currency}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm text-muted-foreground">
                    <p>Slug: {company.slug}</p>
                    <p>Country: {company.country}</p>
                    <p>Fiscal year starts: Month {company.fiscal_year_start_month}</p>
                    {company.tax_regime && <p>Tax regime: {company.tax_regime}</p>}
                  </div>
                  <div className="flex gap-2 pt-2">
                    <Link href={`/dashboard/companies/${company.id}`} className="inline-flex items-center justify-center rounded-md border border-input bg-background px-3 py-1.5 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors">
                      <Edit className="h-4 w-4 mr-1" />
                      Select
                    </Link>
                    <Button variant="outline" size="sm" onClick={() => handleDelete(company.id)} disabled={deleting === company.id}>
                      <Trash2 className="h-4 w-4 mr-1" />
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}