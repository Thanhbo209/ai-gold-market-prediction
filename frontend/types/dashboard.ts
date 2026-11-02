import type { MarketDirection, StatusTone } from "./tokens";

/**
 * Navigation item definition for application header and sidebar.
 */
export interface NavItem {
  readonly id: string;
  readonly label: string;
  readonly href: string;
  readonly isActive?: boolean;
  readonly badge?: string;
}

/**
 * Metric slot definition for dashboard summary cards.
 * Supports explicit empty/awaiting states to prevent fabricated data.
 */
export interface MetricSlot {
  readonly id: string;
  readonly title: string;
  readonly description?: string;
  readonly value: string | null;
  readonly change?: string | null;
  readonly direction?: MarketDirection;
  readonly statusText: string;
  readonly tone?: StatusTone;
  readonly isAwaitingData: boolean;
}

/**
 * Typed real-time prediction signal emitted by the ML inference engine.
 */
export interface PredictionSignal {
  readonly direction: MarketDirection;
  readonly horizon: string;
  readonly confidenceScore: number;
  readonly targetPrice?: number | null;
  readonly modelName: string;
}

/**
 * Record representing a historical or queued prediction log entry.
 */
export interface PredictionRecord {
  readonly id: string;
  readonly timestamp: string;
  readonly modelName: string;
  readonly horizon: string;
  readonly direction: MarketDirection;
  readonly targetPrice: number | null;
  readonly confidenceScore: number | null;
  readonly status: "pending" | "fulfilled" | "expired";
}

/**
 * Chart time range options.
 */
export type TimeRange = "1H" | "24H" | "7D" | "30D" | "90D" | "1Y" | "ALL";

/**
 * System and market operational status.
 */
export interface SystemStatus {
  readonly marketState: "open" | "closed" | "standby";
  readonly pipelineStatus: "online" | "syncing" | "idle" | "error";
  readonly lastUpdated: string | null;
  readonly activeModelVersion: string;
}
