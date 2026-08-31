"use client";

import React, { useEffect, useState } from "react";
import { motion } from "motion/react";
import { clsx } from "clsx";

interface WaveformProps {
  isActive?: boolean;
  barsCount?: number;
  color?: "cyan" | "green" | "accent" | "amber";
  className?: string;
}

export const WaveformVisualizer: React.FC<WaveformProps> = ({
  isActive = true,
  barsCount = 18,
  color = "cyan",
  className,
}) => {
  const [heights, setHeights] = useState<number[]>(Array(barsCount).fill(15));

  useEffect(() => {
    if (!isActive) {
      setHeights(Array(barsCount).fill(8));
      return;
    }

    const interval = setInterval(() => {
      setHeights(
        Array.from({ length: barsCount }, () => Math.floor(Math.random() * 85) + 15)
      );
    }, 120);

    return () => clearInterval(interval);
  }, [isActive, barsCount]);

  const colorStyles = {
    cyan: "bg-signal-cyan",
    green: "bg-signal-green",
    accent: "bg-accent",
    amber: "bg-signal-amber",
  };

  return (
    <div className={clsx("flex items-center gap-[3px] h-8 select-none", className)}>
      {heights.map((h, i) => (
        <motion.div
          key={i}
          animate={{ height: `${h}%` }}
          transition={{ duration: 0.1, ease: "linear" }}
          className={clsx(
            "w-[3px] rounded-none transition-colors",
            isActive ? colorStyles[color] : "bg-border-active",
            isActive && "opacity-90"
          )}
        />
      ))}
    </div>
  );
};
