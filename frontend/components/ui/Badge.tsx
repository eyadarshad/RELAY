"use client";

import React from "react";
import { clsx } from "clsx";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "green" | "cyan" | "amber" | "red" | "accent" | "neutral";
  size?: "sm" | "md";
  pulse?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "neutral",
  size = "sm",
  pulse = false,
  className,
}) => {
  const sizeStyles = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
  };

  const variantStyles = {
    green: "bg-signal-green/10 text-signal-green border-signal-green/30",
    cyan: "bg-signal-cyan/10 text-signal-cyan border-signal-cyan/30",
    amber: "bg-signal-amber/10 text-signal-amber border-signal-amber/30",
    red: "bg-signal-red/10 text-signal-red border-signal-red/30",
    accent: "bg-accent/10 text-accent border-accent/40",
    neutral: "bg-surface-raised text-text-secondary border-border",
  };

  const dotColors = {
    green: "bg-signal-green",
    cyan: "bg-signal-cyan",
    amber: "bg-signal-amber",
    red: "bg-signal-red",
    accent: "bg-accent",
    neutral: "bg-text-secondary",
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 font-mono uppercase tracking-widest border select-none font-semibold",
        sizeStyles[size],
        variantStyles[variant],
        className
      )}
    >
      {pulse && (
        <span className="relative flex h-1.5 w-1.5">
          <span
            className={clsx(
              "animate-ping absolute inline-flex h-full w-full opacity-75",
              dotColors[variant]
            )}
          />
          <span className={clsx("relative inline-flex h-1.5 w-1.5", dotColors[variant])} />
        </span>
      )}
      {children}
    </span>
  );
};
