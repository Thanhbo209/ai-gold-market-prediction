import Link from "next/link";
import type { NavItem } from "@/types/dashboard";

export interface AppSidebarProps {
  readonly items?: readonly NavItem[];
  readonly currentPath?: string;
}

const DEFAULT_NAV_ITEMS: readonly NavItem[] = [
  { id: "overview", label: "Market Overview", href: "/", isActive: true },
  { id: "forecasts", label: "Model Predictions", href: "#predictions" },
  { id: "models", label: "Model Registry", href: "#models" },
  { id: "macro", label: "Macro Factors", href: "#macro" },
  { id: "eval", label: "Backtest & Metrics", href: "#backtest" },
  { id: "system", label: "Pipeline Status", href: "#system" },
];

export function AppSidebar({
  items = DEFAULT_NAV_ITEMS,
  currentPath = "/",
}: AppSidebarProps): React.JSX.Element {
  return (
    <aside
      className="hidden lg:flex w-60 shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground min-h-[calc(100vh-3.5rem)] select-none"
      aria-label="Sidebar Navigation"
    >
      {/* Navigation Group */}
      <div className="p-4 space-y-6">
        <div>
          <div className="px-2 pb-2 text-[11px] uppercase tracking-widest text-muted-foreground/80">
            Navigation
          </div>
          <nav className="flex flex-col gap-0.5">
            {items.map((item) => {
              const isActive = item.href === currentPath || item.isActive;
              return (
                <Link
                  key={item.id}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2 text-xs font-medium tracking-wide border-l-2 transition-colors ${
                    isActive
                      ? "border-sidebar-primary bg-sidebar-accent text-sidebar-accent-foreground font-semibold"
                      : "border-transparent text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="text-[10px] px-1 py-0.2 bg-muted text-muted-foreground border border-border">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* System Specs Box */}
        <div className="border border-sidebar-border p-3 space-y-2 bg-background/50">
          <div className="text-[10px] uppercase tracking-widest text-muted-foreground">
            Environment
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between text-muted-foreground">
              <span>Target Asset:</span>
              <span className="text-foreground font-semibold">XAU/USD</span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>Engine:</span>
              <span className="text-foreground">Prediction Core</span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>Mode:</span>
              <span className="text-market-up">Ready</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="mt-auto p-4 border-t border-sidebar-border text-[11px] text-muted-foreground">
        <div>v0.1.0-alpha</div>
        <div className="text-[10px] text-muted-foreground/70 mt-0.5">
          Sharp-edge Design System
        </div>
      </div>
    </aside>
  );
}
