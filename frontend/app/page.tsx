import type { MetricSlot } from "@/types/dashboard";
import { AppShell } from "@/components/layout/app-shell";
import { MarketStatusBar } from "@/components/dashboard/market-status-bar";
import { MetricCard } from "@/components/dashboard/metric-card";
import { ChartContainer } from "@/components/dashboard/chart-container";
import { PredictionPanel } from "@/components/dashboard/prediction-panel";
import { PredictionTable } from "@/components/dashboard/prediction-table";
import { TYPOGRAPHY } from "@/lib/tokens";

const INITIAL_METRIC_SLOTS: readonly MetricSlot[] = [
  {
    id: "gold-spot",
    title: "Gold Spot (XAU/USD)",
    description: "Real-time bullion spot reference",
    value: null,
    change: null,
    direction: "neutral",
    statusText: "Feed Standby",
    isAwaitingData: true,
  },
  {
    id: "change-24h",
    title: "24H Net Change",
    description: "Daily trading window delta",
    value: null,
    change: null,
    direction: "neutral",
    statusText: "Standby",
    isAwaitingData: true,
  },
  {
    id: "model-consensus",
    title: "AI Signal Consensus",
    description: "Multi-model ensemble vote",
    value: null,
    direction: "neutral",
    statusText: "Awaiting Run",
    isAwaitingData: true,
  },
  {
    id: "volatility-regime",
    title: "Volatility Regime",
    description: "Realized Parkinson volatility",
    value: null,
    direction: "neutral",
    statusText: "Standby",
    isAwaitingData: true,
  },
];

export default function DashboardPage(): React.JSX.Element {
  return (
    <AppShell>
      {/* Page Title & Context Header */}
      <div className="mb-6 pb-4 border-b border-border/80 flex flex-col md:flex-row md:items-end justify-between gap-3">
        <div>
          <div className="text-[11px] uppercase tracking-widest text-muted-foreground">
            Market Intelligence Platform
          </div>
          <h1 className={TYPOGRAPHY.pageTitle}>AI Gold Market Prediction</h1>
          <p className={TYPOGRAPHY.pageSubtitle}>
            Real-time quantitative forecasting, macroeconomic feature
            attribution, and trend prediction
          </p>
        </div>
        <div className="text-xs text-muted-foreground flex items-center gap-2">
          <span>Engine Status:</span>
          <span className="text-market-up font-semibold uppercase">
            Initialized
          </span>
        </div>
      </div>

      {/* Operational Status Bar */}
      <MarketStatusBar />

      {/* Metric Cards Grid */}
      <section
        aria-label="Market Overview Metrics"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
      >
        {INITIAL_METRIC_SLOTS.map((slot) => (
          <MetricCard key={slot.id} slot={slot} />
        ))}
      </section>

      {/* Main Analysis Grid: Chart + AI Prediction Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChartContainer activeRange="24H" />
        </div>
        <div className="lg:col-span-1">
          <PredictionPanel currentSignal={null} />
        </div>
      </div>

      {/* Historical Inference Log Table */}
      <PredictionTable records={[]} />
    </AppShell>
  );
}
