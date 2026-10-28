import type { MarketDirection, StatusTone } from "@/types/tokens";

/**
 * Shared typography token class compositions.
 * Enforces clear visual hierarchy, readability, and tabular numbers for financial data.
 */
export const TYPOGRAPHY = {
  pageTitle: "text-lg md:text-xl font-semibold tracking-tight text-foreground",
  pageSubtitle: "text-xs md:text-sm text-muted-foreground",
  sectionTitle: "text-xs font-semibold uppercase tracking-wider text-muted-foreground",
  cardTitle: "text-sm font-semibold text-foreground tracking-tight",
  cardDescription: "text-xs text-muted-foreground",
  metricValue: "text-2xl font-mono font-semibold tabular-nums tracking-tight text-foreground",
  metricLabel: "text-xs font-medium uppercase tracking-wider text-muted-foreground",
  body: "text-sm text-foreground leading-normal",
  caption: "text-xs text-muted-foreground tabular-nums",
  code: "font-mono text-xs bg-muted px-1 py-0.5 border border-border",
} as const;

/**
 * Returns consistent Tailwind utility classes for market direction indicators.
 * Strictly avoids rounded utilities and adheres to the restrained color palette.
 */
export function getDirectionClasses(direction?: MarketDirection): {
  readonly text: string;
  readonly bg: string;
  readonly border: string;
} {
  switch (direction) {
    case "up":
      return {
        text: "text-market-up",
        bg: "bg-market-up/10",
        border: "border-market-up/30",
      };
    case "down":
      return {
        text: "text-market-down",
        bg: "bg-market-down/10",
        border: "border-market-down/30",
      };
    case "neutral":
    default:
      return {
        text: "text-market-neutral",
        bg: "bg-muted",
        border: "border-border",
      };
  }
}

/**
 * Returns consistent badge utility classes based on status tone.
 */
export function getStatusToneClasses(tone: StatusTone): {
  readonly text: string;
  readonly bg: string;
  readonly border: string;
} {
  switch (tone) {
    case "success":
      return {
        text: "text-market-up",
        bg: "bg-market-up/10",
        border: "border-market-up/30",
      };
    case "destructive":
      return {
        text: "text-destructive",
        bg: "bg-destructive/10",
        border: "border-destructive/30",
      };
    case "warning":
      return {
        text: "text-primary",
        bg: "bg-primary/10",
        border: "border-primary/30",
      };
    case "muted":
      return {
        text: "text-muted-foreground",
        bg: "bg-muted/50",
        border: "border-border",
      };
    case "default":
    default:
      return {
        text: "text-foreground",
        bg: "bg-secondary",
        border: "border-border",
      };
  }
}
