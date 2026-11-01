import { clsx } from "clsx";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: "sm" | "md" | "lg";
}

const paddingStyles = {
  sm: "p-4",
  md: "p-6",
  lg: "p-8",
};

export function Card({ children, className, padding = "md" }: CardProps) {
  return (
    <div
      className={clsx(
        "bg-white dark:bg-surface-dark border border-gray-200 dark:border-gray-700",
        "rounded-[10px] shadow-sm",
        paddingStyles[padding],
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        "flex items-center justify-between pb-4 mb-4 border-b border-gray-200 dark:border-gray-700",
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardTitle({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <h3
      className={clsx(
        "font-display font-bold text-lg text-gray-900 dark:text-white",
        className
      )}
    >
      {children}
    </h3>
  );
}
