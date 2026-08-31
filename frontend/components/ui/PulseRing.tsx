"use client";

import React from "react";
import { motion } from "motion/react";
import { clsx } from "clsx";

interface PulseRingProps {
  color?: "cyan" | "green" | "amber" | "accent";
  size?: number;
  className?: string;
}

export const PulseRing: React.FC<PulseRingProps> = ({
  color = "cyan",
  size = 40,
  className,
}) => {
  const colorBorders = {
    cyan: "border-signal-cyan",
    green: "border-signal-green",
    amber: "border-signal-amber",
    accent: "border-accent",
  };

  return (
    <div
      className={clsx("relative flex items-center justify-center select-none", className)}
      style={{ width: size, height: size }}
    >
      {/* Expanding Ring 1 */}
      <motion.div
        animate={{ scale: [1, 2.2], opacity: [0.8, 0] }}
        transition={{ duration: 2.0, repeat: Infinity, ease: "easeOut" }}
        className={clsx("absolute inset-0 border", colorBorders[color])}
      />
      {/* Expanding Ring 2 */}
      <motion.div
        animate={{ scale: [1, 2.2], opacity: [0.8, 0] }}
        transition={{ duration: 2.0, repeat: Infinity, ease: "easeOut", delay: 0.6 }}
        className={clsx("absolute inset-0 border", colorBorders[color])}
      />
      {/* Center Solid Node */}
      <div
        className={clsx(
          "w-3 h-3 bg-current border border-black",
          color === "cyan" && "text-signal-cyan",
          color === "green" && "text-signal-green",
          color === "amber" && "text-signal-amber",
          color === "accent" && "text-accent"
        )}
      />
    </div>
  );
};
