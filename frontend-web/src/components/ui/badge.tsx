import { clsx } from "clsx";

type BadgeVariant =
  | "default"
  | "success"
  | "warning"
  | "error"
  | "accent"
  | "secondary";

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300",
  success: "bg-success-light dark:bg-success/20 text-success",
  warning: "bg-warning-light dark:bg-warning/20 text-warning",
  error: "bg-error-light dark:bg-error/20 text-error",
  accent: "bg-accent-50 dark:bg-accent/20 text-accent",
  secondary: "bg-secondary/10 text-secondary",
};

export function Badge({ variant = "default", children, className }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 px-2.5 py-0.5",
        "text-xs font-display font-semibold rounded-full",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
