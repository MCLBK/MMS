"use client";

import { BarChart3 } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const PIE_COLORS = [
  "#FF6B35",
  "#2DD4BF",
  "#0F1B2D",
  "#22C55E",
  "#F59E0B",
  "#EF4444",
  "#8B5CF6",
  "#64748B",
];

interface Props {
  daily: Array<{ date: string; created: number; completed: number; failed: number }>;
  pieData: Array<{ name: string; value: number }>;
}

export function DailyTrendChart({ data }: { data: Props["daily"] }) {
  return (
    <div className="h-72 px-2">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: "#94A3B8" }}
            tickFormatter={(d: string) =>
              new Date(d).toLocaleDateString("fr-FR", { day: "2-digit", month: "short" })
            }
          />
          <YAxis tick={{ fontSize: 12, fill: "#94A3B8" }} width={35} />
          <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #E2E8F0", fontSize: 13 }} />
          <Legend wrapperStyle={{ fontSize: 13 }} />
          <Line type="monotone" dataKey="created" name="Créées" stroke="#FF6B35" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="completed" name="Terminées" stroke="#22C55E" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="failed" name="Échouées" stroke="#EF4444" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function StatusPieChart({ data }: { data: Props["pieData"] }) {
  if (data.length === 0) {
    return (
      <div className="h-72 px-2 flex items-center justify-center text-gray-400">
        <div className="text-center">
          <BarChart3 className="w-10 h-10 mx-auto mb-3 opacity-50" />
          <p className="text-sm">Les données apparaîtront avec les commandes</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-72 px-2">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
            {data.map((_, i) => (
              <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #E2E8F0", fontSize: 13 }} />
          <Legend wrapperStyle={{ fontSize: 12 }} layout="vertical" align="right" verticalAlign="middle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function AnalyticsCharts({ daily, pieData }: Props) {
  return (
    <>
      <DailyTrendChart data={daily} />
      <StatusPieChart data={pieData} />
    </>
  );
}
