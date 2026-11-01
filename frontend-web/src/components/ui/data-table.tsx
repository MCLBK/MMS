"use client";

import { clsx } from "clsx";
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react";

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyField: string;
  page?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  onRowClick?: (item: T) => void;
  isLoading?: boolean;
  emptyIcon?: React.ReactNode;
  emptyMessage?: string;
  emptyDescription?: string;
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  keyField,
  page = 1,
  totalPages = 1,
  onPageChange,
  onRowClick,
  isLoading,
  emptyIcon,
  emptyMessage = "Aucune donnee",
  emptyDescription,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-surface-dark border border-gray-200 dark:border-gray-700 rounded-[10px] overflow-hidden">
        <div className="animate-pulse p-6 space-y-4">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="bg-white dark:bg-surface-dark border border-gray-200 dark:border-gray-700 rounded-[10px] p-12">
        <div className="text-center">
          {emptyIcon && <div className="mx-auto mb-4 text-gray-300 dark:text-gray-600">{emptyIcon}</div>}
          <p className="text-gray-500 dark:text-gray-400 font-medium">{emptyMessage}</p>
          {emptyDescription && (
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">{emptyDescription}</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-surface-dark border border-gray-200 dark:border-gray-700 rounded-[10px] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={clsx(
                    "text-left px-4 py-3 text-xs font-display font-semibold uppercase tracking-wider",
                    "text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-surface-dark-alt",
                    col.className
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr
                key={item[keyField]}
                onClick={() => onRowClick?.(item)}
                className={clsx(
                  "border-b border-gray-100 dark:border-gray-800 last:border-b-0",
                  "hover:bg-gray-50 dark:hover:bg-surface-dark-alt transition-colors duration-100",
                  onRowClick && "cursor-pointer"
                )}
              >
                {columns.map((col) => (
                  <td key={col.key} className={clsx("px-4 py-3 text-sm", col.className)}>
                    {col.render ? col.render(item) : item[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && onPageChange && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Page {page} sur {totalPages}
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => onPageChange(1)}
              disabled={page <= 1}
              className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-surface-dark-alt disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronsLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-surface-dark-alt disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-surface-dark-alt disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onPageChange(totalPages)}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-surface-dark-alt disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronsRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
