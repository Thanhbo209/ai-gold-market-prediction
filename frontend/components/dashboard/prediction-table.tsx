import type { PredictionRecord } from "@/types/dashboard";
import { TYPOGRAPHY, getDirectionClasses } from "@/lib/tokens";
import { Badge } from "@/components/ui/badge";

export interface PredictionTableProps {
  readonly records?: readonly PredictionRecord[];
}

export function PredictionTable({
  records = [],
}: PredictionTableProps): React.JSX.Element {
  return (
    <section
      aria-label="Recent Model Predictions Log"
      className="border border-border bg-card p-4 md:p-5 mt-6"
    >
      {/* Table Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 mb-3 border-b border-border/70">
        <div>
          <h2 className={TYPOGRAPHY.cardTitle}>
            Inference & Prediction History
          </h2>
          <p className={TYPOGRAPHY.cardDescription}>
            Audit log of generated model forecasts and validation statuses
          </p>
        </div>
        <div className="text-xs text-muted-foreground">
          Showing {records.length} records
        </div>
      </div>

      {/* Semantic Table Container */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-border bg-muted/40 text-muted-foreground uppercase text-[11px] tracking-wider">
              <th scope="col" className="py-2.5 px-3 font-semibold">
                Timestamp (UTC)
              </th>
              <th scope="col" className="py-2.5 px-3 font-semibold">
                Model
              </th>
              <th scope="col" className="py-2.5 px-3 font-semibold">
                Horizon
              </th>
              <th scope="col" className="py-2.5 px-3 font-semibold">
                Direction
              </th>
              <th scope="col" className="py-2.5 px-3 font-semibold text-right">
                Target Price
              </th>
              <th scope="col" className="py-2.5 px-3 font-semibold text-right">
                Confidence
              </th>
              <th scope="col" className="py-2.5 px-3 font-semibold text-center">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {records.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className="py-8 text-center text-muted-foreground"
                >
                  <div className="space-y-1">
                    <p className="font-semibold text-foreground text-xs">
                      No predictions logged yet
                    </p>
                    <p className="text-[11px] text-muted-foreground">
                      Inference records will appear here as models run scheduled
                      forecasts.
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              records.map((record) => {
                const directionClasses = getDirectionClasses(record.direction);
                return (
                  <tr
                    key={record.id}
                    className="hover:bg-muted/30 transition-colors"
                  >
                    <td className="py-2 px-3 whitespace-nowrap text-muted-foreground">
                      {record.timestamp}
                    </td>
                    <td className="py-2 px-3 whitespace-nowrap font-semibold text-foreground">
                      {record.modelName}
                    </td>
                    <td className="py-2 px-3 whitespace-nowrap text-muted-foreground">
                      {record.horizon}
                    </td>
                    <td className="py-2 px-3 whitespace-nowrap">
                      <span
                        className={`inline-block font-semibold uppercase ${directionClasses.text}`}
                      >
                        {record.direction}
                      </span>
                    </td>
                    <td className="py-2 px-3 whitespace-nowrap text-right tabular-nums">
                      {record.targetPrice !== null
                        ? `$${record.targetPrice.toFixed(2)}`
                        : "--"}
                    </td>
                    <td className="py-2 px-3 whitespace-nowrap text-right tabular-nums">
                      {record.confidenceScore !== null
                        ? `${(record.confidenceScore * 100).toFixed(1)}%`
                        : "--"}
                    </td>
                    <td className="py-2 px-3 whitespace-nowrap text-center">
                      <Badge
                        tone={
                          record.status === "fulfilled"
                            ? "success"
                            : record.status === "pending"
                              ? "warning"
                              : "muted"
                        }
                      >
                        {record.status}
                      </Badge>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
