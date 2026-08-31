"use client";

import React from "react";
import { motion, HTMLMotionProps } from "motion/react";
import { clsx } from "clsx";

interface ButtonProps extends HTMLMotionProps<"button"> {
  variant?: "primary" | "secondary" | "danger" | "ghost" | "cyan";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  children,
  icon,
  className,
  disabled,
  ...props
}) => {
  const baseStyles =
    "relative inline-flex items-center justify-center font-mono font-medium uppercase tracking-wider transition-all duration-200 select-none disabled:opacity-40 disabled:pointer-events-none cursor-pointer";

  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs gap-1.5 border",
    md: "px-5 py-2.5 text-sm gap-2 border",
    lg: "px-7 py-3.5 text-base gap-2.5 border-2 font-bold",
  };

  const variantStyles = {
    primary:
      "bg-accent text-void border-accent hover:bg-transparent hover:text-accent hover:acid-glow active:scale-[0.98]",
    secondary:
      "bg-surface text-text-primary border-border hover:border-accent hover:text-accent hover:bg-surface-raised active:scale-[0.98]",
    danger:
      "bg-signal-red/10 text-signal-red border-signal-red/50 hover:bg-signal-red hover:text-void active:scale-[0.98]",
    cyan:
      "bg-signal-cyan/10 text-signal-cyan border-signal-cyan/50 hover:bg-signal-cyan hover:text-void cyan-glow active:scale-[0.98]",
    ghost:
      "bg-transparent text-text-secondary border-transparent hover:border-border hover:text-text-primary hover:bg-surface",
  };

  return (
    <motion.button
      whileHover={{ y: -1 }}
      whileTap={{ y: 1 }}
      className={clsx(baseStyles, sizeStyles[size], variantStyles[variant], className)}
      disabled={disabled}
      {...props}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{children}</span>
    </motion.button>
  );
};
