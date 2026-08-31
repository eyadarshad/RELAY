"use client";

import React, { useState } from "react";
import { motion } from "motion/react";
import { ArrowRight, Sparkles, Terminal, PhoneForwarded, ShieldCheck, Zap } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

interface HeroSectionProps {
  objective: string;
  setObjective: (val: string) => void;
  onStartMission: () => void;
  isLoading: boolean;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  objective,
  setObjective,
  onStartMission,
  isLoading,
}) => {
  return (
    <div className="space-y-6 sm:space-y-8 font-mono">
      {/* Top Telemetry Line */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-[11px] text-text-secondary pb-3 border-b border-border">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <span className="text-text-primary font-bold tracking-widest uppercase">
            CALL-E HACKATHON 2026 // AUTONOMOUS MISSION RUNTIME
          </span>
        </div>
        <div className="flex items-center gap-3 text-[10px] text-text-muted">
          <span>LATENCY: 18ms</span>
          <span>•</span>
          <span>TELEPHONY: CALL-E v1.0 SDK</span>
          <span>•</span>
          <span>HUMAN-IN-THE-LOOP: ACTIVE</span>
        </div>
      </div>

      {/* Hero Headline & Tagline */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-surface-raised border border-border text-[11px] text-accent">
          <Zap className="w-3.5 h-3.5" />
          <span className="font-bold uppercase tracking-wider">THE PHONE IS NOT THE PRODUCT. AUTONOMOUS REAL-WORLD EXECUTION IS.</span>
        </div>

        <h1 className="font-display font-black text-4xl sm:text-6xl md:text-7xl text-text-primary tracking-tight uppercase">
          RELAY<span className="text-accent">_</span>
        </h1>

        <p className="font-sans text-lg sm:text-xl md:text-2xl text-text-secondary max-w-3xl font-light">
          Give AI a high-level business objective. It plans, discovers suppliers, makes phone calls via CALL-E, compares quotes, negotiates price, and secures the deal.
        </p>
      </div>

      {/* Interactive Objective Input Terminal */}
      <div className="border-2 border-border focus-within:border-accent bg-surface p-4 sm:p-5 space-y-4 transition-colors acid-glow-sm">
        <div className="flex items-center justify-between text-xs text-text-muted pb-2 border-b border-border/80">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-accent" />
            <span className="font-bold text-text-primary uppercase tracking-wider">
              MISSION_OBJECTIVE_INPUT
            </span>
          </div>
          <span className="text-[10px] uppercase tracking-widest text-accent">
            NATURAL LANGUAGE PROMPT
          </span>
        </div>

        <div className="relative">
          <textarea
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            rows={3}
            placeholder="e.g. We need 500 ergonomic office chairs delivered to our Lahore office before Friday. Keep total cost below $15,000."
            className="w-full bg-void border border-border p-3.5 text-text-primary font-mono text-sm sm:text-base placeholder:text-text-muted focus:outline-none focus:border-accent/80 resize-none"
          />
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-2 text-[11px] text-text-secondary">
            <ShieldCheck className="w-4 h-4 text-signal-green" />
            <span>Multi-call autonomous loop with human authorization gate</span>
          </div>

          <Button
            variant="primary"
            size="lg"
            disabled={!objective.trim() || isLoading}
            onClick={onStartMission}
            icon={<ArrowRight className="w-4 h-4" />}
            className="sm:w-auto"
          >
            {isLoading ? "INITIALIZING MISSION..." : "LAUNCH MISSION ▸"}
          </Button>
        </div>
      </div>
    </div>
  );
};
