"use client";

import { clsx } from "clsx";

interface Tab {
  value: string;
  label: string;
  count?: number;
}

interface TabsProps {
  tabs: Tab[];
  value: string;
  onChange: (value: string) => void;
}

export function Tabs({ tabs, value, onChange }: TabsProps) {
  return (
    <div className="flex gap-1 p-1 bg-gray-100 dark:bg-surface-dark-alt rounded-xl">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={clsx(
            "px-4 py-2 rounded-lg text-sm font-display font-medium transition-all duration-150",
            value === tab.value
              ? "bg-white dark:bg-surface-dark text-gray-900 dark:text-white shadow-sm"
              : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          )}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span
              className={clsx(
                "ml-2 px-1.5 py-0.5 text-xs rounded-md font-semibold tabular-nums",
                value === tab.value
                  ? "bg-accent/10 text-accent"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
              )}
            >
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
