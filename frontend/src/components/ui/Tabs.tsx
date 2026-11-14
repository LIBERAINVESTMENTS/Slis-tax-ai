"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface TabsContextType {
  value: string
  onValueChange: (value: string) => void
}

const TabsContext = React.createContext<TabsContextType | null>(null)

function useTabs() {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error("Tabs components must be used within Tabs")
  return context
}

interface TabsProps {
  children: React.ReactNode
  defaultValue: string
  onValueChange?: (value: string) => void
  value?: string
}

export function Tabs({ children, defaultValue, onValueChange, value }: TabsProps) {
  const [internalValue, setInternalValue] = React.useState(defaultValue)
  const controlled = value !== undefined
  const currentValue = controlled ? value : internalValue

  return (
    <TabsContext.Provider value={{ value: currentValue, onValueChange: (v: string) => { setInternalValue(v); onValueChange?.(v) } }}>
      <div data-slot="tabs">{children}</div>
    </TabsContext.Provider>
  )
}

interface TabsListProps extends React.HTMLAttributes<HTMLDivElement> {}

export function TabsList({ className, ...props }: TabsListProps) {
  return (
    <div
      data-slot="tabs-list"
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground",
        className
      )}
      {...props}
    />
  )
}

interface TabsTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string
}

export function TabsTrigger({ className, value, disabled, children, ...props }: TabsTriggerProps) {
  const { value: contextValue, onValueChange } = useTabs()
  const isActive = contextValue === value

  return (
    <button
      data-slot="tabs-trigger"
      data-state={isActive ? "active" : "inactive"}
      data-disabled={disabled}
      onClick={() => { if (!disabled) onValueChange(value) }}
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        isActive ? "bg-background text-foreground shadow-sm" : "hover:bg-accent hover:text-accent-foreground",
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}

interface TabsContentProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string
}

export function TabsContent({ className, value, children, ...props }: TabsContentProps) {
  const { value: contextValue } = useTabs()
  const isActive = contextValue === value

  if (!isActive) return null

  return (
    <div
      data-slot="tabs-content"
      data-state="active"
      className={cn(
        "mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}