"use client";

import React from "react";
import { motion } from "motion/react";

interface GaugeProps {
  value: number; // e.g. Current spent or best offer
  max: number; // Target budget
  size?: number;
  label?: string;
  sublabel?: string;
}

export const Gauge: React.FC<GaugeProps> = ({
  value,
  max,
  size = 140,
  label = "BUDGET",
  sublabel,
}) => {
  const strokeWidth = 8;
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const percentage = Math.min(100, Math.max(0, max > 0 ? (value / max) * 100 : 0));
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // Determine color based on budget adherence
  let strokeColor = "#00FF88"; // Green if under budget
  if (percentage > 100) strokeColor = "#FF3333";
  else if (percentage > 90) strokeColor = "#FFB800";

  return (
    <div className="flex flex-col items-center justify-center relative select-none">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1C1C1C"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Animated value track */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          strokeLinecap="butt"
        />
      </svg>

      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="font-mono text-[10px] text-text-secondary uppercase tracking-widest">
          {label}
        </span>
        <span className="font-mono font-bold text-lg text-text-primary">
          {percentage.toFixed(0)}%
        </span>
        {sublabel && (
          <span className="font-mono text-[9px] text-accent uppercase tracking-wider mt-0.5">
            {sublabel}
          </span>
        )}
      </div>
    </div>
  );
};
