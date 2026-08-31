"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { AlertTriangle, CheckCircle, Info, X } from "lucide-react";
import { clsx } from "clsx";

export interface ToastProps {
  id: string;
  type?: "error" | "success" | "info" | "warning";
  title?: string;
  message: string;
  onClose: (id: string) => void;
  duration?: number;
}

export const Toast: React.FC<ToastProps> = ({
  id,
  type = "info",
  title,
  message,
  onClose,
  duration = 5000,
}) => {
  useEffect(() => {
    if (duration <= 0) return;
    const timer = setTimeout(() => onClose(id), duration);
    return () => clearTimeout(timer);
  }, [id, duration, onClose]);

  const typeConfig = {
    error: {
      border: "border-signal-red",
      text: "text-signal-red",
      icon: <AlertTriangle className="w-4 h-4 text-signal-red shrink-0" />,
      bg: "bg-void/95",
      glow: "shadow-[0_0_15px_rgba(255,51,51,0.25)]",
    },
    success: {
      border: "border-signal-green",
      text: "text-signal-green",
      icon: <CheckCircle className="w-4 h-4 text-signal-green shrink-0" />,
      bg: "bg-void/95",
      glow: "shadow-[0_0_15px_rgba(0,255,136,0.25)]",
    },
    warning: {
      border: "border-signal-amber",
      text: "text-signal-amber",
      icon: <AlertTriangle className="w-4 h-4 text-signal-amber shrink-0" />,
      bg: "bg-void/95",
      glow: "shadow-[0_0_15px_rgba(255,184,0,0.25)]",
    },
    info: {
      border: "border-accent",
      text: "text-accent",
      icon: <Info className="w-4 h-4 text-accent shrink-0" />,
      bg: "bg-void/95",
      glow: "shadow-[0_0_15px_rgba(204,255,0,0.25)]",
    },
  };

  const config = typeConfig[type];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={clsx(
        "relative p-3.5 border font-mono text-xs max-w-md w-full backdrop-blur-md",
        config.border,
        config.bg,
        config.glow
      )}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{config.icon}</div>
        <div className="flex-1 space-y-1">
          {title && (
            <div className={clsx("font-bold uppercase tracking-wider text-[11px]", config.text)}>
              {title}
            </div>
          )}
          <p className="text-text-primary text-[11px] leading-relaxed">{message}</p>
        </div>
        <button
          onClick={() => onClose(id)}
          className="text-text-muted hover:text-text-primary p-0.5 transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </motion.div>
  );
};

export interface ToastContainerProps {
  toasts: Array<{
    id: string;
    type?: "error" | "success" | "info" | "warning";
    title?: string;
    message: string;
  }>;
  onClose: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onClose }) => {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-auto">
      <AnimatePresence>
        {toasts.map((t) => (
          <Toast key={t.id} {...t} onClose={onClose} />
        ))}
      </AnimatePresence>
    </div>
  );
};
