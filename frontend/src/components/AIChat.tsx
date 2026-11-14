"use client"

import { useState, useRef, useEffect } from "react"
import { api, UserOut } from "@/lib/api"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ScrollArea } from "@/components/ui/ScrollArea"
import { Send, Bot, User, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface Message {
  role: "user" | "assistant" | "system"
  content: string
  agent?: string
}

export function AIChat({ user }: { user: UserOut | null }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "system", content: "Welcome! I'm your AI Accountant assistant. I can help with bookkeeping, tax calculations, financial analysis, and more. Ask me anything about your finances!" }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string>("master")
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const agents = [
    { value: "master", label: "Master (Auto-route)" },
    { value: "accountant", label: "Accountant Agent" },
    { value: "tax", label: "Tax Agent" },
    { value: "cfo", label: "CFO Agent" },
    { value: "personal_finance", label: "Personal Finance Agent" },
    { value: "document", label: "Document Agent" },
    { value: "audit", label: "Audit Agent" },
  ]

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input
    setMessages(prev => [...prev, { role: "user", content: userMessage }])
    setInput("")
    setLoading(true)

    try {
      const response = await api.chat(userMessage, selectedAgent)
      setMessages(prev => [...prev, {
        role: "assistant",
        content: response.text,
        agent: response.agent
      }])
    } catch (err: any) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: `Error: ${err.message || "Failed to get response"}`
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full border border-border rounded-lg bg-card">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">AI Assistant</h3>
        </div>
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="text-sm border border-input rounded-md px-2 py-1 bg-background"
        >
          {agents.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
        </select>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4 space-y-4" ref={scrollAreaRef}>
        {messages.map((msg, idx) => (
          <div key={idx} className={cn(
            "flex gap-3 max-w-[80%]",
            msg.role === "user" ? "justify-end" : "justify-start"
          )}>
            <div className={cn(
              "rounded-2xl px-4 py-2 text-sm",
              msg.role === "user"
                ? "bg-primary text-primary-foreground rounded-br-none"
                : msg.role === "system"
                ? "bg-muted text-muted-foreground italic text-center w-full max-w-none"
                : "bg-secondary text-secondary-foreground rounded-bl-none"
            )}>
              {msg.role !== "system" && msg.role !== "user" && (
                <div className="flex items-center gap-1 text-xs text-muted-foreground/70 mb-1">
                  <Bot className="h-3 w-3" />
                  <span>{msg.agent || "assistant"}</span>
                </div>
              )}
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-secondary text-secondary-foreground rounded-2xl px-4 py-2 text-sm flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          </div>
        )}
      </ScrollArea>

      {/* Input */}
      <form onSubmit={handleSend} className="p-4 border-t border-border">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your finances..."
            disabled={loading}
            className="flex-1"
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), handleSend(e))}
          />
          <Button type="submit" disabled={loading || !input.trim()} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-1 text-center">
          Current agent: <strong>{agents.find(a => a.value === selectedAgent)?.label}</strong>
        </p>
      </form>
    </div>
  )
}