import type { HTMLAttributes, ReactNode } from "react";
import type { StatusTone } from "@/types/tokens";
import { getStatusToneClasses } from "@/lib/tokens";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  readonly children: ReactNode;
  readonly tone?: StatusTone;
  readonly className?: string;
}

export function Badge({
  children,
  tone = "default",
  className = "",
  ...props
}: BadgeProps): React.JSX.Element {
  const toneClasses = getStatusToneClasses(tone);

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-[11px] font-mono font-medium uppercase tracking-wider border ${toneClasses.bg} ${toneClasses.text} ${toneClasses.border} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
