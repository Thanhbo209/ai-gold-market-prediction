import type { ReactNode } from "react";
import { AppHeader } from "./app-header";
import { AppSidebar } from "./app-sidebar";

export interface AppShellProps {
  readonly children: ReactNode;
}

export function AppShell({ children }: AppShellProps): React.JSX.Element {
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground antialiased selection:bg-foreground selection:text-background">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:px-3 focus:py-1.5 focus:bg-foreground focus:text-background focus:font-mono focus:text-xs focus:border focus:border-border"
      >
        Skip to main content
      </a>
      <AppHeader />
      <div className="flex flex-1 w-full">
        <AppSidebar />
        <main
          className="flex-1 w-full px-4 py-5 md:px-8 md:py-6 max-w-7xl mx-auto overflow-x-hidden"
          id="main-content"
          tabIndex={-1}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
