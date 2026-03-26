import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.ComponentProps<"div"> {
  variant?: "default" | "success" | "warning" | "danger" | "info" | "outline";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "bg-dark-border text-dark-text-primary",
    success: "bg-semantic-success/20 text-semantic-success",
    warning: "bg-semantic-warning/20 text-semantic-warning",
    danger: "bg-semantic-danger/20 text-semantic-danger",
    info: "bg-semantic-info/20 text-semantic-info",
    outline: "text-dark-text-primary border border-[#f1ebdf]/10",
  }

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-dark-accent-primary focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }
