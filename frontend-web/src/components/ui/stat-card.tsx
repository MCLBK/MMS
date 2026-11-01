import { clsx } from "clsx";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
  icon: React.ReactNode;
  iconColor?: string;
}

export function StatCard({
  label,
  value,
  change,
  trend = "neutral",
  icon,
  iconColor = "text-accent bg-accent/10",
}: StatCardProps) {
  return (
    <div className="bg-white dark:bg-surface-dark border border-gray-200 dark:border-gray-700 rounded-[10px] p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">
            {label}
          </p>
          <p className="font-display font-bold text-3xl text-gray-900 dark:text-white tabular-nums">
            {value}
          </p>
          {change && (
            <div className="flex items-center gap-1.5">
              {trend === "up" && <TrendingUp className="w-3.5 h-3.5 text-success" />}
              {trend === "down" && <TrendingDown className="w-3.5 h-3.5 text-error" />}
              {trend === "neutral" && <Minus className="w-3.5 h-3.5 text-gray-400" />}
              <span
                className={clsx(
                  "text-xs font-semibold",
                  trend === "up" && "text-success",
                  trend === "down" && "text-error",
                  trend === "neutral" && "text-gray-400"
                )}
              >
                {change}
              </span>
            </div>
          )}
        </div>
        <div className={clsx("w-11 h-11 rounded-xl flex items-center justify-center", iconColor)}>
          {icon}
        </div>
      </div>
    </div>
  );
}
