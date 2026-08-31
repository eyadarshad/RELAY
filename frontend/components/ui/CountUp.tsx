"use client";

import React, { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "motion/react";

interface CountUpProps {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  duration?: number;
  className?: string;
}

export const CountUp: React.FC<CountUpProps> = ({
  value,
  prefix = "",
  suffix = "",
  decimals = 0,
  duration = 1.5,
  className,
}) => {
  const spring = useSpring(0, {
    duration: duration * 1000,
    bounce: 0,
  });

  const [displayValue, setDisplayValue] = useState<string>("0");

  useEffect(() => {
    spring.set(value);
  }, [value, spring]);

  useEffect(() => {
    return spring.on("change", (latest) => {
      const formatted = decimals > 0
        ? latest.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
        : Math.round(latest).toLocaleString("en-US");
      setDisplayValue(formatted);
    });
  }, [spring, decimals]);

  return (
    <span className={className}>
      {prefix}
      {displayValue}
      {suffix}
    </span>
  );
};
