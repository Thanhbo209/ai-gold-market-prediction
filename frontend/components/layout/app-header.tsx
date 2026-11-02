import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { ModeToggle } from "../ui/theme-toggle";

export interface AppHeaderProps {
  readonly marketStatus?: "open" | "closed" | "standby";
  readonly activePath?: string;
}

export function AppHeader({
  marketStatus = "standby",
  activePath = "/",
}: AppHeaderProps): React.JSX.Element {
  const navLinks = [
    { label: "Dashboard", href: "/" },
    { label: "Predictions", href: "#predictions" },
    { label: "Model Registry", href: "#models" },
    { label: "Macro Factors", href: "#macro" },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur-none">
      <div className="flex h-14 items-center justify-between px-4 md:px-6">
        {/* Left: Branding & Identifier */}
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="flex items-center gap-2 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            <div className="h-5 w-5 bg-foreground text-background flex items-center justify-center font-bold text-xs select-none">
              AU
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-sm tracking-tight text-foreground leading-none">
                AI GOLD PREDICTOR
              </span>
              <span className="text-[10px] tracking-widest text-muted-foreground uppercase leading-none mt-1">
                XAU/USD Intelligence
              </span>
            </div>
          </Link>

          {/* Market Status Indicator */}
          <div className="hidden sm:flex items-center pl-4 border-l border-border/80">
            <Badge tone={marketStatus === "open" ? "success" : "muted"}>
              Market: {marketStatus}
            </Badge>
          </div>
        </div>

        {/* Center: Primary Navigation (Desktop) */}
        <nav
          className="hidden md:flex items-center gap-1"
          aria-label="Desktop Primary Navigation"
        >
          {navLinks.map((link) => {
            const isActive = activePath === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 text-xs font-medium uppercase tracking-wider transition-colors border ${
                  isActive
                    ? "border-border bg-secondary text-foreground"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-border/60"
                }`}
                aria-current={isActive ? "page" : undefined}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Right: Operational Info */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <ModeToggle />
          <span className="hidden lg:inline tabular-nums">UTC 24H Feed</span>
          <span className="border-l border-border/80 pl-3 text-[11px] uppercase tracking-wider text-muted-foreground/80">
            Ready
          </span>
        </div>
      </div>

      {/* Accessible Mobile Navigation Bar (Visible on < md Viewports) */}
      <nav
        className="flex md:hidden items-center gap-1.5 px-4 py-2 border-t border-border/70 bg-muted/20 overflow-x-auto"
        aria-label="Mobile Navigation"
      >
        {navLinks.map((link) => {
          const isActive = activePath === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`px-2.5 py-1 text-[11px] uppercase tracking-wider whitespace-nowrap transition-colors border ${
                isActive
                  ? "border-border bg-secondary text-foreground font-semibold"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-border/60"
              }`}
              aria-current={isActive ? "page" : undefined}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
