import type { PredictionSignal } from "@/types/dashboard";
import { TYPOGRAPHY, getDirectionClasses } from "@/lib/tokens";
import { Badge } from "@/components/ui/badge";

export interface PredictionPanelProps {
  readonly currentSignal?: PredictionSignal | null;
}

export function PredictionPanel({
  currentSignal = null,
}: PredictionPanelProps): React.JSX.Element {
  const isAwaitingSignal = currentSignal === null;
  const directionClasses = getDirectionClasses(currentSignal?.direction);

  return (
    <section
      aria-label="Latest Prediction Signal"
      className="border border-border bg-card p-4 md:p-5 flex flex-col justify-between"
    >
      <div>
        {/* Panel Header */}
        <div className="flex items-center justify-between pb-3 border-b border-border/70">
          <div>
            <h2 className={TYPOGRAPHY.cardTitle}>Latest Model Inference</h2>
            <p className={TYPOGRAPHY.cardDescription}>
              Multi-horizon AI directional forecast
            </p>
          </div>
          <Badge tone={isAwaitingSignal ? "muted" : "success"}>
            {isAwaitingSignal ? "Standby" : "Active"}
          </Badge>
        </div>

        {/* Signal Overview */}
        <div className="py-4 border-b border-border/70 space-y-3">
          <div className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground">
            Forecast Signal
          </div>

          {isAwaitingSignal ? (
            <div className="p-3 bg-muted/30 border border-border space-y-1.5">
              <div className="text-xs font-mono font-semibold text-foreground">
                Inference Engine: Idle
              </div>
              <p className="text-xs text-muted-foreground">
                Awaiting market tick trigger or scheduled inference job to generate next target
                trajectory.
              </p>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div>
                <div
                  className={`text-2xl font-mono font-bold tracking-tight uppercase ${directionClasses.text}`}
                >
                  {currentSignal.direction}
                </div>
                <div className="text-xs font-mono text-muted-foreground">
                  Horizon: {currentSignal.horizon}
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs font-mono text-muted-foreground">Confidence</div>
                <div className="text-base font-mono font-semibold tabular-nums text-foreground">
                  {(currentSignal.confidenceScore * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Inference Parameters */}
        <div className="py-4 space-y-2.5 text-xs font-mono">
          <div className="text-[11px] uppercase tracking-widest text-muted-foreground">
            Model Specifications
          </div>
          <div className="space-y-1.5 border border-border p-3 bg-background/50">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Algorithm:</span>
              <span className="text-foreground font-medium">LSTM + Transformer</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Horizon:</span>
              <span className="text-foreground">24h / 7d Multi-step</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Features:</span>
              <span className="text-foreground">DXY, Yields, VIX, Oil</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Validation:</span>
              <span className="text-market-up">Walk-forward Validated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-3 border-t border-border/70 text-[11px] font-mono text-muted-foreground">
        Signals are probabilistic forecasts; strictly for decision support.
      </div>
    </section>
  );
}
