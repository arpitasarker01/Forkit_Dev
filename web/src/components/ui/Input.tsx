import React from 'react';

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        className={`flex h-10 w-full rounded-md border border-[#f1ebdf]/10 bg-dark-bg px-3 py-2 text-sm text-[#f1ebdf] placeholder:text-dark-text-secondary focus:outline-none focus:ring-1 focus:ring-dark-accent-primary disabled:cursor-not-allowed disabled:opacity-50 ${className || ''}`}
        ref={ref}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';
