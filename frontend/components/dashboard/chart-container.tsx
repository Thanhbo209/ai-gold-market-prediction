import type { TimeRange } from "@/types/dashboard";
import { TYPOGRAPHY } from "@/lib/tokens";

export interface ChartContainerProps {
  readonly activeRange?: TimeRange;
}

const TIME_RANGES: readonly TimeRange[] = [
  "1H",
  "24H",
  "7D",
  "30D",
  "90D",
  "1Y",
  "ALL",
];

export function ChartContainer({
  activeRange = "24H",
}: ChartContainerProps): React.JSX.Element {
  return (
    <section
      aria-label="Market Price Chart Container"
      className="border border-border bg-card p-4 md:p-5 flex flex-col h-full"
    >
      {/* Chart Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-border/70">
        <div>
          <h2 className={TYPOGRAPHY.cardTitle}>Price & Trajectory Forecast</h2>
          <p className={TYPOGRAPHY.cardDescription}>
            Historical gold spot price (XAU/USD) with ML predicted confidence
            cone
          </p>
        </div>

        {/* Timeframe Selector */}
        <div
          className="flex items-center border border-border bg-background"
          role="group"
          aria-label="Timeframe"
        >
          {TIME_RANGES.map((range) => {
            const isActive = range === activeRange;
            return (
              <button
                key={range}
                type="button"
                className={`px-2.5 py-1 text-xs font-medium transition-colors border-r border-border last:border-r-0 cursor-pointer ${
                  isActive
                    ? "bg-foreground text-background font-semibold"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
                aria-pressed={isActive}
              >
                {range}
              </button>
            );
          })}
        </div>
      </div>

      {/* Chart Area Container (Structural Placeholder awaiting Chart Library) */}
      <div className="flex-1 min-h-80 md:min-h-95 mt-4 border border-dashed border-border/80 bg-muted/10 flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-md space-y-2">
          <div className="text-[11px]  uppercase tracking-widest text-muted-foreground/70">
            Visualization Viewport
          </div>
          <h3 className="text-sm font-semibold text-foreground tracking-tight">
            Market Chart Container
          </h3>
          <p className={TYPOGRAPHY.cardDescription}>
            Chart integration point prepared for real-time candlestick and
            forecast trajectory rendering. Live data stream connection pending.
          </p>
        </div>
      </div>
    </section>
  );
}
