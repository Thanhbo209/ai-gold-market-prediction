import type { MetricSlot } from "@/types/dashboard";
import { TYPOGRAPHY, getDirectionClasses } from "@/lib/tokens";

export interface MetricCardProps {
  readonly slot: MetricSlot;
}

export function MetricCard({ slot }: MetricCardProps): React.JSX.Element {
  const directionClasses = getDirectionClasses(slot.direction);

  return (
    <div className="border border-border bg-card text-card-foreground p-4 flex flex-col justify-between">
      {/* Title & Status */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <span className={TYPOGRAPHY.metricLabel}>{slot.title}</span>
          {slot.description && (
            <p className="text-[11px] text-muted-foreground mt-0.5">{slot.description}</p>
          )}
        </div>
        <span className="text-[10px] font-mono px-1.5 py-0.5 bg-muted text-muted-foreground border border-border uppercase">
          {slot.statusText}
        </span>
      </div>

      {/* Main Metric Value */}
      <div className="mt-3">
        {slot.isAwaitingData || slot.value === null ? (
          <div className="space-y-1">
            <div className="text-xl font-mono text-muted-foreground/60 tracking-wider">
              --
            </div>
            <div className="text-[11px] font-mono text-muted-foreground/80">
              Awaiting data stream
            </div>
          </div>
        ) : (
          <div className="flex items-baseline gap-3">
            <span className={TYPOGRAPHY.metricValue}>{slot.value}</span>
            {slot.change && (
              <span
                className={`text-xs font-mono font-medium tabular-nums ${directionClasses.text}`}
              >
                {slot.direction === "up" && "▲ "}
                {slot.direction === "down" && "▼ "}
                {slot.change}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
