"use client"

import { forwardRef, HTMLAttributes } from "react"
import { cn } from "@/lib/utils"

export interface ScrollAreaProps extends HTMLAttributes<HTMLDivElement> {}

const ScrollArea = forwardRef<HTMLDivElement, ScrollAreaProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "overflow-auto scrollbar-thin scrollbar-track-transparent scrollbar-thumb-muted/30",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
)
ScrollArea.displayName = "ScrollArea"

export { ScrollArea }