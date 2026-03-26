import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const variants = {
      default: "bg-dark-accent-primary text-[#f1ebdf] hover:bg-dark-accent-secondary",
      destructive: "bg-semantic-danger text-[#f1ebdf] hover:bg-semantic-danger/90",
      outline: "border border-[#f1ebdf]/10 bg-transparent hover:bg-[#f1ebdf]/5 text-dark-text-primary",
      secondary: "bg-dark-border text-dark-text-primary hover:bg-dark-border/80",
      ghost: "hover:bg-[#f1ebdf]/5 text-dark-text-primary",
      link: "text-dark-accent-primary underline-offset-4 hover:underline",
    }

    const sizes = {
      default: "h-10 px-4 py-2",
      sm: "h-9 rounded-md px-3",
      lg: "h-11 rounded-md px-8",
      icon: "h-10 w-10",
    }

    return (
      <button
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-dark-bg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-dark-accent-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 glass-press",
          variants[variant],
          sizes[size],
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
