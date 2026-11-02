import type { SystemStatus } from "@/types/dashboard";
import { Badge } from "@/components/ui/badge";

export interface MarketStatusBarProps {
  readonly status?: SystemStatus;
}

const DEFAULT_STATUS: SystemStatus = {
  marketState: "standby",
  pipelineStatus: "idle",
  lastUpdated: null,
  activeModelVersion: "Ensemble-v1.0-alpha",
};

export function MarketStatusBar({
  status = DEFAULT_STATUS,
}: MarketStatusBarProps): React.JSX.Element {
  return (
    <section
      aria-label="System and Market Status"
      className="border border-border bg-card p-3 md:p-4 mb-6 flex flex-wrap items-center justify-between gap-4 text-xs"
    >
      {/* Left Details */}
      <div className="flex flex-wrap items-center gap-4 sm:gap-6">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground uppercase tracking-wider">
            Feed:
          </span>
          <Badge
            tone={
              status.marketState === "open"
                ? "success"
                : status.marketState === "standby"
                  ? "warning"
                  : "muted"
            }
          >
            {status.marketState}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-muted-foreground uppercase tracking-wider">
            Pipeline:
          </span>
          <span className="text-foreground font-semibold uppercase">
            {status.pipelineStatus}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-muted-foreground uppercase tracking-wider">
            Active Model:
          </span>
          <span className="text-foreground">{status.activeModelVersion}</span>
        </div>
      </div>

      {/* Right Details */}
      <div className="flex items-center gap-3 text-muted-foreground">
        <span>Last Checkpoint:</span>
        <span className="text-foreground tabular-nums">
          {status.lastUpdated ? status.lastUpdated : "Awaiting initial sync"}
        </span>
      </div>
    </section>
  );
}
