"use client";

import React from "react";
import { motion, HTMLMotionProps } from "motion/react";
import { clsx } from "clsx";

interface CardProps extends HTMLMotionProps<"div"> {
  title?: string;
  badge?: React.ReactNode;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
  variant?: "default" | "glow" | "active" | "danger" | "raised";
  withCorners?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  badge,
  headerAction,
  children,
  variant = "default",
  withCorners = true,
  className,
  ...props
}) => {
  const variantStyles = {
    default: "bg-surface border-border",
    raised: "bg-surface-raised border-border",
    glow: "bg-surface border-accent/40 acid-glow-sm",
    active: "bg-surface border-signal-cyan/40 cyan-glow",
    danger: "bg-surface border-signal-red/40",
  };

  return (
    <motion.div
      className={clsx(
        "relative border p-4 sm:p-5 transition-colors duration-200",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {/* Brutalist Corner Crosshairs */}
      {withCorners && (
        <>
          <span className="absolute -top-1.5 -left-1.5 font-mono text-[10px] text-border-active select-none pointer-events-none">
            +
          </span>
          <span className="absolute -top-1.5 -right-1.5 font-mono text-[10px] text-border-active select-none pointer-events-none">
            +
          </span>
          <span className="absolute -bottom-1.5 -left-1.5 font-mono text-[10px] text-border-active select-none pointer-events-none">
            +
          </span>
          <span className="absolute -bottom-1.5 -right-1.5 font-mono text-[10px] text-border-active select-none pointer-events-none">
            +
          </span>
        </>
      )}

      {(title || badge || headerAction) && (
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-border/80">
          <div className="flex items-center gap-2.5">
            {title && (
              <h3 className="font-display font-bold uppercase tracking-wider text-xs sm:text-sm text-text-primary">
                {title}
              </h3>
            )}
            {badge}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}

      {children}
    </motion.div>
  );
};
