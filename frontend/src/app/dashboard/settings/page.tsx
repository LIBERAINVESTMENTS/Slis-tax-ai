"use client"

import { useState } from "react"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { User, Shield, Key, Bell, Database, Palette, Globe } from "lucide-react"
import { formatDate } from "@/lib/utils"

export default function SettingsPage() {
  const { user, accessToken } = useAuth()
  const [activeTab, setActiveTab] = useState("profile")
  const [profile, setProfile] = useState({ full_name: user?.full_name || "", email: user?.email || "" })
  const [password, setPassword] = useState({ current: "", new: "", confirm: "" })
  const [mfaEnabled, setMfaEnabled] = useState(false)
  const [mfaSecret, setMfaSecret] = useState("")
  const [mfaCode, setMfaCode] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    // Profile update API not implemented yet
    setSuccess("Profile updated (demo)")
    setTimeout(() => setSuccess(""), 3000)
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password.new !== password.confirm) {
      setError("New passwords don't match")
      return
    }
    if (password.new.length < 8) {
      setError("Password must be at least 8 characters")
      return
    }
    // Password change API not implemented yet
    setSuccess("Password changed (demo)")
    setPassword({ current: "", new: "", confirm: "" })
    setTimeout(() => setSuccess(""), 3000)
  }

  const setupMFA = async () => {
    try {
      const data = await api.mfaSetup()
      setMfaSecret(data.secret)
      setSuccess("MFA setup ready. Scan QR code with authenticator app.")
    } catch (err: any) {
      setError(err.message || "MFA setup failed")
    }
  }

  const verifyMFA = async () => {
    try {
      await api.mfaVerify(mfaCode)
      setMfaEnabled(true)
      setMfaCode("")
      setSuccess("MFA enabled successfully!")
    } catch (err: any) {
      setError(err.message || "Invalid code")
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">Manage your account and preferences</p>
        </div>

        <Tabs defaultValue="profile" onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="profile">
              <User className="h-4 w-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="security">
              <Shield className="h-4 w-4 mr-2" />
              Security
            </TabsTrigger>
            <TabsTrigger value="notifications">
              <Bell className="h-4 w-4 mr-2" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="advanced">
              <Database className="h-4 w-4 mr-2" />
              Advanced
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Profile
                </CardTitle>
                <CardDescription>Manage your personal information</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleProfileUpdate} className="space-y-4 max-w-md">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      value={profile.full_name}
                      onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                      placeholder="John Doe"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profile.email}
                      onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                      disabled
                    />
                    <p className="text-xs text-muted-foreground">Email cannot be changed</p>
                  </div>
                  <div className="space-y-2">
                    <Label>Role</Label>
                    <Input value={user?.role || "owner"} disabled />
                    <p className="text-xs text-muted-foreground">Role is assigned by system</p>
                  </div>
                  <Button type="submit">Save Changes</Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security">
            <div className="space-y-6">
              {/* Password */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5" />
                    Change Password
                  </CardTitle>
                  <CardDescription>Update your login password</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
                    <div className="space-y-2">
                      <Label htmlFor="current_password">Current Password</Label>
                      <Input
                        id="current_password"
                        type="password"
                        value={password.current}
                        onChange={(e) => setPassword({ ...password, current: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new_password">New Password</Label>
                      <Input
                        id="new_password"
                        type="password"
                        value={password.new}
                        onChange={(e) => setPassword({ ...password, new: e.target.value })}
                        minLength={8}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirm_password">Confirm New Password</Label>
                      <Input
                        id="confirm_password"
                        type="password"
                        value={password.confirm}
                        onChange={(e) => setPassword({ ...password, confirm: e.target.value })}
                        required
                      />
                    </div>
                    <Button type="submit">Update Password</Button>
                  </form>
                </CardContent>
              </Card>

              {/* MFA */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Two-Factor Authentication (MFA)
                  </CardTitle>
                  <CardDescription>Add an extra layer of security with TOTP</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {!mfaEnabled ? (
                    <div className="space-y-4">
                      <Button onClick={setupMFA} variant="outline">
                        Enable MFA
                      </Button>
                      {mfaSecret && (
                        <div className="space-y-2 p-4 rounded-lg bg-muted/50">
                          <p className="text-sm font-medium">Scan this QR code with your authenticator app:</p>
                          <p className="text-sm font-mono break-all">{mfaSecret}</p>
                          <p className="text-xs text-muted-foreground">Or enter this secret manually: <code>{mfaSecret}</code></p>
                        </div>
                      )}
                      {mfaSecret && (
                        <div className="space-y-2">
                          <Label htmlFor="mfa_code">Enter 6-digit code from authenticator</Label>
                          <Input
                            id="mfa_code"
                            value={mfaCode}
                            onChange={(e) => setMfaCode(e.target.value)}
                            placeholder="123456"
                            maxLength={6}
                          />
                          <Button onClick={verifyMFA}>Verify & Enable</Button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">MFA is enabled</p>
                        <p className="text-sm text-muted-foreground">Your account is protected with two-factor authentication</p>
                      </div>
                      <Button variant="destructive">Disable MFA</Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Sessions */}
              <Card>
                <CardHeader>
                  <CardTitle>Active Sessions</CardTitle>
                  <CardDescription>Manage your active login sessions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="text-xs font-medium text-primary">CU</span>
                        </div>
                        <div>
                          <p className="font-medium">Current Session</p>
                          <p className="text-sm text-muted-foreground">Chrome on Windows • Active now</p>
                        </div>
                      </div>
                      <span className="text-xs px-2 py-1 rounded-full bg-green/10 text-green-600">Current</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>Choose what notifications you receive</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { label: "Tax filing deadlines", desc: "Get reminded before tax returns are due" },
                  { label: "Budget alerts", desc: "Notify when spending exceeds budget" },
                  { label: "AI agent insights", desc: "Weekly financial insights from AI agents" },
                  { label: "System updates", desc: "Platform maintenance and feature announcements" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{item.label}</p>
                      <p className="text-sm text-muted-foreground">{item.desc}</p>
                    </div>
                    <Input type="checkbox" defaultChecked />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Advanced Tab */}
          <TabsContent value="advanced">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Data & Privacy</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button variant="outline">Export My Data</Button>
                  <Button variant="destructive">Delete Account</Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Appearance</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Dark Mode</p>
                      <p className="text-sm text-muted-foreground">System preference</p>
                    </div>
                    <Input type="checkbox" defaultChecked />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Danger Zone</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">These actions are irreversible</p>
                  <Button variant="destructive">Delete All Data</Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  )
}