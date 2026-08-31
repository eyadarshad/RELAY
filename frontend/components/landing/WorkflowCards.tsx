"use client";

import React from "react";
import { motion } from "motion/react";
import { ShoppingCart, Truck, FileSpreadsheet, CalendarCheck2, ArrowUpRight } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { clsx } from "clsx";

interface WorkflowCardsProps {
  onSelectPreset: (prompt: string, type: "PROCURE" | "RESCUE" | "QUOTE" | "SCHEDULE") => void;
}

export const WorkflowCards: React.FC<WorkflowCardsProps> = ({ onSelectPreset }) => {
  const workflows = [
    {
      id: "PROCURE",
      title: "01 // PROCURE",
      subtitle: "Autonomous Sourcing & Multi-Call Price Negotiation",
      icon: <ShoppingCart className="w-5 h-5 text-accent" />,
      description: "Finds vendors, compares stock availability, and autonomously calls back top candidates to negotiate volume discounts.",
      badge: <Badge variant="accent">PRIMARY HACKATHON DEMO</Badge>,
      preset: "We need 500 ergonomic office chairs delivered to our Lahore office before Friday. Keep the total cost below $15,000.",
      tag: "500 Chairs • $15,000 Budget",
      borderColor: "hover:border-accent",
    },
    {
      id: "RESCUE",
      title: "02 // RESCUE",
      subtitle: "Emergency Logistics & Rapid Failure Recovery",
      icon: <Truck className="w-5 h-5 text-signal-amber" />,
      description: "Emergency carrier broke down? RELAY dials multiple local logistics dispatchers sequentially until a replacement truck is secured.",
      badge: <Badge variant="amber">URGENT OPS</Badge>,
      preset: "Our delivery truck cancelled. Find a replacement that can arrive within two hours under $800.",
      tag: "2h ETA • Immediate Dispatch",
      borderColor: "hover:border-signal-amber",
    },
    {
      id: "QUOTE",
      title: "03 // QUOTE",
      subtitle: "Comparative Commercial Bidding Engine",
      icon: <FileSpreadsheet className="w-5 h-5 text-signal-cyan" />,
      description: "Collects quotes for complex machinery, normalizes warranty and power specifications, and recommends the best bid.",
      badge: <Badge variant="cyan">COMPETITIVE BID</Badge>,
      preset: "I need a commercial 50kVA diesel generator. Collect competitive quotes under $20,000 with installation.",
      tag: "3 Quotes • Normalized Matrix",
      borderColor: "hover:border-signal-cyan",
    },
    {
      id: "SCHEDULE",
      title: "04 // SCHEDULE",
      subtitle: "Automated Waitlist Slot Filling",
      icon: <CalendarCheck2 className="w-5 h-5 text-signal-green" />,
      description: "Calls priority waitlist patients or clients in sequence until an open slot is accepted and locked into the calendar.",
      badge: <Badge variant="green">CALENDAR RESCUE</Badge>,
      preset: "The 3 PM consultation appointment was cancelled. Call our priority waitlist to find someone who can take the slot.",
      tag: "Sequential Dial • Auto Lock",
      borderColor: "hover:border-signal-green",
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between font-mono text-xs text-text-secondary pb-1 border-b border-border">
        <span className="uppercase tracking-widest font-bold text-text-primary">
          [ SUPPORTED OPERATIONAL WORKFLOW TEMPLATES ]
        </span>
        <span className="text-[10px] text-text-muted">ONE AUTONOMOUS CALL-E ENGINE</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {workflows.map((w, idx) => (
          <motion.div
            key={w.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.08, duration: 0.3 }}
            whileHover={{ y: -2 }}
            onClick={() => onSelectPreset(w.preset, w.id as any)}
            className={clsx(
              "group relative p-5 bg-surface border border-border transition-all duration-200 cursor-pointer font-mono select-none",
              w.borderColor,
              "hover:bg-surface-raised"
            )}
          >
            {/* Corner Crosshairs */}
            <span className="absolute -top-1.5 -left-1.5 font-mono text-[10px] text-border-active group-hover:text-accent">
              +
            </span>
            <span className="absolute -top-1.5 -right-1.5 font-mono text-[10px] text-border-active group-hover:text-accent">
              +
            </span>

            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 bg-void border border-border group-hover:border-accent/60">
                    {w.icon}
                  </div>
                  <div>
                    <h4 className="font-display font-bold text-sm text-text-primary tracking-wide">
                      {w.title}
                    </h4>
                    <p className="text-[10px] text-text-secondary">{w.subtitle}</p>
                  </div>
                </div>
                {w.badge}
              </div>

              <p className="text-xs text-text-secondary leading-relaxed font-sans">
                {w.description}
              </p>

              <div className="pt-2 border-t border-border/60 flex items-center justify-between text-xs">
                <span className="text-[10px] text-text-muted font-mono">{w.tag}</span>
                <span className="inline-flex items-center gap-1 text-text-primary group-hover:text-accent font-bold text-[11px] uppercase tracking-wider">
                  LOAD PRESET <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
