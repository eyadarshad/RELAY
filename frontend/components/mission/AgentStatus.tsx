"use client";

import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  Compass, 
  Search, 
  PhoneCall, 
  BrainCircuit, 
  TrendingDown, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle,
  Clock
} from "lucide-react";
import { clsx } from "clsx";

interface AgentStatusProps {
  status: string;
  className?: string;
}

export const AgentStatus: React.FC<AgentStatusProps> = ({ status, className }) => {
  const getStatusConfig = (s: string) => {
    switch (s) {
      case "PLANNING":
        return {
          label: "PLANNING MISSION",
          icon: <Compass className="w-4 h-4 text-accent animate-spin" />,
          bgColor: "bg-accent/10 border-accent/40 text-accent",
          dotColor: "bg-accent",
          description: "Parsing constraints & formulating strategy",
        };
      case "DISCOVERING":
        return {
          label: "SEARCHING SUPPLIERS",
          icon: <Search className="w-4 h-4 text-signal-cyan animate-pulse" />,
          bgColor: "bg-signal-cyan/10 border-signal-cyan/40 text-signal-cyan",
          dotColor: "bg-signal-cyan",
          description: "Matching verified suppliers in directory",
        };
      case "CALLING":
        return {
          label: "MAKING CALLS (CALL-E)",
          icon: <PhoneCall className="w-4 h-4 text-signal-cyan animate-bounce" />,
          bgColor: "bg-signal-cyan/15 border-signal-cyan text-signal-cyan cyan-glow",
          dotColor: "bg-signal-cyan",
          description: "Conducting natural phone inquiries via CALL-E",
        };
      case "ANALYZING":
        return {
          label: "ANALYZING OFFERS",
          icon: <BrainCircuit className="w-4 h-4 text-signal-amber animate-pulse" />,
          bgColor: "bg-signal-amber/10 border-signal-amber/40 text-signal-amber",
          dotColor: "bg-signal-amber",
          description: "Multi-attribute scoring & ranking candidates",
        };
      case "NEGOTIATING":
        return {
          label: "NEGOTIATING PRICE",
          icon: <TrendingDown className="w-4 h-4 text-signal-amber animate-pulse" />,
          bgColor: "bg-signal-amber/15 border-signal-amber text-signal-amber amber-glow",
          dotColor: "bg-signal-amber",
          description: "Leveraging competing bids to secure discount",
        };
      case "APPROVAL_REQUIRED":
        return {
          label: "APPROVAL REQUIRED",
          icon: <ShieldAlert className="w-4 h-4 text-signal-red animate-pulse" />,
          bgColor: "bg-signal-red/15 border-signal-red text-signal-red",
          dotColor: "bg-signal-red",
          description: "Paused for human authorization (> $5,000 threshold)",
        };
      case "CONFIRMING":
        return {
          label: "CONFIRMING ORDER",
          icon: <CheckCircle2 className="w-4 h-4 text-signal-green animate-pulse" />,
          bgColor: "bg-signal-green/10 border-signal-green/40 text-signal-green",
          dotColor: "bg-signal-green",
          description: "Placing binding purchase confirmation call",
        };
      case "COMPLETED":
        return {
          label: "MISSION ACCOMPLISHED",
          icon: <CheckCircle2 className="w-4 h-4 text-signal-green" />,
          bgColor: "bg-signal-green/15 border-signal-green text-signal-green green-glow",
          dotColor: "bg-signal-green",
          description: "All requirements met. Audit report generated.",
        };
      case "ABORTED":
      case "FAILED":
        return {
          label: status,
          icon: <XCircle className="w-4 h-4 text-signal-red" />,
          bgColor: "bg-signal-red/10 border-signal-red/30 text-signal-red",
          dotColor: "bg-signal-red",
          description: "Mission halted",
        };
      default:
        return {
          label: "INITIALIZING",
          icon: <Clock className="w-4 h-4 text-text-muted" />,
          bgColor: "bg-surface-raised border-border text-text-secondary",
          dotColor: "bg-text-muted",
          description: "Preparing autonomous agent",
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <div className={clsx("flex items-center gap-3", className)}>
      <AnimatePresence mode="wait">
        <motion.div
          key={status}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 4 }}
          transition={{ duration: 0.2 }}
          className={clsx(
            "flex items-center gap-2.5 px-3 py-1.5 border font-mono font-bold text-xs uppercase tracking-wider select-none",
            config.bgColor
          )}
        >
          {config.icon}
          <span>{config.label}</span>
          <span className="relative flex h-2 w-2">
            <span
              className={clsx(
                "animate-ping absolute inline-flex h-full w-full opacity-75 rounded-full",
                config.dotColor
              )}
            />
            <span className={clsx("relative inline-flex rounded-full h-2 w-2", config.dotColor)} />
          </span>
        </motion.div>
      </AnimatePresence>

      <span className="hidden md:inline font-mono text-xs text-text-secondary truncate">
        {config.description}
      </span>
    </div>
  );
};
