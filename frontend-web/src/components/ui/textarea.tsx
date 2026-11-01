"use client";

import { forwardRef } from "react";
import { clsx } from "clsx";

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className, id, ...props }, ref) => {
    const textareaId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="space-y-1.5">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-display font-medium text-gray-700 dark:text-gray-300"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          className={clsx(
            "w-full px-4 py-2.5 text-sm font-body",
            "bg-white dark:bg-surface-dark border border-gray-300 dark:border-gray-600",
            "rounded-[10px] transition-colors duration-150 resize-y min-h-[80px]",
            "placeholder:text-gray-400 dark:placeholder:text-gray-500",
            "focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent",
            error && "border-error focus:ring-error",
            className
          )}
          {...props}
        />
        {error && <p className="text-xs text-error font-medium">{error}</p>}
      </div>
    );
  }
);

Textarea.displayName = "Textarea";
